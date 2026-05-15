"""
Moteur Threads via threads-api (s'appuie sur Instagrapi pour l'auth).
"""
import asyncio
import random
from typing import Optional
from threads_api.src.threads_api import ThreadsAPI
from .account_manager import get_manager
from .human_simulator import HumanSimulator


class ThreadsEngine:
    def __init__(self):
        self.clients = {}

    async def get_client(self, account: dict) -> Optional[ThreadsAPI]:
        aid = account["id"]
        if aid in self.clients:
            return self.clients[aid]
        try:
            api = ThreadsAPI()
            await api.login(
                account["username"],
                account["password"],
                cached_token_path=f"accounts/threads_token_{account['username']}.json"
            )
            get_manager().set_status(aid, "active")
            self.clients[aid] = api
            return api
        except Exception as e:
            print(f"⚠️  Threads login {account['username']}: {e}")
            get_manager().set_status(aid, "challenge", str(e))
            return None

    async def create_post(self, account: dict, text: str,
                          image_path: Optional[str] = None) -> Optional[str]:
        api = await self.get_client(account)
        if not api:
            return None
        try:
            if image_path:
                result = await api.post(caption=text, image_path=image_path)
            else:
                result = await api.post(caption=text)
            if result:
                get_manager().increment(account["id"], "post")
                return str(result)
        except Exception as e:
            print(f"⚠️  Threads post: {e}")
        return None

    async def like_timeline(self, account: dict, amount: int = 10) -> int:
        api = await self.get_client(account)
        if not api:
            return 0
        count = 0
        try:
            timeline = await api.get_timeline()
            for post in timeline[:amount]:
                if HumanSimulator.should_act(0.6):
                    await api.like(post.get("id"))
                    get_manager().increment(account["id"], "like")
                    count += 1
                HumanSimulator.pause("like")
        except Exception as e:
            print(f"⚠️  Threads like: {e}")
        return count

    async def run_daily_routine(self, account: dict) -> dict:
        api = await self.get_client(account)
        if not api:
            return {"status": "error", "reason": "login"}

        results = {"likes": 0, "posts": 0}

        # Liker le timeline
        results["likes"] += await self.like_timeline(account, 15)
        HumanSimulator.pause("between")

        # Poster
        texts = [
            "Magnifique journée ! ☀️",
            "Nouvelle découverte incroyable ✨",
            "Quel coucher de soleil ! 🌅",
            "Trop hâte de partager ça 🔥",
        ]
        if HumanSimulator.should_act(0.7):
            post_id = await self.create_post(account, random.choice(texts))
            if post_id:
                results["posts"] += 1

        return {"status": "success", **results}
