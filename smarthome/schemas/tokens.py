"""
Token schemas
"""
from pydantic import BaseModel


class Token(BaseModel):
    """ Read token schema """
    token: str
    user_id: int

    class ConfigDict:
        """ Config """
        from_attributes = True
