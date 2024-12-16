"""
Browser APIs with Nodes
"""
import datetime
from typing import Annotated, Literal
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
):
    """ Get user nodes endpoint """
    db_nodes = user.nodes
    return dict(nodes=db_nodes)


@router.get("/{node_id}", response_model=schemas.Node)
def get_node(
        node_id: int,
        user: Annotated[models.User, Depends(get_current_user)],
):
    """ Get 1 node by id """
    # TODO fix it
    db_nodes = [item for item in user.nodes if item.id == node_id]
    if not db_nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    return db_nodes[0]


@router.get("/{node_id}/lamps", response_model=schemas.NodeLamps)
def get_node_lamps(
        node_id: int,
        user: Annotated[models.User, Depends(get_current_user)],
):
    """ Get current values of node by id """
    # TODO fix it
    db_nodes = [item for item in user.nodes if item.id == node_id]
    if not db_nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    db_node = db_nodes[0]

    db_lamps = db_node.lamps

    return dict(data=db_lamps)


@router.get("/{node_id}/sensors", response_model=schemas.NodeSensors)
def get_node_sensors(
        node_id: int,
        user: Annotated[models.User, Depends(get_current_user)],
):
    """ Get current values of node by id """
    # TODO fix it
    db_nodes = [item for item in user.nodes if item.id == node_id]
    if not db_nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    db_node = db_nodes[0]

    db_sensors = db_node.sensors

    return dict(data=db_sensors)


@router.get("/{node_id}/sensors/{sensor_id}", response_model=schemas.NodeSensor)
def get_node_sensor(
        node_id: int,
        sensor_id: int,
        user: Annotated[models.User, Depends(get_current_user)],
):
    """ Get sensor data of node by sensor id """
    # TODO fix it
    db_nodes = [item for item in user.nodes if item.id == node_id]
    if not db_nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    db_node = db_nodes[0]

    db_sensors = [item for item in db_node.sensors if item.id == sensor_id]
    if not db_sensors:
        raise HTTPException(status_code=404, detail="Node not found")

    return db_sensors[0]


@router.get("/{node_id}/sensors/{sensor_id}/history", response_model=schemas.NodeSensorAggregateHistoryList)
def get_node_sensor_history(
        node_id: int,
        sensor_id: int,
        user: Annotated[models.User, Depends(get_current_user)],
        db: Session = Depends(get_db),
        start_date: datetime.datetime = Query(
            datetime.datetime.now() - datetime.timedelta(hours=24),
            description="Дата начала в формате YYYY-MM-DD",
        ),
        end_date: datetime.datetime = Query(
            datetime.datetime.now() + datetime.timedelta(hours=1),
            description="Дата окончания в формате YYYY-MM-DD",
        ),
        group_by: Literal["minute", "hour", "day", "month"] = Query(
            "hour",
            description="Вариант группировки (minute, hour, day, month)"
        ),
):
    """ Get history values of node by sensor_id """
    # TODO fix it
    db_nodes = [item for item in user.nodes if item.id == node_id]
    if not db_nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    db_node = db_nodes[0]

    db_sensors = [item for item in db_node.sensors if item.id == sensor_id]
    if not db_sensors:
        raise HTTPException(status_code=404, detail="Node not found")

    db_sensor = db_sensors[0]

    # start_date = datetime.datetime.now() - datetime.timedelta(hours=24)
    # end_date = datetime.datetime.now() + datetime.timedelta(hours=1)

    sensor_history = get_aggregated_sensor_history_data(db, db_sensor.id, start_date, end_date, group_by=group_by)
    logger.debug("Raw history: %s", sensor_history)
    history_response = [
        {
            "period": str(item[0].replace(tzinfo=datetime.timezone.utc)),
            "max_value": round(item[1], 2),
            "min_value": round(item[2], 2),
            "avg_value": round(item[3], 2),
        } for item in sensor_history
    ]
    logger.debug("History response: %s", history_response)

    return dict(
        data=history_response,
        start_date=start_date,
        end_date=end_date,
        group_by=group_by,
    )
