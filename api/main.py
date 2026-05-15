from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

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

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok", "version": "3.0.0"}
