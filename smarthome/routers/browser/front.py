"""
Browser endpoints with html for front pages
"""
from typing import Annotated, Union
from fastapi import APIRouter, Cookie, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

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


@router.get("/login", response_class=HTMLResponse)
async def login(
        request: Request,
        session: Annotated[Union[str, None], Cookie()] = None,
):
    # No auth
    return templates.TemplateResponse("login.html", {"request": request, "session": session})


@router.get("/nodes", response_class=HTMLResponse)
async def nodes(
        request: Request,
        # TODO выделить проверку в отдельный метод для http
        # user: Annotated[models.User, Depends(get_current_user)],
        session: Annotated[Union[str, None], Cookie()] = None,
):
    # Need auth
    return templates.TemplateResponse("nodes.html", {"request": request, "session": session})


@router.get("/nodes/{node_id}", response_class=HTMLResponse)
async def node(
        node_id: int,
        request: Request,
        # TODO выделить проверку в отдельный метод для http
        # user: Annotated[models.User, Depends(get_current_user)],
        session: Annotated[Union[str, None], Cookie()] = None,
):
    # Need auth
    return templates.TemplateResponse("node.html", {"request": request, "session": session, "node_id": node_id})


@router.get("/nodes/{node_id}/sensors/{sensor_id}", response_class=HTMLResponse)
async def node_sensor(
        node_id: int,
        sensor_id: int,
        request: Request,
        # TODO выделить проверку в отдельный метод для http
        # user: Annotated[models.User, Depends(get_current_user)],
        session: Annotated[Union[str, None], Cookie()] = None,
):
    # Need auth
    return templates.TemplateResponse("node_sensor.html", {
        "request": request, "session": session, "node_id": node_id, "sensor_id": sensor_id
    })
