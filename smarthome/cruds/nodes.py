"""
Node CRUD
"""
from sqlalchemy.orm import Session

from smarthome import models


def get_nodes(db: Session, skip: int = 0, limit: int = 100):
    """ Get node list """
    return db.query(models.Node).offset(skip).limit(limit).all()


async def get_node_by_token(db: Session, token: str):
    """ Get node by token """
    result = db.query(models.Node).join(models.NodeToken).filter(models.NodeToken.token == token).first()
    return result
