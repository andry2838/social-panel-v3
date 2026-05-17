import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 1. Base de données EN PREMIER (avant tout import de routes)
from core.database import engine, Base
import core.models
Base.metadata.create_all(bind=engine)

# 2. App FastAPI
app = FastAPI(
    title="Social Panel API",
    description="Gestion multi-comptes Instagram + Threads + Twitter/X",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Routes (après DB init)
from .routes import router
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok", "version": "3.0.0"}

# 4. Serve React frontend si build existe
dist_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(dist_path):
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    # Récupérer de façon sécurisée le port injecté par Railway
    port_str = os.environ.get("PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        port = 8000
    print(f"🚀 Démarrage du serveur FastAPI sur le port {port}...")
    uvicorn.run("api.main:app", host="0.0.0.0", port=port)
