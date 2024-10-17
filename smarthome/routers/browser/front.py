"""
Browser endpoints with html for front pages
"""
from typing import Annotated, Union
import uuid
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from smarthome import cruds, models, schemas
from smarthome.auth import get_current_user
from smarthome.depends import get_db
from smarthome.logger import logger

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def index(
        request: Request,
        session: Annotated[Union[str, None], Cookie()] = None,
):
    # No auth
    return templates.TemplateResponse("index.html", {"request": request, "session": session})


@router.get("/node-ws-test", response_class=HTMLResponse)
async def node_test_index(
        request: Request,
        token: Annotated[Union[str, None], Query()] = None,
):
    # No auth
    return templates.TemplateResponse("test_node_ws.html", {"request": request, "session": token})


@router.get("/nodes", response_class=HTMLResponse)
async def nodes(
        request: Request,
        # user: Annotated[models.User, Depends(get_current_user)],
        session: Annotated[Union[str, None], Cookie()] = None,
):
    # Need auth
    return templates.TemplateResponse("nodes.html", {"request": request, "session": session})


@router.get("/nodes/{node_id}", response_class=HTMLResponse)
async def nodes(
        node_id: int,
        request: Request,
        # user: Annotated[models.User, Depends(get_current_user)],
        session: Annotated[Union[str, None], Cookie()] = None,
):
    # Need auth
    return templates.TemplateResponse("node.html", {"request": request, "session": session, "node_id": node_id})


@router.get("/login", response_class=HTMLResponse)
async def login(
        request: Request,
        session: Annotated[Union[str, None], Cookie()] = None,
):
    # No auth
    return templates.TemplateResponse("login.html", {"request": request, "session": session})


@router.post("/login", response_model=schemas.Status)
async def login_redirect(
        login_data: schemas.UserCreate,
        response: Response,
        session: Annotated[Union[str, None], Cookie()] = None,
        db: Session = Depends(get_db)
):
    # No auth
    if session:
        logger.info("Find session: %s", session)
        db_token = cruds.get_token_by_token(db, token=session)

        if db_token:
            logger.info("Find token: %s", db_token)
            return schemas.Status()

        logger.info("Session deleted")

    db_user = cruds.get_user_by_email(db, email=login_data.email)
    logger.info("Find db_user: %s by email %s", db_user, login_data.email)
    if not db_user:
        logger.info("No found db_user: %s", login_data.email)
        raise HTTPException(status_code=403, detail="Wrong email or password")

    db_token = cruds.get_token_by_user_id(db=db, user_id=db_user.id)
    logger.info("Find token: %s", db_token)

    if not db_token:
        token = uuid.uuid4().hex
        db_token = cruds.create_token(db=db, user_id=db_user.id, token=token)
        logger.info("Token %s generated: %s", token, db_token)

    response.set_cookie(
        key="session",
        value=db_token.token,
        max_age=60 * 60 * 24 * 365,  # Кука будет действовать 7 дней
        httponly=True,  # Доступно только через HTTP (невозможно получить через JavaScript)
        # secure=True,  # Работает только через HTTPS (если ваш сайт использует HTTPS)
        # samesite="lax"  # Политика SameSite для защиты от CSRF-атак
    )

    return schemas.Status()


@router.get("/token", response_model=schemas.Token)
def get_token(
        user: Annotated[models.User, Depends(get_current_user)],
        # session: Annotated[Union[str, None], Cookie()] = None,
        db: Session = Depends(get_db)
):
    """ Generate token for websocket connection """
    # Need auth
    logger.info("Get token for user: %s", user)
    return cruds.get_token_by_user_id(db, user_id=user.id)
    # return cruds.get_token_by_token(db, token=session)
