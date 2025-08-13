import os
from dotenv import load_dotenv
# Force-load repo .env
DOTENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
load_dotenv(DOTENV_PATH, override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.engine.url import make_url, URL
import typing as _t
from .db.database import create_tables
from .api.endpoints import router as api_router

app = FastAPI(title="Autonomous Launch Orchestrator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _mask_db_url(raw: str) -> _t.Dict[str, _t.Any]:
    try:
        u: URL = make_url(raw)
        return {
            "drivername": u.drivername,
            "host": u.host,
            "port": u.port,
            "database": u.database,
            "username": "****" if u.username else None,
        }
    except Exception:
        return {"invalid_url": True}

def _validate_env() -> _t.Dict[str, _t.Any]:
    db_url = os.getenv("DATABASE_URL")
    n8n_base = os.getenv("N8N_BASE_URL")
    google_key = os.getenv("GOOGLE_API_KEY")

    issues = []
    if not db_url:
        issues.append("DATABASE_URL missing")
    elif "@localhost" in db_url and "%40" not in db_url and "@" in db_url.split("://", 1)[1].split("@")[0]:
        issues.append("DATABASE_URL password contains '@' but is not URL-encoded (%40)")

    if not n8n_base:
        issues.append("N8N_BASE_URL missing")

    return {
        "database_url": _mask_db_url(db_url) if db_url else None,
        "n8n_base_url": n8n_base,
        "google_api_key_set": bool(google_key),
        "issues": issues,
        "webhook_envs": {
            "MARKETING_GENERAL": bool(os.getenv("N8N_WEBHOOK_MARKETING_GENERAL")),
            "DEVELOPER_GENERAL": bool(os.getenv("N8N_WEBHOOK_DEVELOPER_GENERAL")),
            "SALES_GENERAL": bool(os.getenv("N8N_WEBHOOK_SALES_GENERAL")),
            "LEGAL_GENERAL": bool(os.getenv("N8N_WEBHOOK_LEGAL_GENERAL")),
            "GENERAL_WORKFLOW": bool(os.getenv("N8N_WEBHOOK_GENERAL_WORKFLOW")),
        },
    }

app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    cfg = _validate_env()
    if cfg["issues"]:
        # Log issues; keep running so you can see /config
        print("[config] Issues:", cfg["issues"])
    create_tables()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/config")
async def config():
    return _validate_env()

@app.get("/")
async def index():
    return {
        "message": "Backend running",
        "docs": "/docs",
        "health": "/health",
        "config": "/config",
        "api_examples": [
            "POST /api/create-plan",
            "GET /api/tasks",
            "POST /api/tasks/{task_id}/approve",
        ],
    }


