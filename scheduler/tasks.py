import asyncio
import random
from datetime import datetime
from celery import current_app as app

from core.account_manager import get_manager
from core.instagram_engine import InstagramEngine
from core.threads_engine import ThreadsEngine
from core.twitter_engine import TwitterEngine
from core.human_simulator import HumanSimulator
from core.database import SessionLocal
from core.models import Campaign, ActionLog

def log_action(db, account_id, campaign_id, action_type, target_user, source=None):
    """Enregistre une action en base de données pour les analytics."""
    log = ActionLog(
        account_id=str(account_id),
        campaign_id=campaign_id,
        action_type=action_type,
        target_user=target_user,
        source=source
    )
    db.add(log)
    db.commit()

@app.task(bind=True)
def routine_instagram(self, account_id: int):
    mgr = get_manager()
    account = mgr.get_account(account_id)
    if not account or not account.get("active"): return {"status": "skipped"}
    if HumanSimulator.is_sleep_time(): return {"status": "skipped", "reason": "sleep"}
    
    engine = InstagramEngine()
    result = engine.run_daily_routine(account)
    return {"account": account["username"], "result": result}

@app.task(bind=True)
def routine_threads(self, account_id: int):
    mgr = get_manager()
    account = mgr.get_account(account_id)
    if not account or not account.get("active"): return {"status": "skipped"}
    engine = ThreadsEngine()
    result = asyncio.run(engine.run_daily_routine(account))
    return {"account": account["username"], "result": result}

@app.task(bind=True)
def routine_twitter(self, account_id: int):
    mgr = get_manager()
    account = mgr.get_account(account_id)
    if not account or not account.get("active"): return {"status": "skipped"}
    engine = TwitterEngine()
    result = asyncio.run(engine.run_daily_routine(account))
    return {"account": account["username"], "result": result}

@app.task
def bulk_action_instagram(account_ids: list, action: str, target: str, amount: int = 5):
    mgr = get_manager(); engine = InstagramEngine(); results = []
    db = SessionLocal()
    for aid in account_ids:
        acc = mgr.get_account(aid)
        if not acc: continue
        count = 0
        if action == "like": count = engine.like_from_hashtag(acc, target, amount)
        elif action == "comment": count = engine.comment_on_hashtag(acc, target, amount)
        elif action == "follow": count = engine.follow_followers(acc, target, amount)
        
        # Logging simple
        for _ in range(count):
            log_action(db, aid, None, action, target)
            
        results.append({"account_id": aid, "username": acc["username"], "count": count})
        HumanSimulator.pause("between")
    db.close()
    return results

@app.task
def bulk_action_twitter(account_ids: list, action: str, target: str, amount: int = 5):
    mgr = get_manager(); engine = TwitterEngine(); results = []
    for aid in account_ids:
        acc = mgr.get_account(aid)
        if not acc: continue
        if action == "like": res = asyncio.run(engine.search_and_interact(acc, target, likes=amount))
        elif action == "follow": ok = asyncio.run(engine.follow_user(acc, target)); res = {"ok": ok}
        elif action == "post": tid = asyncio.run(engine.post_tweet(acc, target)); res = {"tweet_id": tid}
        results.append({"account_id": aid, "username": acc["username"], "result": res})
        HumanSimulator.pause("between")
    return results

@app.task
def reset_daily_limits():
    get_manager().reset_daily_limits()

@app.task
def dispatch_daily_routines():
    """ Master Task: dispatch daily routines randomly during active daytime hours. """
    if HumanSimulator.is_sleep_time():
        return {"status": "skipped", "reason": "System is in sleep mode (nighttime)."}

    mgr = get_manager()
    active_accounts = [a for a in mgr.accounts if a.get("active") and a.get("status") == "active"]
    dispatched = 0

    for account in active_accounts:
        # 30% chance to trigger the routine on this 15-minute tick if active (spreads the load naturally)
        if random.random() < 0.3:
            platform = account.get("platform", "instagram")
            account_id = account.get("id")
            if platform == "instagram":
                routine_instagram.delay(account_id)
                dispatched += 1
            elif platform == "twitter":
                routine_twitter.delay(account_id)
                dispatched += 1

    return {"status": "success", "dispatched_routines": dispatched}

@app.task(bind=True)
def execute_smart_campaign(self, campaign_id: str):
    """Exécute une campagne premium avec logging analytique en DB."""
    db = SessionLocal()
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign or campaign.status != "running":
        db.close(); return {"status": "skipped"}
        
    mgr = get_manager()
    account = next((a for a in mgr.accounts if str(a["id"]) == str(campaign.account_id)), None)
    if not account:
        db.close(); return {"status": "error", "reason": "Account not found"}
        
    engine = InstagramEngine()
    features = campaign.features or {}
    targets = campaign.targets or {}
    competitors = targets.get("competitors", [])
    allowed_langs = (campaign.ai_settings or {}).get("lang_filter", [])
    
    results = {"actions": 0}
    try:
        for competitor in competitors:
            comp_clean = competitor.replace('@', '')
            
            # 1. Stories
            if features.get("story_interactions"):
                res = engine.mass_look_and_interact_stories(account, comp_clean)
                for _ in range(res.get("viewed", 0)): 
                    log_action(db, account["id"], campaign_id, "story_view", comp_clean, source=comp_clean)
                for _ in range(res.get("polls_voted", 0)):
                    log_action(db, account["id"], campaign_id, "story_poll_vote", comp_clean, source=comp_clean)
                results["actions"] += res.get("viewed", 0)
                HumanSimulator.pause("between")
                
            # 2. Smart Follow
            if features.get("smart_follow"):
                res = engine.smart_follow_loop(account, comp_clean, allowed_langs)
                for _ in range(res.get("followed", 0)):
                    log_action(db, account["id"], campaign_id, "follow", comp_clean, source=comp_clean)
                results["actions"] += res.get("followed", 0)
                HumanSimulator.pause("between")
                
        campaign.status = "completed"
        db.commit()
    except Exception as e:
        campaign.status = f"error: {str(e)}"
        db.commit()
    finally:
        db.close()
        
    return results
