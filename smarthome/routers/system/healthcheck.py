"""
Healthcheck endpoints
"""
from fastapi import APIRouter
from smarthome.settings import settings
from smarthome.schemas import Status

router = APIRouter(
    prefix=settings.main_url
)


@router.get("/status")
async def status():
    """ Status endpoint """
    return Status()
