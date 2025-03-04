"""
Database Connector Module for Smart Home System.

This module provides SQLAlchemy database connection setup and session management
for the smart home system. It configures the database engine, session factory,
and declarative base for ORM models.
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from smarthome.settings import settings

# Create database engine with PostgreSQL connection string from settings
engine: Engine = create_engine(
    settings.pg_dsn, 
    echo=True,  # SQL query logging for debugging
)

# Session factory for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()
