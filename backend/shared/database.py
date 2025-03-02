from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.shared.config import shared_config
import os

DATABASE_URL = f"postgresql://{shared_config.DB_USER}:{shared_config.DB_PASSWORD}@{shared_config.DB_HOST}:{shared_config.DB_PORT}/{shared_config.DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    from backend.shared.models import Base
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for getting a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
