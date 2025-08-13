import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Load .env and prefer its values
load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to local SQLite for dev
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    sqlite_path = os.path.join(BASE_DIR, "db", "app.db")
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    DATABASE_URL = f"sqlite:///{sqlite_path}"

engine_kwargs = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

