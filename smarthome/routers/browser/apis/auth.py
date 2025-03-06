"""
Browser authentication endpoints for handling user sessions and tokens.
"""
from typing import Annotated
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
) -> schemas.Token:
    """
    Generate token for websocket connection.
    
    Args:
        user: Authenticated user from dependency
        db: Database session
    
    Returns:
        Token object for the authenticated user
    """
    logger.debug("Get token for user: %s", user)
    return cruds.get_token_by_user_id(db, user_id=user.id)


@router.post("/login", response_model=schemas.Status)
async def login(
        login_data: schemas.UserCreate,
        response: Response,
        session: Annotated[str | None, Cookie()] = None,
        db: Session = Depends(get_db)
) -> schemas.Status:
    """
    Authenticate user and set session cookie.
    
    Args:
        login_data: User credentials
        response: FastAPI response object for setting cookies
        session: Current session cookie if exists
        db: Database session
    
    Returns:
        Status object indicating success
    
    Raises:
        HTTPException: If authentication fails
    """
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
        max_age=60 * 60 * 24 * 365,  # Cookie will be valid for 365 days
        httponly=True,  # Only accessible via HTTP (not via JavaScript)
        # secure=True,  # Only works via HTTPS (if your site uses HTTPS)
        # samesite="lax"  # SameSite policy for CSRF protection
    )

    return schemas.Status()


@router.get("/logout", response_model=schemas.Status)
async def logout(
        response: Response,
        session: Annotated[str | None, Cookie()] = None,
        db: Session = Depends(get_db)
) -> schemas.Status:
    """
    Log out user by deleting session token and cookie.
    
    Args:
        response: FastAPI response object for deleting cookies
        session: Current session cookie if exists
        db: Database session
    
    Returns:
        Status object indicating success
    """
    if session:
        logger.debug("Find session: %s", session)
        db_token = cruds.get_token_by_token(db, token=session)
        if db_token:
            db.delete(db_token)
            db.commit()

        response.delete_cookie("session")

    return schemas.Status()
