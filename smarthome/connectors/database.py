"""
DB connector
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from smarthome.settings import settings

engine = create_engine(
    settings.pg_dsn, echo=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
