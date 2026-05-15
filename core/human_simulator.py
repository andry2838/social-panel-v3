"""
Simulation de comportements humains réalistes.
Délais aléatoires, décisions pondérées, texte variable.
"""
import random
import time
from datetime import datetime


class HumanSimulator:
    TIMINGS = {
        "like":        (1.0, 4.0),
        "unlike":      (0.5, 2.0),
        "comment":     (15.0, 90.0),
        "follow":      (5.0, 20.0),
        "unfollow":    (3.0, 10.0),
        "scroll":      (2.0, 8.0),
        "view_post":   (3.0, 15.0),
        "view_story":  (1.0, 5.0),
        "view_profile":(10.0, 30.0),
        "post":        (30.0, 180.0),
        "login":       (5.0, 15.0),
        "between":     (2.0, 8.0),
    }

    @staticmethod
    def pause(action: str = "between"):
        min_t, max_t = HumanSimulator.TIMINGS.get(action, (1, 3))
        mean = (min_t + max_t) / 2
        std = (max_t - min_t) / 4
        delay = abs(random.gauss(mean, std))
        delay = max(min_t, min(delay, max_t))
        time.sleep(delay)

    @staticmethod
    def should_act(probability: float = 0.3) -> bool:
        return random.random() < probability

    @staticmethod
    def random_hour(min_h: int = 8, max_h: int = 22) -> int:
        return random.randint(min_h, max_h)

    @staticmethod
    def random_minute() -> int:
        return random.randint(0, 59)

    @staticmethod
    def is_sleep_time(min_h: int = 23, max_h: int = 7) -> bool:
        h = datetime.now().hour
        if min_h > max_h:
            return h >= min_h or h < max_h
        return min_h <= h < max_h

    @staticmethod
    def random_comment(style: str = "auto") -> str:
        comments = {
            "compliment": [
                "Magnifique ! 🔥", "Trop beau !", "Incroyable 😍",
                "Superbe !", "Waouh !", "Quelle qualité !",
            ],
            "short": ["🔥", "❤️", "👏", "💯", "Top !", "Bravo !"],
            "question": [
                "C'est où ?", "Tu shootes avec quoi ?",
                "Quels réglages ?", "Tu utilises Lightroom ?",
            ],
            "supportive": [
                "Continue comme ça !", "Inspirant !",
                "Merci pour le partage !", "Hâte de voir la suite !",
            ],
        }
        if style == "auto":
            weights = {"compliment": 0.40, "short": 0.30, "supportive": 0.20, "question": 0.10}
            style = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
        return random.choice(comments.get(style, comments["short"]))

    @staticmethod
    def random_tweet() -> str:
        tweets = [
            "Superbe journée ! ✨",
            "Nouvelle découverte incroyable 🔥",
            "Quel coucher de soleil ! 🌅",
            "Trop hâte de partager ça !",
            "Le meilleur moment de la journée ☀️",
            "Quelqu'un d'autre aime ça ? 👇",
        ]
        return random.choice(tweets)
