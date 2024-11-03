"""
User CRUD
"""
from sqlalchemy.orm import Session

from smarthome import models


def get_user_by_email(db: Session, email: str):
    """ Get user by email """
    return db.query(models.User).filter(models.User.email == email).first()


async def get_user_by_token(db: Session, token: str):
    """ Get user by token """
    result = db.query(models.User).join(models.UserToken).filter(models.UserToken.token == token).first()
    return result
