from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict
import asyncio
import tempfile, os
import uuid

from core.account_manager import get_manager
from core.instagram_engine import InstagramEngine
from core.threads_engine import ThreadsEngine
from core.twitter_engine import TwitterEngine
from core.database import get_db
from core.models import Campaign, ActionLog, Account
from core.pdf_generator import generate_campaign_report
from scheduler.tasks import (
    routine_instagram, routine_threads, routine_twitter,
    bulk_action_instagram, bulk_action_twitter, execute_smart_campaign
)

router = APIRouter(prefix="/api/v1")


# --- Modèles Pydantic ---

class AccountCreate(BaseModel):
    username: str
    password: str
    platform: str = "instagram"
    proxy: Optional[str] = None
    tags: Optional[List[str]] = None
    two_factor_seed: Optional[str] = None  # Clé TOTP secrète (format base32)

class CampaignCreate(BaseModel):
    account_id: str
    name: str
    type: str
    targets: dict
    features: dict
    ai_settings: dict
    activity_settings: dict

class BulkAction(BaseModel):
    account_ids: List[int]
    action: str
    target: str
    amount: int = 5

class PostCreate(BaseModel):
    account_id: int
    text: str
    platform: str = "instagram"


# --- Endpoints ---

@router.get("/stats")
def get_stats():
    return get_manager().get_stats()


@router.get("/accounts")
def list_accounts(platform: Optional[str] = None, status: Optional[str] = None):
    mgr = get_manager()
    accs = mgr.accounts
    if platform:
        accs = [a for a in accs if a["platform"] == platform]
    if status:
        accs = [a for a in accs if a["status"] == status]
    safe = [{k: v for k, v in a.items() if k != "password"} for a in accs]
    return {"accounts": safe, "total": len(safe)}


@router.post("/accounts")
def add_account(acct: AccountCreate):
    mgr = get_manager()
    if mgr.get_by_username(acct.username):
        raise HTTPException(400, "Ce username existe déjà")
    new = mgr.add_account(
        acct.username, acct.password, acct.platform, 
        acct.proxy, acct.tags, acct.two_factor_seed
    )
    return {k: v for k, v in new.items() if k != "password"}


@router.delete("/accounts/{account_id}")
def delete_account(account_id: int):
    get_manager().remove_account(account_id)
    return {"status": "deleted"}


@router.post("/accounts/import")
def import_accounts(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "Format CSV requis")
    tmp = f"/tmp/{file.filename}"
    with open(tmp, 'wb') as f:
        f.write(file.file.read())
    count = get_manager().import_csv(tmp)
    os.unlink(tmp)
    return {"status": "imported", "count": count}


@router.post("/accounts/{account_id}/run")
def run_routine(account_id: int, bg: BackgroundTasks):
    mgr = get_manager()
    acc = mgr.get_account(account_id)
    if not acc:
        raise HTTPException(404, "Compte inconnu")
    if acc["platform"] == "instagram":
        bg.add_task(routine_instagram, account_id)
    elif acc["platform"] == "threads":
        bg.add_task(routine_threads, account_id)
    elif acc["platform"] == "twitter":
        bg.add_task(routine_twitter, account_id)
    return {"status": "queued", "account": acc["username"]}


@router.post("/actions/bulk")
def bulk_action(req: BulkAction, bg: BackgroundTasks):
    mgr = get_manager()
    for aid in req.account_ids:
        if not mgr.get_account(aid):
            raise HTTPException(404, f"Compte #{aid} inconnu")
    if req.action in ("like", "comment", "follow"):
        bg.add_task(bulk_action_instagram, req.account_ids, req.action, req.target, req.amount)
    elif req.action in ("twitter_like", "twitter_follow", "twitter_post"):
        bg.add_task(bulk_action_twitter, req.account_ids, req.action.split("_")[1], req.target, req.amount)
    return {"status": "queued", "accounts": len(req.account_ids), "action": req.action}


@router.post("/posts")
async def create_post(req: PostCreate):
    mgr = get_manager()
    acc = mgr.get_account(req.account_id)
    if not acc:
        raise HTTPException(404, "Compte inconnu")

    if req.platform == "instagram":
        engine = InstagramEngine()
        # Sans image pour la simplicité de l'API
        result = engine.post_photo(acc, "placeholder.jpg", req.text)
        return {"status": "posted" if result else "error", "id": result}
    elif req.platform == "threads":
        engine = ThreadsEngine()
        result = await engine.create_post(acc, req.text)
        return {"status": "posted" if result else "error", "id": result}
    elif req.platform == "twitter":
        engine = TwitterEngine()
        result = await engine.post_tweet(acc, req.text)
        return {"status": "posted" if result else "error", "id": result}
    raise HTTPException(400, "Plateforme inconnue")


# --- Endpoints Campagnes (Premium) ---

@router.post("/campaigns")
def create_campaign(camp: CampaignCreate, bg: BackgroundTasks, db: Session = Depends(get_db)):
    camp_id = str(uuid.uuid4())
    db_campaign = Campaign(
        id=camp_id,
        account_id=camp.account_id,
        name=camp.name,
        type=camp.type,
        targets=camp.targets,
        features=camp.features,
        ai_settings=camp.ai_settings,
        activity_settings=camp.activity_settings,
        status="running"
    )
    db.add(db_campaign)
    db.commit()
    
    # Lancer la campagne en arrière-plan via Celery
    bg.add_task(execute_smart_campaign, camp_id)
    
    return {"status": "success", "campaign_id": camp_id}

@router.get("/campaigns")
def list_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).all()
    return {"campaigns": campaigns}

@router.get("/reports/{campaign_id}/download")
def download_pdf_report(campaign_id: str, agency_name: str = "BoostPanel Agency", db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(404, "Campagne inconnue")
        
    # TODO: Calculate real stats from ActionLogs
    # For now, generate dummy stats matching the campaign features
    stats = {
        "new_followers": 142,
        "stories_viewed": 530 if campaign.features.get("story_interactions") else 0,
        "polls_voted": 85 if campaign.features.get("story_interactions") else 0,
        "ai_comments": 45 if campaign.features.get("auto_comment") else 0,
        "comment_likes": 120 if campaign.features.get("auto_like") else 0,
        "top_sources": [
            {"username": target.replace('@', ''), "conversions": 34} 
            for target in campaign.targets.get("competitors", [])[:3]
        ]
    }
    
    filepath = generate_campaign_report(campaign.name, stats, agency_name)
    
    return FileResponse(
        path=filepath,
        filename=os.path.basename(filepath),
        media_type="application/pdf"
    )
