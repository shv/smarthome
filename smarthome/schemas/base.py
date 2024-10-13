from typing import Any
from pydantic import BaseModel


class ListResponse(BaseModel):
    """ Read list schema """
    data: list[Any]

    class ConfigDict:
        """ Config """
        from_attributes = True
