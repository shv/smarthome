from typing import Annotated, Union
from fastapi import Depends, WebSocketException, Cookie, status, Query
from sqlalchemy.orm import Session

from smarthome import cruds, models
from smarthome.depends import get_db
from smarthome.logger import logger


async def get_current_user(
    session: Annotated[Union[str, None], Cookie()] = None,
    token: Annotated[Union[str, None], Query()] = None,
    db: Session = Depends(get_db),
) -> models.User:
    """ Get current user from token dependency """
    # TODO сделать универсальным, а не только для вебсокета
    logger.info("Session: %s, token: %s", session, token)
    if session is None and token is None:
        logger.warning("No user")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    token = token if token else session

    if token:
        user = await cruds.get_user_by_token(db=db, token=token)
        logger.info("User: %s", user)
        if user:
            return user

    logger.info("User not found")
    raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)


async def get_current_node(
    token: Annotated[Union[str, None], Query()] = None,
    db: Session = Depends(get_db),
) -> models.User:
    """ Get current node from token dependency """
    # TODO сделать универсальным, а не только для вебсокета
    logger.info("Session: token: %s", token)
    if token is None:
        logger.warning("No token")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    node = await cruds.get_node_by_token(db=db, token=token)
    logger.info("Node: %s", node)
    if node:
        return node

    logger.info("Node not found")
    raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)