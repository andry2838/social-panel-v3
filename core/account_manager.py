"""
Gestionnaire de pool de comptes multi-plateforme.
- Chiffrement AES des mots de passe
- Gestion 100+ comptes
- Import CSV
- Stats globales
- Sélection intelligente (round-robin, limites)
"""
import json
import random
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from cryptography.fernet import Fernet


class AccountManager:
    def __init__(self, data_dir: str = "accounts"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.key_file = self.data_dir / ".master_key"
        self._init_crypto()
        self.accounts: List[dict] = self._load_all()

    def _init_crypto(self):
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                self.cipher = Fernet(f.read())
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            self.cipher = Fernet(key)
            os.chmod(self.key_file, 0o600)

    def _encrypt(self, pwd: str) -> str:
        return self.cipher.encrypt(pwd.encode()).decode()

    def _decrypt(self, enc: str) -> str:
        return self.cipher.decrypt(enc.encode()).decode()

    def _load_all(self) -> List[dict]:
        accounts = []
        for file in sorted(self.data_dir.glob("account_*.json")):
            try:
                with open(file) as f:
                    data = json.load(f)
                    if data.get("password_encrypted"):
                        data["password"] = self._decrypt(data["password_encrypted"])
                    # Déchiffrement du seed 2FA
                    if data.get("two_factor_seed_encrypted"):
                        data["two_factor_seed"] = self._decrypt(data["two_factor_seed_encrypted"])
                    accounts.append(data)
            except Exception as e:
                print(f"⚠️  Erreur {file.name}: {e}")
        return sorted(accounts, key=lambda a: a.get("id", 0))

    def _save(self, account: dict):
        path = self.data_dir / f"account_{account['id']:04d}.json"
        data = account.copy()
        data["password_encrypted"] = self._encrypt(account["password"])
        data.pop("password", None)
        # Chiffre aussi la clé 2FA si présente
        if account.get("two_factor_seed"):
            data["two_factor_seed_encrypted"] = self._encrypt(account["two_factor_seed"])
            data.pop("two_factor_seed", None)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def add_account(self, username: str, password: str,
                    platform: str = "instagram",
                    proxy: Optional[str] = None,
                    tags: Optional[list] = None,
                    two_factor_seed: Optional[str] = None) -> dict:
        """Ajoute un compte. platform: instagram|threads|twitter"""
        account = {
            "id": len(self.accounts) + 1,
            "username": username,
            "password": password,
            "two_factor_seed": two_factor_seed or "",  # Clé TOTP secret pour 2FA
            "platform": platform,
            "proxy": proxy,
            "tags": tags or [],
            "active": True,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "last_action": None,
            "daily_actions": 0,
            "total_actions": 0,
            "status": "pending",
            "notes": ""
        }
        self.accounts.append(account)
        self._save(account)
        print(f"✅ #{account['id']} {username} ({platform}) ajouté {'[2FA]' if two_factor_seed else ''}")
        return account

    def remove_account(self, account_id: int):
        self.accounts = [a for a in self.accounts if a["id"] != account_id]
        path = self.data_dir / f"account_{account_id:04d}.json"
        if path.exists():
            path.unlink()

    def get_account(self, account_id: int) -> Optional[dict]:
        for a in self.accounts:
            if a["id"] == account_id:
                return a
        return None

    def get_by_username(self, username: str) -> Optional[dict]:
        for a in self.accounts:
            if a["username"] == username:
                return a
        return None

    def get_random(self, platform: str = "instagram",
                   exclude_ids: Optional[list] = None) -> Optional[dict]:
        exclude_ids = exclude_ids or []
        eligible = [
            a for a in self.accounts
            if a["active"] and a["status"] not in ("banned",)
            and a["id"] not in exclude_ids
            and a["platform"] == platform
            and a["daily_actions"] < 150
        ]
        if not eligible:
            return None
        eligible.sort(key=lambda a: a["daily_actions"])
        return eligible[0]

    def get_multiple(self, count: int, platform: str = "instagram") -> List[dict]:
        selected, exclude = [], []
        for _ in range(count):
            acc = self.get_random(platform=platform, exclude_ids=exclude)
            if acc:
                selected.append(acc)
                exclude.append(acc["id"])
            else:
                break
        return selected

    def increment(self, account_id: int, action: str = "like"):
        a = self.get_account(account_id)
        if not a:
            return
        a["total_actions"] += 1
        a["daily_actions"] += 1
        a["last_action"] = datetime.now().isoformat()
        self._save(a)

    def set_status(self, account_id: int, status: str, notes: str = ""):
        a = self.get_account(account_id)
        if a:
            a["status"] = status
            if notes:
                a["notes"] = notes
            self._save(a)

    def reset_daily_limits(self):
        for a in self.accounts:
            a["daily_actions"] = 0
            self._save(a)
        print("🔄 Limites quotidiennes réinitialisées")

    def import_csv(self, csv_path: str) -> int:
        import csv
        count = 0
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tags = [t.strip() for t in row.get("tags", "").split(",") if t.strip()]
                self.add_account(
                    username=row["username"],
                    password=row["password"],
                    platform=row.get("platform", "instagram"),
                    proxy=row.get("proxy") or None,
                    tags=tags,
                    two_factor_seed=row.get("2fa_seed") or row.get("two_factor_seed") or None
                )
                count += 1
        return count

    def get_stats(self) -> dict:
        total = len(self.accounts)
        platforms = {}
        statuses = {}
        for a in self.accounts:
            p = a["platform"]
            platforms[p] = platforms.get(p, 0) + 1
            s = a["status"]
            statuses[s] = statuses.get(s, 0) + 1
        return {
            "total": total,
            "platforms": platforms,
            "statuses": statuses,
            "active": sum(1 for a in self.accounts if a["active"] and a["status"] == "active"),
            "banned": sum(1 for a in self.accounts if a["status"] == "banned"),
            "challenge": sum(1 for a in self.accounts if a["status"] == "challenge"),
            "total_actions": sum(a["total_actions"] for a in self.accounts),
            "today_actions": sum(a["daily_actions"] for a in self.accounts)
        }

    def get_dataframe(self):
        import pandas as pd
        rows = []
        for a in self.accounts:
            rows.append({
                "ID": a["id"],
                "Username": a["username"],
                "Plateforme": a["platform"],
                "Statut": a["status"],
                "Actif": "✅" if a["active"] and a["status"] == "active" else "❌",
                "Actions Auj": a["daily_actions"],
                "Total": a["total_actions"],
                "Tags": ", ".join(a["tags"]),
                "Proxy": a["proxy"] or "—",
                "Dernière action": a["last_action"] or "—"
            })
        return pd.DataFrame(rows)


# Singleton
_instance = None
def get_manager() -> AccountManager:
    global _instance
    if _instance is None:
        _instance = AccountManager()
    return _instance
