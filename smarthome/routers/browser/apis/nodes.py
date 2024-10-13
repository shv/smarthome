"""
Browser APIs with Nodes
"""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from smarthome import models, schemas
from smarthome.auth import get_current_user
from smarthome.settings import settings

router = APIRouter(
    prefix=settings.main_url
)


@router.get("/", response_model=schemas.Nodes)
def get_nodes(
        user: Annotated[models.User, Depends(get_current_user)],
):
    """ Get user nodes endpoint """
    db_nodes = user.nodes
    return dict(nodes=db_nodes)


@router.get("/{node_id}", response_model=schemas.Node)
def get_node(
        node_id: int,
        user: Annotated[models.User, Depends(get_current_user)],
):
    """ Get 1 node by id """
    # TODO fix it
    db_nodes = [item for item in user.nodes if item.id == node_id]
    if not db_nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    return db_nodes[0]


@router.get("/{node_id}/current-values", response_model=schemas.NodeCurrentValues)
def get_node_current_values(
        node_id: int,
        user: Annotated[models.User, Depends(get_current_user)],
):
    """ Get current values of node by id """
    # TODO fix it
    db_nodes = [item for item in user.nodes if item.id == node_id]
    if not db_nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    db_node = db_nodes[0]

    db_current_values = db_node.current_values

    return dict(data=db_current_values)
