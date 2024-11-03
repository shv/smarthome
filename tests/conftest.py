import pytest
from fastapi.testclient import TestClient
from faker import Faker

from smarthome.main import app
from smarthome.settings import settings
from smarthome.connectors.database import Base, engine
from smarthome.depends import get_db
from smarthome import models

fake = Faker()

@pytest.fixture(scope="session")
def client():
    client = TestClient(app)
    client.base_url = str(client.base_url) + settings.main_url
    return client


@pytest.fixture(autouse=True)
def init_db():
    """ Actions with db before and after each test """
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db():
    # TODO fix it
    # https://fastapi.tiangolo.com/advanced/testing-database/
    return next(get_db())


@pytest.fixture
def create_user_in_db(db):
    def _create_user():
        email = fake.email()
        hashed_password = fake.md5()
        db_user = models.User(email=email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    return _create_user


@pytest.fixture
def get_user_from_db(db):
    def _get_user_from_db(user_id: int):
        return db.query(models.User).filter(models.User.id == user_id).first()
    return _get_user_from_db


@pytest.fixture
def get_user_by_email_from_db(db):
    def _get_user_by_email_from_db(user_email: str):
        return db.query(models.User).filter(models.User.email == user_email).first()
    return _get_user_by_email_from_db


@pytest.fixture
def create_token_in_db(db):
    def _create_token_in_db(user_id: int):
        token = fake.md5()
        db_token = models.UserToken(user_id=user_id, token=token)
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return db_token
    return _create_token_in_db
