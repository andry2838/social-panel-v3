#!/usr/bin/env python3
"""Génère des comptes de test pour les 3 plateformes."""
import sys
sys.path.insert(0, ".")
from core.account_manager import get_manager

def generate(count: int = 50):
    mgr = get_manager()
    platforms = ["instagram", "threads", "twitter"]
    niches = ["nature", "travel", "food", "tech", "art", "music", "sport", "fashion"]
    proxies = ["http://proxy1:8080", "http://proxy2:8080", None, None, None]

    for i in range(count):
        plat = platforms[i % 3]
        niche = niches[i % len(niches)]
        proxy = proxies[i % len(proxies)]
        mgr.add_account(
            username=f"{plat}_{niche}_{i+1:04d}",
            password=f"Pass{i+1:04d}!",
            platform=plat,
            proxy=proxy,
            tags=[niche, "fr"]
        )

    s = mgr.get_stats()
    print(f"\n✅ {count} comptes générés !")
    for p, n in s["platforms"].items():
        print(f"   {p}: {n}")

if __name__ == "__main__":
    generate(int(sys.argv[1]) if len(sys.argv) > 1 else 50)
