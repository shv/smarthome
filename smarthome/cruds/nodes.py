"""
Node CRUD
"""
from sqlalchemy.orm import Session

from smarthome import models, schemas


def get_node(db: Session, node_id: int):
    """ Get node """
    return db.query(models.Node).filter(models.Node.id == node_id).first()


def get_nodes(db: Session, skip: int = 0, limit: int = 100):
    """ Get node list """
    return db.query(models.Node).offset(skip).limit(limit).all()


async def get_node_by_token(db: Session, token: str):
    """ Get node by token """
    result = db.query(models.Node).join(models.NodeToken).filter(models.NodeToken.token == token).first()
    return result


def create_node_state(db: Session, node_state: schemas.NodeStateCreate):
    """ Create node state """
    db_node_state = models.NodeState(data=node_state.data, node_id=node_state.node_id)
    db.add(db_node_state)
    db.commit()
    db.refresh(db_node_state)
    return db_node_state


def get_node_current_values(db: Session, node_id: int, skip: int = 0, limit: int = 100):
    """ Get node current_values list """
    return db.query(models.NodeCurrentValue).filter(
        models.NodeCurrentValue.node_id == node_id
    ).offset(skip).limit(limit).all()


def upsert_node_current_values(db: Session, node_id: int, current_value: schemas.NodeCurrentValueCreate):
    """ Upsert node current_values list """
    db_value = db.query(models.NodeCurrentValue).filter(
        models.NodeCurrentValue.node_id == node_id,
        models.NodeCurrentValue.name == current_value.name
    ).first()
    if db_value:
        db_value.value = {"value": current_value.value}
    else:
        db_value = models.NodeCurrentValue(node_id=node_id, name=current_value.name, value={"value": current_value.value})
        db.add(db_value)
    db.commit()
    db.refresh(db_value)
    return db_value
