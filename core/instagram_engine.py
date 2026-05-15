"""
Moteur Instagram via Instagrapi.
"""
import random
from typing import Optional, List
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, FeedbackRequired
from .account_manager import get_manager
from .human_simulator import HumanSimulator


class InstagramEngine:
    def __init__(self):
        self.clients = {}

    def get_client(self, account: dict) -> Optional[Client]:
        aid = account["id"]
        if aid in self.clients:
            return self.clients[aid]

        cl = Client()
        cl.delay_range = [1, 3]
        cl.set_user_agent(
            "Instagram 289.0.0.77.109 Android (33/13; 420dpi; 1080x2400; "
            "OnePlus; ONEPLUS+A6003; OnePlus6; qcom; fr_FR; 482756178)"
        )
        if account.get("proxy"):
            cl.set_proxy(account["proxy"])

        session_path = f"accounts/session_ig_{account['username']}.json"
        try:
            cl.load_settings(session_path)
        except:
            pass

        try:
            cl.login(account["username"], account["password"])
            cl.dump_settings(session_path)
            mgr = get_manager()
            mgr.set_status(aid, "active")
            self.clients[aid] = cl
            return cl
        except ChallengeRequired:
            get_manager().set_status(aid, "challenge", "Challenge requis")
            return None
        except FeedbackRequired:
            get_manager().set_status(aid, "banned", "Temp ban")
            return None
        except Exception as e:
            print(f"⚠️  IG login {account['username']}: {e}")
            return None

    def like_from_hashtag(self, account: dict, hashtag: str, amount: int = 5) -> int:
        cl = self.get_client(account)
        if not cl:
            return 0
        count = 0
        try:
            medias = cl.hashtag_medias_recent(hashtag, amount=amount + 5)
            for m in medias[:amount]:
                if HumanSimulator.should_act(0.75):
                    cl.media_like(m.id)
                    get_manager().increment(account["id"], "like")
                    count += 1
                HumanSimulator.pause("like")
        except Exception as e:
            print(f"⚠️  IG like hashtag: {e}")
        return count

    def comment_on_hashtag(self, account: dict, hashtag: str, amount: int = 3) -> int:
        cl = self.get_client(account)
        if not cl:
            return 0
        count = 0
        try:
            medias = cl.hashtag_medias_recent(hashtag, amount=amount + 5)
            for m in medias[:amount]:
                if HumanSimulator.should_act(0.3):
                    cl.media_comment(m.id, HumanSimulator.random_comment())
                    get_manager().increment(account["id"], "comment")
                    count += 1
                HumanSimulator.pause("comment")
        except Exception as e:
            print(f"⚠️  IG comment: {e}")
        return count

    def follow_followers(self, account: dict, target: str, amount: int = 5) -> int:
        cl = self.get_client(account)
        if not cl:
            return 0
        count = 0
        try:
            tid = cl.user_id_from_username(target)
            followers = cl.user_followers(tid, amount=amount + 10)
            for uid, info in followers.items():
                if count >= amount:
                    break
                if HumanSimulator.should_act(0.4):
                    cl.user_follow(uid)
                    get_manager().increment(account["id"], "follow")
                    count += 1
                HumanSimulator.pause("follow")
        except Exception as e:
            print(f"⚠️  IG follow: {e}")
        return count

    def post_photo(self, account: dict, image_path: str, caption: str) -> Optional[str]:
        cl = self.get_client(account)
        if not cl:
            return None
        try:
            media = cl.photo_upload(image_path, caption)
            get_manager().increment(account["id"], "post")
            return str(media.id)
        except Exception as e:
            print(f"⚠️  IG post: {e}")
            return None

    def run_daily_routine(self, account: dict) -> dict:
        cl = self.get_client(account)
        if not cl:
            return {"status": "error", "reason": "login"}

        results = {"likes": 0, "comments": 0, "follows": 0}

        # Feed scroll
        try:
            cl.get_timeline_feed()
            HumanSimulator.pause("scroll")
        except:
            pass

        # Like depuis hashtags
        tags = ["nature", "photography", "travel", "art", "food", "fashion", "music"]
        selected = random.sample(tags, random.randint(2, 4))
        for tag in selected:
            results["likes"] += self.like_from_hashtag(account, tag, random.randint(5, 15))
            HumanSimulator.pause("between")

        # Commentaires
        if selected:
            results["comments"] += self.comment_on_hashtag(account, random.choice(selected), random.randint(2, 5))
            HumanSimulator.pause("between")

        # Follow
        targets = ["natgeo", "bbcnews", "lonelyplanet", "nytimes", "nasa"]
        results["follows"] += self.follow_followers(account, random.choice(targets), random.randint(1, 4))

        return {"status": "success", **results}
