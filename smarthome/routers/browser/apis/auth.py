"""
Browser endpoints with html for front pages
"""
from typing import Annotated, Union
import uuid
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from smarthome import cruds, models, schemas
from smarthome.auth import get_current_user
from smarthome.depends import get_db
from smarthome.logger import logger

router = APIRouter()


@router.get("/token", response_model=schemas.Token)
def get_token(
        user: Annotated[models.User, Depends(get_current_user)],
        db: Session = Depends(get_db)
):
    """ Generate token for websocket connection """
    # Need auth
    logger.debug("Get token for user: %s", user)
    return cruds.get_token_by_user_id(db, user_id=user.id)


@router.post("/login", response_model=schemas.Status)
async def login(
        login_data: schemas.UserCreate,
        response: Response,
        session: Annotated[Union[str, None], Cookie()] = None,
        db: Session = Depends(get_db)
):
    # No auth
    if session:
        logger.debug("Find session: %s", session)
        db_token = cruds.get_token_by_token(db, token=session)

        if db_token:
            logger.debug("Find token: %s", db_token)
            return schemas.Status()

        logger.debug("Session deleted")

    db_user = cruds.get_user_by_email(db, email=login_data.email)
    logger.debug("Find db_user: %s by email %s", db_user, login_data.email)
    if not db_user:
        logger.debug("No found db_user: %s", login_data.email)
        raise HTTPException(status_code=403, detail="Wrong email or password")

    db_token = cruds.get_token_by_user_id(db=db, user_id=db_user.id)
    logger.debug("Find token: %s", db_token)

    if not db_token:
        token = uuid.uuid4().hex
        db_token = cruds.create_token(db=db, user_id=db_user.id, token=token)
        logger.debug("Token %s generated: %s", token, db_token)

    response.set_cookie(
        key="session",
        value=db_token.token,
        max_age=60 * 60 * 24 * 365,  # Кука будет действовать 7 дней
        httponly=True,  # Доступно только через HTTP (невозможно получить через JavaScript)
        # secure=True,  # Работает только через HTTPS (если ваш сайт использует HTTPS)
        # samesite="lax"  # Политика SameSite для защиты от CSRF-атак
    )

    return schemas.Status()


@router.get("/logout", response_model=schemas.Status)
async def logout(
        response: Response,
        session: Annotated[Union[str, None], Cookie()] = None,
        db: Session = Depends(get_db)
):
    # No auth
    if session:
        logger.debug("Find session: %s", session)
        db_token = cruds.get_token_by_token(db, token=session)
        if db_token:
            db.delete(db_token)

        response.delete_cookie("session")
        return schemas.Status()
