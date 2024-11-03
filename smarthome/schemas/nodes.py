"""
Node schemas
"""
from pydantic import BaseModel
from datetime import datetime


class Node(BaseModel):
    """ Read node schema """
    id: int
    is_active: bool
    is_online: bool
    url: str

    class ConfigDict:
        """ Config """
        from_attributes = True


class Nodes(BaseModel):
    """ Read node list schema """
    nodes: list[Node]

    class ConfigDict:
        """ Config """
        from_attributes = True


# Лампы
class NodeLamp(BaseModel):
    """ Read node lamp schema """
    id: int
    name: str
    value: int
    updated: datetime | None

    class ConfigDict:
        """ Config """
        from_attributes = True


class NodeLamps(BaseModel):
    """ Read lamp list schema """
    data: list[NodeLamp]

    class ConfigDict:
        """ Config """
        from_attributes = True


# Сенсоры
class NodeSensor(BaseModel):
    """ Read node sensor schema """
    id: int
    name: str
    value: float
    updated: datetime | None

    class ConfigDict:
        """ Config """
        from_attributes = True


class NodeSensors(BaseModel):
    """ Read sensor list schema """
    data: list[NodeSensor]

    class ConfigDict:
        """ Config """
        from_attributes = True
