"""
DRAFT
Equipment Router. Sensors, executors, switches
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from smarthome.depends import get_db
from smarthome.settings import settings

router = APIRouter(
    prefix=settings.main_url
)


@router.get("/state/")
def get_state(db: Session = Depends(get_db)):
    """ Create user endpoint """
    # db_user = cruds.get_user_by_email(db, email=user.email)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Email already registered")
    # return cruds.create_user(db=db, user=user)
    return {}


@router.put("/state/")
def save_state(db: Session = Depends(get_db)):
    """ Save new data """
    # db_user = cruds.get_user_by_email(db, email=user.email)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Email already registered")
    # return cruds.create_user(db=db, user=user)
    return {}
