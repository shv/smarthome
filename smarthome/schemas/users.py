"""
User schemas
"""
from pydantic import BaseModel


class UserBase(BaseModel):
    """ Base user schema """
    email: str


class UserCreate(UserBase):
    """ Create user schema """
    password: str


class User(UserBase):
    """ Read user schema """
    id: int
    is_active: bool

    class ConfigDict:
        """ Config """
        from_attributes = True
