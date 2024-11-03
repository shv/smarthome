from typing import Annotated, Union
from fastapi import Cookie, Depends, HTTPException, Query, Response, status, WebSocketException
from sqlalchemy.orm import Session

from smarthome import cruds, models
from smarthome.depends import get_db
from smarthome.logger import logger


class AuthError(Exception):
    pass


async def _get_current_user(
    session: Annotated[Union[str, None], Cookie()] = None,
    token: Annotated[Union[str, None], Query()] = None,
    db: Session = Depends(get_db),
) -> models.User:
    """ Get current user from token dependency """
    # TODO сделать универсальным, а не только для вебсокета
    logger.debug("Session: %s, token: %s", session, token)
    if session is None and token is None:
        logger.warning("No user")
        raise AuthError("No user")

    token = token if token else session

    if token:
        user = await cruds.get_user_by_token(db=db, token=token)
        logger.debug("User: %s", user)
        if user:
            return user

    logger.info("User not found")
    raise AuthError("No user")


async def get_current_user(
    response: Response,
    session: Annotated[Union[str, None], Cookie()] = None,
    token: Annotated[Union[str, None], Query()] = None,
    db: Session = Depends(get_db),
) -> models.User:
    try:
        result = await _get_current_user(session, token, db)
    except AuthError as ex:
        exception_params = {}
        if session:
            response.delete_cookie("session")
            exception_params["headers"] = {"set-cookie": response.headers["set-cookie"]}
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, **exception_params) from ex
    return result


async def get_current_user_for_ws(
    session: Annotated[Union[str, None], Cookie()] = None,
    token: Annotated[Union[str, None], Query()] = None,
    db: Session = Depends(get_db),
) -> models.User:
    """ Для вебсокета """
    try:
        result = await _get_current_user(session, token, db)
    except AuthError as ex:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION) from ex
    return result


async def get_current_node_for_ws(
    token: Annotated[Union[str, None], Query()] = None,
    db: Session = Depends(get_db),
) -> models.User:
    """ Get current node from token dependency """
    # TODO сделать универсальным, а не только для вебсокета
    logger.debug("Session: token: %s", token)
    if token is None:
        logger.warning("No token")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    node = await cruds.get_node_by_token(db=db, token=token)
    logger.debug("Node: %s", node)
    if node:
        return node

    logger.info("Node not found")
    raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)