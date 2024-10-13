"""
User CRUD
"""
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect

from smarthome import models, schemas


def get_user(db: Session, user_id: int):
    """ Get user """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    """ Get user by email """
    return db.query(models.User).filter(models.User.email == email).first()


async def get_user_by_token(db: Session, token: str):
    """ Get user by token """
    result = db.query(models.User).join(models.UserToken).filter(models.UserToken.token == token).first()
    return result


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """ Get user list """
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    """ Create user """
    # TODO: hash password
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
