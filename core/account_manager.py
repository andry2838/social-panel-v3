"""
Gestionnaire de pool de comptes multi-plateforme unifié sur SQLAlchemy.
- Chiffrement AES des mots de passe et clés 2FA
- Gestion 100+ comptes en base de données
- Import CSV
- Stats globales
- Sélection intelligente (round-robin, limites)
"""
import csv
import os
import random
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from cryptography.fernet import Fernet
import pandas as pd

from .database import SessionLocal
from .models import Account


class AccountManager:
    def __init__(self, data_dir: str = "accounts"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.key_file = self.data_dir / ".master_key"
        self._init_crypto()
        
        # Garantir l'initialisation de la base de données
        from .database import engine, Base
        import core.models
        Base.metadata.create_all(bind=engine)

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
        if not pwd:
            return ""
        return self.cipher.encrypt(pwd.encode()).decode()

    def _decrypt(self, enc: str) -> str:
        if not enc:
            return ""
        return self.cipher.decrypt(enc.encode()).decode()

    def _to_dict(self, a: Account) -> dict:
        """Convertit un objet SQLAlchemy Account en dictionnaire déchiffré."""
        if not a:
            return {}
            
        password = a.password
        if password and password.startswith("gAAAAA"):
            try:
                password = self._decrypt(password)
            except Exception:
                pass
                
        two_factor_seed = a.two_factor_seed
        if two_factor_seed and two_factor_seed.startswith("gAAAAA"):
            try:
                two_factor_seed = self._decrypt(two_factor_seed)
            except Exception:
                pass

        return {
            "id": int(a.id) if (a.id and a.id.isdigit()) else a.id,
            "username": a.username,
            "password": password,
            "two_factor_seed": two_factor_seed or "",
            "platform": a.platform,
            "proxy": a.proxy,
            "tags": a.tags or [],
            "active": a.active if a.active is not None else True,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "last_login": a.last_login.isoformat() if a.last_login else None,
            "last_action": a.last_action.isoformat() if a.last_action else None,
            "daily_actions": a.daily_actions or 0,
            "total_actions": a.total_actions or 0,
            "status": a.status or "pending",
            "notes": a.notes or "",
            "email": a.email or ""
        }

    @property
    def accounts(self) -> List[dict]:
        """Sert de pont de compatibilité en renvoyant tous les comptes sous forme de liste de dicts."""
        db = SessionLocal()
        try:
            db_accs = db.query(Account).order_by(Account.id).all()
            return [self._to_dict(a) for a in db_accs]
        finally:
            db.close()

    def add_account(self, username: str, password: str,
                    platform: str = "instagram",
                    proxy: Optional[str] = None,
                    tags: Optional[list] = None,
                    two_factor_seed: Optional[str] = None,
                    email: Optional[str] = None) -> dict:
        """Ajoute un compte directement en base de données avec chiffrement."""
        db = SessionLocal()
        try:
            # Recherche de l'ID maximal pour l'incrémentation
            max_id = 0
            for a in db.query(Account).all():
                try:
                    if int(a.id) > max_id:
                        max_id = int(a.id)
                except Exception:
                    pass
            new_id = str(max_id + 1)
            
            enc_password = self._encrypt(password)
            enc_2fa = self._encrypt(two_factor_seed) if two_factor_seed else None
            
            db_acc = Account(
                id=new_id,
                username=username,
                password=enc_password,
                platform=platform,
                proxy=proxy,
                tags=tags or [],
                two_factor_seed=enc_2fa,
                email=email,
                active=True,
                status="pending",
                daily_actions=0,
                total_actions=0,
                notes=""
            )
            db.add(db_acc)
            db.commit()
            db.refresh(db_acc)
            
            print(f"[OK] #{db_acc.id} {username} ({platform}) ajoute en DB {'[2FA]' if two_factor_seed else ''}")
            return self._to_dict(db_acc)
        finally:
            db.close()

    def remove_account(self, account_id: int):
        """Supprime le compte de la base de données."""
        db = SessionLocal()
        try:
            db.query(Account).filter(Account.id == str(account_id)).delete()
            db.commit()
        finally:
            db.close()

    def get_account(self, account_id: int) -> Optional[dict]:
        """Récupère un compte par son ID."""
        db = SessionLocal()
        try:
            a = db.query(Account).filter(Account.id == str(account_id)).first()
            return self._to_dict(a) if a else None
        finally:
            db.close()

    def get_by_username(self, username: str) -> Optional[dict]:
        """Récupère un compte par son username."""
        db = SessionLocal()
        try:
            a = db.query(Account).filter(Account.username == username).first()
            return self._to_dict(a) if a else None
        finally:
            db.close()

    def get_random(self, platform: str = "instagram",
                   exclude_ids: Optional[list] = None) -> Optional[dict]:
        """Sélectionne un compte éligible au hasard."""
        exclude_ids = exclude_ids or []
        db = SessionLocal()
        try:
            eligible = db.query(Account).filter(
                Account.active == True,
                Account.status != "banned",
                Account.platform == platform,
                Account.daily_actions < 150
            ).all()
            
            eligible = [a for a in eligible if int(a.id) not in exclude_ids]
            
            if not eligible:
                return None
            eligible.sort(key=lambda a: a.daily_actions or 0)
            return self._to_dict(eligible[0])
        finally:
            db.close()

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
        """Incrémente les compteurs d'actions pour le compte."""
        db = SessionLocal()
        try:
            a = db.query(Account).filter(Account.id == str(account_id)).first()
            if a:
                a.total_actions = (a.total_actions or 0) + 1
                a.daily_actions = (a.daily_actions or 0) + 1
                a.last_action = datetime.now()
                db.commit()
        finally:
            db.close()

    def set_status(self, account_id: int, status: str, notes: str = ""):
        """Met à jour le statut du compte."""
        db = SessionLocal()
        try:
            a = db.query(Account).filter(Account.id == str(account_id)).first()
            if a:
                a.status = status
                if notes:
                    a.notes = notes
                db.commit()
        finally:
            db.close()

    def reset_daily_limits(self):
        """Réinitialise toutes les limites d'actions quotidiennes à 0."""
        db = SessionLocal()
        try:
            db.query(Account).update({Account.daily_actions: 0})
            db.commit()
            print("[RESET] Limites quotidiennes reinitialisees en base de donnees.")
        finally:
            db.close()

    def import_csv(self, csv_path: str) -> int:
        """Importe des comptes à partir d'un fichier CSV."""
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
                    two_factor_seed=row.get("2fa_seed") or row.get("two_factor_seed") or None,
                    email=row.get("email") or None
                )
                count += 1
        return count

    def get_stats(self) -> dict:
        """Calcule les statistiques globales des comptes."""
        db = SessionLocal()
        try:
            accounts = db.query(Account).all()
            total = len(accounts)
            platforms = {}
            statuses = {}
            for a in accounts:
                p = a.platform
                platforms[p] = platforms.get(p, 0) + 1
                s = a.status or "pending"
                statuses[s] = statuses.get(s, 0) + 1
            
            return {
                "total": total,
                "platforms": platforms,
                "statuses": statuses,
                "active": sum(1 for a in accounts if a.active and a.status == "active"),
                "banned": sum(1 for a in accounts if a.status == "banned"),
                "challenge": sum(1 for a in accounts if a.status == "challenge"),
                "total_actions": sum(a.total_actions or 0 for a in accounts),
                "today_actions": sum(a.daily_actions or 0 for a in accounts)
            }
        finally:
            db.close()

    def get_dataframe(self) -> pd.DataFrame:
        """Renvoie les statistiques sous forme de DataFrame Pandas pour Streamlit."""
        rows = []
        db = SessionLocal()
        try:
            accounts = db.query(Account).all()
            for a in accounts:
                rows.append({
                    "ID": int(a.id) if (a.id and a.id.isdigit()) else a.id,
                    "Username": a.username,
                    "Plateforme": a.platform,
                    "Statut": a.status,
                    "Actif": "✅" if (a.active and a.status == "active") else "❌",
                    "Actions Auj": a.daily_actions or 0,
                    "Total": a.total_actions or 0,
                    "Tags": ", ".join(a.tags) if a.tags else "",
                    "Proxy": a.proxy or "—",
                    "Dernière action": a.last_action.isoformat() if a.last_action else "—"
                })
        finally:
            db.close()
        return pd.DataFrame(rows)


# Singleton
_instance = None
def get_manager() -> AccountManager:
    global _instance
    if _instance is None:
        _instance = AccountManager()
    return _instance
