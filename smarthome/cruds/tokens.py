""" Token CRUD """
from sqlalchemy.orm import Session

from smarthome import models


def get_token_by_token(db: Session, token: str) -> models.UserToken:
    """ Get token """
    return db.query(models.UserToken).filter(models.UserToken.token == token).first()


def get_token_by_user_id(db: Session, user_id: int) -> models.UserToken:
    """ Get token """
    return db.query(models.UserToken).filter(models.UserToken.user_id == user_id).first()


def create_token(db: Session, user_id: int, token: str):
    """ Create new token """
    db_token = models.UserToken(user_id=user_id, token=token)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token
