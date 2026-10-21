import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL

# Render / Heroku compatibility: SQLAlchemy 2.0 requires postgresql:// instead of postgres://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ── SQLite: ensure parent directory exists ────────────────────────────────────
# Handles sqlite:///relative/path  and  sqlite:////absolute/path (Render disk)
if DATABASE_URL.startswith("sqlite:///"):
    raw = DATABASE_URL[len("sqlite:///"):]          # strip the 3-slash prefix
    if raw.startswith("/"):                           # absolute path (4 slashes total)
        sqlite_path = raw
    else:                                             # relative path
        sqlite_path = os.path.join(os.getcwd(), raw)
    db_dir = os.path.dirname(sqlite_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
        logger.info("SQLite data directory: %s", db_dir)

# ── SQLAlchemy engine ─────────────────────────────────────────────────────────
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
