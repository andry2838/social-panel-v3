"""
Moteur Threads désactivé (threads-api non-officielle et instable désactivée).
Toutes les actions renvoient un statut désactivé propre pour éviter les plantages de l'application.
"""
import asyncio
from typing import Optional


class ThreadsEngine:
    def __init__(self):
        pass

    async def get_client(self, account: dict) -> Optional[any]:
        print(f"⚠️ Moteur Threads désactivé pour {account.get('username')}.")
        return None

    async def create_post(self, account: dict, text: str,
                          image_path: Optional[str] = None) -> Optional[str]:
        print("⚠️ Le moteur Threads est désactivé.")
        return None

    async def like_timeline(self, account: dict, amount: int = 10) -> int:
        print("⚠️ Le moteur Threads est désactivé.")
        return 0

    async def run_daily_routine(self, account: dict) -> dict:
        print("⚠️ Le moteur Threads est désactivé.")
        return {"status": "disabled", "reason": "Le moteur Threads est désactivé (threads-api supprimée)."}
