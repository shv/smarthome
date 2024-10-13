"""
Dependencies
"""
from smarthome.connectors.database import Base, engine, SessionLocal


def get_db():
    """ Create db connection """
    # TODO: move to right place (alembic)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
