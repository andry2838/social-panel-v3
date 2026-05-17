from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict
import tempfile
import os
import json
import uuid
from pathlib import Path

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

_DATA_DIR = Path("accounts")
SCHEDULED_POSTS_FILE = _DATA_DIR / "scheduled_posts.json"
DM_RULES_FILE = _DATA_DIR / "dm_rules.json"

def _load_json(path: Path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return default

def _save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

# --- Modèles Pydantic ---
class AccountCreate(BaseModel):
    username: str
    password: str
    platform: str = "instagram"
    proxy: Optional[str] = None
    tags: Optional[List[str]] = None
    two_factor_seed: Optional[str] = None
    email: Optional[str] = None

class CampaignCreate(BaseModel):
    account_id: str
    name: str
    type: str
    targets: dict
    features: dict
    ai_settings: dict
    activity_settings: dict

# Schémas de sérialisation pour les campagnes (GET /campaigns)
class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    account_id: str
    name: str
    type: str
    targets: dict
    features: dict
    ai_settings: dict
    activity_settings: dict
    status: str

class CampaignListResponse(BaseModel):
    campaigns: List[CampaignResponse]

class BulkAction(BaseModel):
    account_ids: List[int]
    action: str
    target: str
    amount: int = 5

class ScheduledPostCreate(BaseModel):
    account: str
    caption: str
    date: str
    time: str
    platform: str = "instagram"

class DMRulesUpdate(BaseModel):
    welcome_message: str
    rules: List[dict]

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
    return {"accounts": [{k: v for k, v in a.items() if k not in ("password", "two_factor_seed")} for a in accs], "total": len(accs)}

@router.post("/accounts")
def add_account(acct: AccountCreate):
    mgr = get_manager()
    if mgr.get_by_username(acct.username):
        raise HTTPException(400, "Ce username existe déjà")
    
    new = mgr.add_account(
        username=acct.username,
        password=acct.password,
        platform=acct.platform,
        proxy=acct.proxy,
        tags=acct.tags,
        two_factor_seed=acct.two_factor_seed,
        email=acct.email
    )
    return {k: v for k, v in new.items() if k not in ("password", "two_factor_seed")}

@router.delete("/accounts/{account_id}")
def delete_account(account_id: int):
    get_manager().remove_account(account_id)
    return {"status": "deleted"}

@router.post("/accounts/import")
def import_accounts(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "Format CSV requis")
    
    # Utilisation de tempfile.mkstemp() sécurisé et multi-plateforme
    fd, tmp_path = tempfile.mkstemp(suffix=".csv")
    try:
        with os.fdopen(fd, 'wb') as tmp_file:
            tmp_file.write(file.file.read())
        count = get_manager().import_csv(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
            
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

@router.post("/campaigns")
def create_campaign(camp: CampaignCreate, bg: BackgroundTasks, db: Session = Depends(get_db)):
    camp_id = str(uuid.uuid4())
    db_campaign = Campaign(
        id=camp_id,
        account_id=str(camp.account_id),
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
    bg.add_task(execute_smart_campaign, camp_id)
    return {"status": "success", "campaign_id": camp_id}

@router.get("/campaigns", response_model=CampaignListResponse)
def list_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).all()
    # Pydantic s'occupe de la sérialisation propre via from_attributes
    return {"campaigns": campaigns}

@router.get("/reports/{campaign_id}/download")
def download_pdf_report(campaign_id: str, agency_name: str = "BoostPanel Agency", db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(404, "Campagne inconnue")
    
    # Calculer les stats réelles depuis ActionLog
    logs = db.query(ActionLog).filter(ActionLog.campaign_id == campaign_id).all()
    
    stats = {
        "new_followers": len([l for l in logs if l.action_type == "follow"]),
        "stories_viewed": len([l for l in logs if "story" in l.action_type]),
        "polls_voted": len([l for l in logs if "poll" in l.action_type]),
        "ai_comments": len([l for l in logs if l.action_type == "comment"]),
        "comment_likes": len([l for l in logs if l.action_type == "like"]),
        "top_sources": []
    }
    
    # Top sources tracking
    sources_count = db.query(ActionLog.source, func.count(ActionLog.id)).filter(ActionLog.campaign_id == campaign_id).group_by(ActionLog.source).all()
    stats["top_sources"] = [{"username": s[0], "conversions": s[1]} for s in sources_count if s[0]]

    filepath = generate_campaign_report(campaign.name, stats, agency_name)
    return FileResponse(path=filepath, filename=os.path.basename(filepath), media_type="application/pdf")

# Endpoints posts/schedule et dm-rules
@router.post("/posts/schedule")
def schedule_post(post: ScheduledPostCreate):
    posts = _load_json(SCHEDULED_POSTS_FILE, [])
    new_post = {
        "id": str(uuid.uuid4()),
        "account": post.account,
        "caption": post.caption,
        "scheduled": f"{post.date} {post.time}",
        "platform": post.platform,
        "status": "scheduled"
    }
    posts.append(new_post)
    _save_json(SCHEDULED_POSTS_FILE, posts)
    return new_post

@router.get("/posts/scheduled")
def get_scheduled_posts():
    return {"posts": _load_json(SCHEDULED_POSTS_FILE, [])}

@router.post("/settings/dm-rules")
def save_dm_rules(rules: DMRulesUpdate):
    _save_json(DM_RULES_FILE, rules.dict())
    return {"status": "saved"}

@router.get("/settings/dm-rules")
def get_dm_rules():
    return _load_json(DM_RULES_FILE, {"welcome_message": "...", "rules": []})
