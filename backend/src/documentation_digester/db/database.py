from documentation_digester.config.settings import settings
from sqlalchemy.orm import sessionmaker, Session

from sqlalchemy import create_engine

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()