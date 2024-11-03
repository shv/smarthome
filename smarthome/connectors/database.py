"""
DB connector
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from smarthome.settings import settings

SQLALCHEMY_DATABASE_URL = settings.pg_dsn

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
