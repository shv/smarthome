from pydantic import BaseModel


class Status(BaseModel):
    """ Status result """
    status: str = "ok"
