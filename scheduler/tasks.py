import asyncio
import random
from datetime import datetime
from celery import current_app as app
from celery.schedules import crontab
from celery.signals import celeryd_init

from core.account_manager import get_manager
from core.instagram_engine import InstagramEngine
from core.threads_engine import ThreadsEngine
from core.twitter_engine import TwitterEngine
from core.human_simulator import HumanSimulator


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def routine_instagram(self, account_id: int):
    mgr = get_manager()
    account = mgr.get_account(account_id)
    if not account or not account["active"]:
        return {"status": "skipped"}
    if HumanSimulator.is_sleep_time():
        return {"status": "skipped", "reason": "sleep"}
    engine = InstagramEngine()
    result = engine.run_daily_routine(account)
    return {"account": account["username"], "platform": "instagram",
            "timestamp": datetime.now().isoformat(), "result": result}


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def routine_threads(self, account_id: int):
    mgr = get_manager()
    account = mgr.get_account(account_id)
    if not account or not account["active"]:
        return {"status": "skipped"}
    if HumanSimulator.is_sleep_time():
        return {"status": "skipped", "reason": "sleep"}
    engine = ThreadsEngine()
    result = asyncio.run(engine.run_daily_routine(account))
    return {"account": account["username"], "platform": "threads",
            "timestamp": datetime.now().isoformat(), "result": result}


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def routine_twitter(self, account_id: int):
    mgr = get_manager()
    account = mgr.get_account(account_id)
    if not account or not account["active"]:
        return {"status": "skipped"}
    if HumanSimulator.is_sleep_time():
        return {"status": "skipped", "reason": "sleep"}
    engine = TwitterEngine()
    result = asyncio.run(engine.run_daily_routine(account))
    return {"account": account["username"], "platform": "twitter",
            "timestamp": datetime.now().isoformat(), "result": result}


@app.task
def bulk_action_instagram(account_ids: list, action: str, target: str, amount: int = 5):
    mgr = get_manager()
    engine = InstagramEngine()
    results = []
    for aid in account_ids:
        acc = mgr.get_account(aid)
        if not acc or not acc["active"]:
            continue
        if action == "like":
            count = engine.like_from_hashtag(acc, target, amount)
        elif action == "comment":
            count = engine.comment_on_hashtag(acc, target, amount)
        elif action == "follow":
            count = engine.follow_followers(acc, target, amount)
        else:
            count = 0
        results.append({"account_id": aid, "username": acc["username"], "count": count})
        HumanSimulator.pause("between")
    return results


@app.task
def bulk_action_twitter(account_ids: list, action: str, target: str, amount: int = 5):
    mgr = get_manager()
    engine = TwitterEngine()
    results = []
    for aid in account_ids:
        acc = mgr.get_account(aid)
        if not acc or not acc["active"]:
            continue
        if action == "like":
            res = asyncio.run(engine.search_and_interact(acc, target, likes=amount))
        elif action == "follow":
            ok = asyncio.run(engine.follow_user(acc, target))
            res = {"follow": target, "ok": ok}
        elif action == "post":
            tid = asyncio.run(engine.post_tweet(acc, target))
            res = {"tweet_id": tid}
        else:
            res = {}
        results.append({"account_id": aid, "username": acc["username"], "result": res})
        HumanSimulator.pause("between")
    return results


@app.task
def reset_daily_limits():
    get_manager().reset_daily_limits()


# Planification automatique
@celeryd_init.connect
def setup_periodic_tasks(sender, **kwargs):
    mgr = get_manager()

    # Reset quotidien à minuit
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        reset_daily_limits.s(),
        name="reset_daily_limits"
    )

    for account in mgr.accounts:
        if not account["active"]:
            continue
        hour = HumanSimulator.random_hour(8, 22)
        minute = HumanSimulator.random_minute()

        if account["platform"] == "instagram":
            sender.add_periodic_task(
                crontab(hour=hour, minute=minute),
                routine_instagram.s(account["id"]),
                name=f"ig_{account['username']}"
            )
        elif account["platform"] == "threads":
            sender.add_periodic_task(
                crontab(hour=hour, minute=minute),
                routine_threads.s(account["id"]),
                name=f"threads_{account['username']}"
            )
        elif account["platform"] == "twitter":
            sender.add_periodic_task(
                crontab(hour=hour, minute=minute),
                routine_twitter.s(account["id"]),
                name=f"twitter_{account['username']}"
            )
