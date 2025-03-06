"""
Browser APIs with Nodes.

This module provides API endpoints for browser clients to interact with nodes,
including retrieving node information, lamp states, sensor data, and sensor history.
"""
import datetime
from typing import Annotated, Literal, TypedDict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from smarthome import models, schemas
from smarthome.auth import get_current_user
from smarthome.cruds import get_aggregated_sensor_history_data
from smarthome.depends import get_db
from smarthome.settings import settings
from smarthome.logger import logger

router = APIRouter(
    prefix=settings.main_url
)


@router.get("/", response_model=schemas.Nodes)
def get_nodes(
        user: Annotated[models.User, Depends(get_current_user)],
) -> dict[str, list[models.Node]]:
    """
    Get all nodes associated with the authenticated user.
    
    Args:
        user: The authenticated user from the dependency.
        
    Returns:
        A dictionary containing the list of nodes.
    """
    db_nodes = user.nodes
    return {"nodes": db_nodes}


@router.get("/{node_id}", response_model=schemas.Node)
def get_node(
        node_id: int,
        user: Annotated[models.User, Depends(get_current_user)],
) -> models.Node:
    """
    Get a specific node by its ID.
    
    Args:
        node_id: The ID of the node to retrieve.
        user: The authenticated user from the dependency.
        
    Returns:
        The requested node.
        
    Raises:
        HTTPException: If the node is not found or doesn't belong to the user.
    """
    # TODO: Replace with a more efficient database query
    db_nodes = [item for item in user.nodes if item.id == node_id]
    if not db_nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    return db_nodes[0]


@router.get("/{node_id}/lamps", response_model=schemas.NodeLamps)
def get_node_lamps(
        node_id: int,
        user: Annotated[models.User, Depends(get_current_user)],
) -> dict[str, list[models.NodeLamp]]:
    """
    Get all lamps associated with a specific node.
    
    Args:
        node_id: The ID of the node to retrieve lamps from.
        user: The authenticated user from the dependency.
        
    Returns:
        A dictionary containing the list of lamps.
        
    Raises:
        HTTPException: If the node is not found or doesn't belong to the user.
    """
    # TODO: Replace with a more efficient database query
    db_nodes = [item for item in user.nodes if item.id == node_id]
    if not db_nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    db_node = db_nodes[0]
    db_lamps = db_node.lamps

    return {"data": db_lamps}


@router.get("/{node_id}/sensors", response_model=schemas.NodeSensors)
def get_node_sensors(
        node_id: int,
        user: Annotated[models.User, Depends(get_current_user)],
) -> dict[str, list[models.NodeSensor]]:
    """
    Get all sensors associated with a specific node.
    
    Args:
        node_id: The ID of the node to retrieve sensors from.
        user: The authenticated user from the dependency.
        
    Returns:
        A dictionary containing the list of sensors.
        
    Raises:
        HTTPException: If the node is not found or doesn't belong to the user.
    """
    # TODO: Replace with a more efficient database query
    db_nodes = [item for item in user.nodes if item.id == node_id]
    if not db_nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    db_node = db_nodes[0]
    db_sensors = db_node.sensors

    return {"data": db_sensors}


@router.get("/{node_id}/sensors/{sensor_id}", response_model=schemas.NodeSensor)
def get_node_sensor(
        node_id: int,
        sensor_id: int,
        user: Annotated[models.User, Depends(get_current_user)],
) -> models.NodeSensor:
    """
    Get a specific sensor by its ID from a specific node.
    
    Args:
        node_id: The ID of the node.
        sensor_id: The ID of the sensor to retrieve.
        user: The authenticated user from the dependency.
        
    Returns:
        The requested sensor.
        
    Raises:
        HTTPException: If the node or sensor is not found.
    """
    # TODO: Replace with a more efficient database query
    db_nodes = [item for item in user.nodes if item.id == node_id]
    if not db_nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    db_node = db_nodes[0]

    db_sensors = [item for item in db_node.sensors if item.id == sensor_id]
    if not db_sensors:
        raise HTTPException(status_code=404, detail="Sensor not found")

    return db_sensors[0]


class HistoryResponseItem(TypedDict):
    """Type definition for a single history data point."""
    period: str
    max_value: float
    min_value: float
    avg_value: float


class HistoryResponse(TypedDict):
    """Type definition for the complete history response."""
    data: list[HistoryResponseItem]
    start_date: datetime.datetime
    end_date: datetime.datetime
    group_by: Literal["minute", "hour", "day", "month"]


@router.get("/{node_id}/sensors/{sensor_id}/history", response_model=schemas.NodeSensorAggregateHistoryList)
def get_node_sensor_history(
        node_id: int,
        sensor_id: int,
        user: Annotated[models.User, Depends(get_current_user)],
        db: Session = Depends(get_db),
        start_date: datetime.datetime | None = Query(
            None,
            description="Дата и время начала в формате YYYY-MM-DDTHH:MM:SS",
        ),
        end_date: datetime.datetime | None = Query(
            None,
            description="Дата и время окончания в формате YYYY-MM-DDTHH:MM:SS",
        ),
        group_by: Literal["minute", "hour", "day", "month"] = Query(
            "hour",
            description="Вариант группировки (minute, hour, day, month)"
        ),
) -> HistoryResponse:
    """
    Get historical sensor data with aggregation.
    
    Args:
        node_id: The ID of the node.
        sensor_id: The ID of the sensor to retrieve history for.
        user: The authenticated user from the dependency.
        db: Database session.
        start_date: Optional start date for the history query.
        end_date: Optional end date for the history query.
        group_by: Aggregation period (minute, hour, day, month).
        
    Returns:
        A dictionary containing the aggregated sensor history data.
        
    Raises:
        HTTPException: If the node or sensor is not found.
    """
    # TODO: Replace with a more efficient database query
    db_nodes = [item for item in user.nodes if item.id == node_id]
    if not db_nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    db_node = db_nodes[0]

    db_sensors = [item for item in db_node.sensors if item.id == sensor_id]
    if not db_sensors:
        raise HTTPException(status_code=404, detail="Sensor not found")

    db_sensor = db_sensors[0]

    if not start_date:
        start_date = datetime.datetime.now() - datetime.timedelta(hours=24)
    if not end_date:
        end_date = datetime.datetime.now() + datetime.timedelta(hours=1)

    sensor_history = get_aggregated_sensor_history_data(db, db_sensor.id, start_date, end_date, group_by=group_by)
    logger.debug("Raw history: %s", sensor_history)
    history_response: list[HistoryResponseItem] = [
        {
            "period": str(item[0].replace(tzinfo=datetime.timezone.utc)),
            "max_value": round(item[1], 2),
            "min_value": round(item[2], 2),
            "avg_value": round(item[3], 2),
        } for item in sensor_history
    ]
    logger.debug("History response: %s", history_response)

    return {
        "data": history_response,
        "start_date": start_date,
        "end_date": end_date,
        "group_by": group_by,
    }
