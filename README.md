# Social Panel v3

Gestion multi-comptes automatisée pour **Instagram** + **Threads** + **Twitter/X**.

## Stack

- **Backend API** : FastAPI (port 8000)
- **Dashboard** : Streamlit (port 8501)
- **Scheduler** : Celery + Redis
- **Moteurs** : Instagrapi, threads-api, twikit
- **Déploiement** : Docker Compose

## Démarrage rapide

```bash
# 1. Lancer tous les services
docker compose up -d

# 2. Dashboard → http://localhost:8501
# 3. API → http://localhost:8000

# Pour ajouter des comptes de test :
docker compose exec api python scripts/generate_test_accounts.py 100
```

Sans Docker
```bash
# 1. Redis doit tourner (sudo apt install redis-server)
# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Générer des comptes de test (optionnel)
python scripts/generate_test_accounts.py 100

# 4. Lancer les 4 services (4 terminaux)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
streamlit run dashboard/app.py
celery -A scheduler.celery_app worker -l info --concurrency=10
celery -A scheduler.celery_app beat -l info
```

Structure
```
Dossier	Rôle
core/	Moteurs (Instagram, Threads, Twitter) + gestion comptes + simulation humaine
scheduler/	Tâches planifiées Celery
api/	API REST FastAPI
dashboard/	Interface Streamlit
scripts/	Utilitaires (import CSV, génération test)
accounts/	Sessions et comptes chiffrés
```

Import de comptes
Format CSV :

```csv
username,password,platform,proxy,tags
monuser,mypass,instagram,http://proxy:8080,travel,fr
user2,pass2,twitter,,
user3,pass3,threads,,tech
```

---

## Déploiement final

```bash
# Tout installer en 2 commandes
mkdir social-panel-v3 && cd social-panel-v3
# Copier tous les fichiers du projet...

# Lancer
docker compose up -d

# Accès
echo "📊 Dashboard: http://localhost:8501"
echo "🔌 API:       http://localhost:8000/health"
echo "⚡ Générer 100 comptes de test: docker compose exec api python scripts/generate_test_accounts.py 100"
```

Ce que tu as :

✅ 3 plateformes stables : Instagram, Threads, Twitter/X
✅ 100+ comptes gérés avec chiffrement
✅ Routines quotidiennes automatiques avec heures aléatoires
✅ Simulation de comportement humain (délais gaussiens, décisions pondérées)
✅ Tableau de bord temps réel
✅ API REST pour tout contrôler
✅ Import CSV pour ajouter des comptes en masse
✅ Dockerisé, prêt à déployer
