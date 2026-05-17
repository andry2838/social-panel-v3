"""
Moteur Instagram Extrême via Instagrapi.
Intègre les fonctionnalités SaaS Premium : Vues de masse, interactions de Story,
likes multi-niveaux, commentaires IA et filtrage de langues.
"""
import random
import os
import requests
from typing import Optional, List, Dict
from instagrapi import Client
import pyotp
from instagrapi.exceptions import ChallengeRequired, FeedbackRequired, TwoFactorRequired
from .human_simulator import HumanSimulator
from .account_manager import get_manager

class InstagramEngine:
    def __init__(self):
        self.clients = {}

    def get_client(self, account: dict) -> Optional[Client]:
        aid = account.get("id")
        if aid in self.clients:
            return self.clients[aid]

        cl = Client()
        # Gestionnaire de temps aléatoire injecté directement dans le client
        cl.delay_range = [2, 5] 
        
        cl.set_user_agent(
            "Instagram 289.0.0.77.109 Android (33/13; 420dpi; 1080x2400; "
            "OnePlus; ONEPLUS+A6003; OnePlus6; qcom; fr_FR; 482756178)"
        )
        
        if account.get("proxy"):
            cl.set_proxy(account["proxy"])

        session_path = f"accounts/session_ig_{account.get('username')}.json"
        try:
            cl.load_settings(session_path)
        except:
            pass

        try:
            cl.login(account["username"], account["password"])
            cl.dump_settings(session_path)
            self.clients[aid] = cl
            return cl
        except TwoFactorRequired:
            print(f"⚠️ 2FA requis pour {account['username']}")
            two_factor_seed = account.get("two_factor_seed") or account.get("tags", [None])[0] # Fallback if stored in tags
            if two_factor_seed and len(two_factor_seed) > 10:
                try:
                    totp = pyotp.TOTP(two_factor_seed.replace(" ", "").upper())
                    code = totp.now()
                    cl.two_factor_login(code)
                    cl.dump_settings(session_path)
                    self.clients[aid] = cl
                    return cl
                except Exception as e:
                    print(f"❌ Erreur 2FA PyOTP: {e}")
                    return None
            else:
                print("❌ Echec 2FA: Pas de clé secrète (TOTP Seed) configurée.")
                return None
        except ChallengeRequired:
            print(f"⚠️ Challenge requis pour {account['username']}")
            return None
        except FeedbackRequired:
            print(f"⚠️ Temp ban pour {account['username']}")
            return None
        except Exception as e:
            print(f"⚠️ IG login {account['username']}: {e}")
            return None

    # --- MODULE 1 : STORY ACTIONS (Engagement Extrême) ---

    def mass_look_and_interact_stories(self, account: dict, target_user: str) -> dict:
        """Visionne les stories d'un utilisateur et interagit avec les stickers (Sondages, Sliders)."""
        cl = self.get_client(account)
        if not cl:
            return {"status": "error"}
            
        stats = {"viewed": 0, "liked": 0, "polls_voted": 0, "sliders_voted": 0}
        
        try:
            user_id = cl.user_id_from_username(target_user)
            stories = cl.user_stories(user_id)
            
            for story in stories:
                # Visionnage (Mass Looking)
                cl.story_view([story.pk])
                stats["viewed"] += 1
                HumanSimulator.pause("scroll")
                
                # Story Like
                if HumanSimulator.should_act(0.3): # 30% de chance de liker
                    cl.story_like(story.pk)
                    stats["liked"] += 1
                
                # Interactions avec les Stickers (Sondages, Sliders)
                if hasattr(story, 'story_polls') and story.story_polls:
                    for poll in story.story_polls:
                        if HumanSimulator.should_act(0.8): # 80% de chance de voter
                            # Vote aléatoire (0 ou 1)
                            cl.story_poll_vote(story.pk, poll.poll_id, random.choice([0, 1]))
                            stats["polls_voted"] += 1
                            HumanSimulator.pause("like")
                            
                if hasattr(story, 'story_sliders') and story.story_sliders:
                    for slider in story.story_sliders:
                        if HumanSimulator.should_act(0.8):
                            # Curseur aléatoire entre 50% et 100%
                            cl.story_slider_vote(story.pk, slider.slider_id, random.uniform(0.5, 1.0))
                            stats["sliders_voted"] += 1
                            HumanSimulator.pause("like")
                            
        except Exception as e:
            print(f"⚠️ Erreur Story Interaction: {e}")
            
        return stats

    # --- MODULE 2 : FEED & COMMENTS (Engagement Ciblé) ---

    def like_top_comments(self, account: dict, target_media_id: str, amount: int = 3) -> int:
        """Likes multi-niveaux : Aime les meilleurs commentaires sous un post spécifique."""
        cl = self.get_client(account)
        if not cl:
            return 0
            
        liked_count = 0
        try:
            comments = cl.media_comments(target_media_id, amount=10)
            # Trier par nombre de likes pour trouver les "meilleurs"
            top_comments = sorted(comments, key=lambda c: c.like_count, reverse=True)
            
            for comment in top_comments[:amount]:
                if HumanSimulator.should_act(0.6):
                    cl.comment_like(comment.pk)
                    liked_count += 1
                    HumanSimulator.pause("like")
        except Exception as e:
            print(f"⚠️ Erreur Like Commentaire: {e}")
            
        return liked_count

    def generate_ai_comment(self, context: str) -> str:
        """Utilise l'API Groq (LM Studio) pour générer un commentaire pertinent et naturel."""
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            # Fallback sur Spintax basique si pas d'API Key
            return HumanSimulator.random_comment()
            
        try:
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "mixtral-8x7b-32768",
                "messages": [
                    {"role": "system", "content": "Tu es un utilisateur Instagram. Écris un commentaire court, humain et pertinent (1 phrase, 1 emoji) basé sur le contexte. Pas de hashtags."},
                    {"role": "user", "content": f"Le post parle de : {context}"}
                ],
                "temperature": 0.7
            }
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
            return response.json()["choices"][0]["message"]["content"].strip().replace('"', '')
        except:
            return HumanSimulator.random_comment()

    # --- MODULE 3 : CROISSANCE & FILTRAGE (Follow/Unfollow) ---

    def check_language_filter(self, bio: str, allowed_langs: List[str]) -> bool:
        """Vérifie si l'utilisateur cible correspond aux langues exigées (basé sur des mots-clés dans la bio)."""
        if not allowed_langs:
            return True # Aucun filtre
            
        bio_lower = bio.lower()
        
        # Dictionnaire basique de détection
        lang_keywords = {
            "fr": ["france", "paris", "français", "french", "ouais", "ici"],
            "mg": ["mada", "gasy", "malagasy", "antananarivo", "akory"],
            "en": ["usa", "uk", "english", "world", "official"]
        }
        
        for lang in allowed_langs:
            if lang in lang_keywords:
                for keyword in lang_keywords[lang]:
                    if keyword in bio_lower:
                        return True
        return False

    def smart_follow_loop(self, account: dict, target_competitor: str, allowed_langs: List[str] = []) -> dict:
        """Cycle intelligent pour suivre les abonnés d'un concurrent avec filtrage de langue."""
        cl = self.get_client(account)
        if not cl:
            return {"followed": 0}
            
        followed = 0
        try:
            competitor_id = cl.user_id_from_username(target_competitor)
            followers = cl.user_followers(competitor_id, amount=20)
            
            for uid, user_info in followers.items():
                if followed >= 5: # Limite par cycle pour la sécurité
                    break
                    
                # Extraire la bio complète pour le filtre (nécessite parfois un appel user_info)
                full_info = cl.user_info(uid)
                bio = full_info.biography
                
                # Filtrage de langue
                if allowed_langs and not self.check_language_filter(bio, allowed_langs):
                    continue # On saute cet utilisateur
                    
                if HumanSimulator.should_act(0.5):
                    cl.user_follow(uid)
                    followed += 1
                    HumanSimulator.pause("follow")
                    
        except Exception as e:
            print(f"⚠️ Erreur Smart Follow: {e}")
            
        return {"followed": followed}

    # --- MODULE 4 : ACTIONS BULK (Hashtag) ---

    def like_from_hashtag(self, account: dict, hashtag: str, amount: int = 5) -> int:
        """Like des posts récents d'un hashtag."""
        cl = self.get_client(account)
        if not cl:
            return 0
        count = 0
        try:
            tag = hashtag.lstrip('#')
            medias = cl.hashtag_medias_recent(tag, amount=amount * 3)
            for media in medias[:amount]:
                if HumanSimulator.should_act(0.7):
                    cl.media_like(media.pk)
                    get_manager().increment(account["id"], "like")
                    count += 1
                    HumanSimulator.pause("like")
        except Exception as e:
            print(f"⚠️ Erreur like hashtag #{hashtag}: {e}")
        return count

    def comment_on_hashtag(self, account: dict, hashtag: str, amount: int = 3) -> int:
        """Commente des posts récents d'un hashtag via l'IA."""
        cl = self.get_client(account)
        if not cl:
            return 0
        count = 0
        try:
            tag = hashtag.lstrip('#')
            medias = cl.hashtag_medias_recent(tag, amount=amount * 4)
            for media in medias[:amount]:
                if HumanSimulator.should_act(0.5):
                    context = (media.caption_text or "post Instagram")[:100]
                    comment_text = self.generate_ai_comment(context)
                    cl.media_comment(media.pk, comment_text)
                    get_manager().increment(account["id"], "comment")
                    count += 1
                    HumanSimulator.pause("comment")
        except Exception as e:
            print(f"⚠️ Erreur comment hashtag #{hashtag}: {e}")
        return count

    def follow_followers(self, account: dict, target_username: str, amount: int = 5) -> int:
        """Suit les abonnés d'un compte cible."""
        cl = self.get_client(account)
        if not cl:
            return 0
        followed = 0
        try:
            username = target_username.lstrip('@')
            user_id = cl.user_id_from_username(username)
            followers = cl.user_followers(user_id, amount=amount * 3)
            for uid in list(followers.keys())[:amount]:
                if HumanSimulator.should_act(0.6):
                    cl.user_follow(uid)
                    get_manager().increment(account["id"], "follow")
                    followed += 1
                    HumanSimulator.pause("follow")
        except Exception as e:
            print(f"⚠️ Erreur follow followers de @{target_username}: {e}")
        return followed

    def post_photo(self, account: dict, image_path: str, caption: str) -> Optional[str]:
        """Publie une photo sur Instagram."""
        cl = self.get_client(account)
        if not cl:
            return None
        try:
            if not os.path.exists(image_path):
                print(f"⚠️ Image introuvable : {image_path}")
                return None
            media = cl.photo_upload(image_path, caption)
            get_manager().increment(account["id"], "post")
            return str(media.pk)
        except Exception as e:
            print(f"⚠️ Erreur post photo: {e}")
            return None

    def run_daily_routine(self, account: dict) -> dict:
        """Routine quotidienne complète : likes hashtag + smart follow."""
        cl = self.get_client(account)
        if not cl:
            return {"status": "error", "reason": "login"}

        results = {"likes": 0, "follows": 0}

        # 1. Liker via les tags du compte (ou tags par défaut)
        tags = account.get("tags") or ["lifestyle", "inspiration", "motivation"]
        for tag in [t for t in tags if t][:2]:
            count = self.like_from_hashtag(account, tag, amount=random.randint(5, 12))
            results["likes"] += count
            HumanSimulator.pause("between")

        # 2. Follow intelligent aléatoire
        if HumanSimulator.should_act(0.4):
            default_targets = ["instagram", "natgeo", "9gag"]
            res = self.smart_follow_loop(account, random.choice(default_targets))
            results["follows"] += res.get("followed", 0)
            HumanSimulator.pause("between")

        get_manager().set_status(account["id"], "active")
        return {"status": "success", **results}
