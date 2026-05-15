from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

app = FastAPI(
    title="Social Panel API",
    description="Gestion multi-comptes Instagram + Threads + Twitter/X",
    version="3.0.0"
)

# Initialisation de la base de données
from core.database import engine, Base
import core.models

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

from fastapi.staticfiles import StaticFiles
import os

@app.get("/health")
def health():
    return {"status": "ok", "version": "3.0.0"}

# Serve modern React frontend
dist_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(dist_path):
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="frontend")
