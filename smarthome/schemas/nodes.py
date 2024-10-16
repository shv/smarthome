"""
Node schemas
"""
from typing import Any
from pydantic import BaseModel, field_validator


class NodeBase(BaseModel):
    """ Base node schema """
    is_active: bool
    url: str


class Node(NodeBase):
    """ Read node schema """
    id: int

    class ConfigDict:
        """ Config """
        from_attributes = True


class Nodes(BaseModel):
    """ Read node list schema """
    nodes: list[Node]

    class ConfigDict:
        """ Config """
        from_attributes = True


# class NodeStateBase(BaseModel):
#     """ Base node schema """
#     is_active: bool
#     url: str
#
#
# class NodeStateCreate(NodeBase):
#     """ Read node schema """
#     id: int
#
#     class ConfigDict:
#         """ Config """
#         from_attributes = True


class NodeStateCreate(BaseModel):
    data: dict
    node_id: int

    class ConfigDict:
        """ Config """
        from_attributes = True


class NodeCurrentValue(BaseModel):
    """ Read node current value schema """
    id: int
    name: str
    value: Any

    @field_validator("value", mode="before")
    @classmethod
    def transform(cls, raw: dict) -> Any:
        return raw.get("value")

    class ConfigDict:
        """ Config """
        from_attributes = True


class NodeCurrentValues(BaseModel):
    """ Read node list schema """
    data: list[NodeCurrentValue]

    class ConfigDict:
        """ Config """
        from_attributes = True


class NodeLamp(BaseModel):
    """ Read node lamp schema """
    id: int
    name: str
    value: int

    class ConfigDict:
        """ Config """
        from_attributes = True


class NodeLamps(BaseModel):
    """ Read lamp list schema """
    data: list[NodeLamp]

    class ConfigDict:
        """ Config """
        from_attributes = True


class NodeSensor(BaseModel):
    """ Read node sensor schema """
    id: int
    name: str
    value: float

    class ConfigDict:
        """ Config """
        from_attributes = True


class NodeSensors(BaseModel):
    """ Read sensor list schema """
    data: list[NodeSensor]

    class ConfigDict:
        """ Config """
        from_attributes = True


class NodeCurrentValueCreate(BaseModel):
    name: str
    value: Any

    class ConfigDict:
        """ Config """
        from_attributes = True