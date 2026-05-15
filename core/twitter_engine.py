"""
Moteur Twitter/X via Twikit (sans clé API).
"""
import asyncio
import random
from typing import Optional, List
from twikit import Client
from twikit.errors import TooManyRequests
from .account_manager import get_manager
from .human_simulator import HumanSimulator


class TwitterEngine:
    def __init__(self):
        self.clients = {}

    async def get_client(self, account: dict) -> Optional[Client]:
        aid = account["id"]
        if aid in self.clients:
            return self.clients[aid]
        try:
            client = Client('fr-FR')
            await client.login(
                auth_info_1=account["username"],
                auth_info_2=account["username"],
                password=account["password"]
            )
            client.save_cookies(f"accounts/twitter_cookies_{account['username']}.json")
            get_manager().set_status(aid, "active")
            self.clients[aid] = client
            return client
        except Exception as e:
            print(f"⚠️  Twitter login {account['username']}: {e}")
            get_manager().set_status(aid, "challenge", str(e))
            return None

    async def post_tweet(self, account: dict, text: str) -> Optional[str]:
        client = await self.get_client(account)
        if not client:
            return None
        try:
            tweet = await client.create_tweet(text=text)
            get_manager().increment(account["id"], "post")
            return tweet.id
        except TooManyRequests:
            print(f"⏳ Rate limit Twitter {account['username']}")
            await asyncio.sleep(900)
            return None
        except Exception as e:
            print(f"⚠️  Tweet: {e}")
            return None

    async def like_tweet(self, account: dict, tweet_id: str) -> bool:
        client = await self.get_client(account)
        if not client:
            return False
        try:
            await client.favorite_tweet(tweet_id)
            get_manager().increment(account["id"], "like")
            HumanSimulator.pause("like")
            return True
        except:
            return False

    async def retweet(self, account: dict, tweet_id: str) -> bool:
        client = await self.get_client(account)
        if not client:
            return False
        try:
            await client.retweet(tweet_id)
            get_manager().increment(account["id"], "retweet")
            HumanSimulator.pause("like")
            return True
        except:
            return False

    async def follow_user(self, account: dict, username: str) -> bool:
        client = await self.get_client(account)
        if not client:
            return False
        try:
            user = await client.get_user_by_screen_name(username)
            await client.follow_user(user.id)
            get_manager().increment(account["id"], "follow")
            HumanSimulator.pause("follow")
            return True
        except Exception as e:
            print(f"⚠️  Follow: {e}")
            return False

    async def search_and_interact(self, account: dict, query: str,
                                  likes: int = 5, retweets: int = 2) -> dict:
        client = await self.get_client(account)
        if not client:
            return {"status": "error"}
        results = {"likes": 0, "retweets": 0}
        try:
            tweets = await client.search_tweet(query, 'Latest', count=50)
            for t in tweets[:likes + retweets]:
                if results["likes"] < likes and HumanSimulator.should_act(0.7):
                    await client.favorite_tweet(t.id)
                    get_manager().increment(account["id"], "like")
                    results["likes"] += 1
                    HumanSimulator.pause("like")
                if results["retweets"] < retweets and HumanSimulator.should_act(0.2):
                    await client.retweet(t.id)
                    get_manager().increment(account["id"], "retweet")
                    results["retweets"] += 1
                    HumanSimulator.pause("like")
        except Exception as e:
            print(f"⚠️  Search: {e}")
        return {**results, "status": "success"}

    async def get_trends(self, account: dict) -> List[str]:
        client = await self.get_client(account)
        if not client:
            return []
        try:
            trends = await client.get_trends()
            return [t.name for t in trends[:10]]
        except:
            return []

    async def run_daily_routine(self, account: dict) -> dict:
        client = await self.get_client(account)
        if not client:
            return {"status": "error", "reason": "login"}

        results = {"tweets": 0, "likes": 0, "retweets": 0, "follows": 0}

        # Interagir avec les tendances
        trends = await self.get_trends(account)
        for trend in trends[:3]:
            interact = await self.search_and_interact(account, trend,
                likes=random.randint(3, 8), retweets=random.randint(0, 2))
            results["likes"] += interact.get("likes", 0)
            results["retweets"] += interact.get("retweets", 0)
            await asyncio.sleep(5)

        # Poster
        if HumanSimulator.should_act(0.7):
            tweet_id = await self.post_tweet(account, HumanSimulator.random_tweet())
            if tweet_id:
                results["tweets"] += 1

        # Follow suggestions
        suggestions = ["elonmusk", "python_tip", "techcrunch", "verge", "github"]
        for name in random.sample(suggestions, random.randint(1, 3)):
            if HumanSimulator.should_act(0.3):
                await self.follow_user(account, name)
                results["follows"] += 1
                await asyncio.sleep(3)

        return {"status": "success", **results}
