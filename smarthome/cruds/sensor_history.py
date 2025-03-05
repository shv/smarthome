"""
Sensor history CRUD operations.

This module provides functions for retrieving and manipulating sensor history data.
"""
from datetime import datetime
from typing import Any, Literal, Sequence

from sqlalchemy import func
from sqlalchemy.orm import Session

from smarthome import models


def get_aggregated_sensor_history_data(
    db: Session,
    sensor_id: int,
    start_date: datetime,
    end_date: datetime,
    group_by: Literal["minute", "hour", "day", "month"] = "hour",
) -> Sequence[Any]:
    """
    Retrieve aggregated sensor history data grouped by time period.
    
    Args:
        db: Database session
        sensor_id: ID of the sensor to retrieve history for
        start_date: Start date for the history range
        end_date: End date for the history range
        group_by: Time period to group by (minute, hour, day, or month)
        
    Returns:
        Sequence of aggregated sensor history records with period, max_value, min_value, and avg_value
        
    Raises:
        ValueError: If an invalid group_by value is provided
    """
    # Define grouping
    if group_by == "minute":
        group_field = func.date_trunc("minute", models.NodeSensorHistory.changed)
    elif group_by == "hour":
        group_field = func.date_trunc("hour", models.NodeSensorHistory.changed)
    elif group_by == "day":
        group_field = func.date_trunc("day", models.NodeSensorHistory.changed)
    elif group_by == "month":
        group_field = func.date_trunc("month", models.NodeSensorHistory.changed)
    else:
        raise ValueError("Invalid group_by value. Use minute, hour, day, or month.")

    # Build query
    query = (
        db.query(
            group_field.label("period"),
            func.max(models.NodeSensorHistory.value).label("max_value"),
            func.min(models.NodeSensorHistory.value).label("min_value"),
            func.avg(models.NodeSensorHistory.value).label("avg_value"),
        )
        .filter(
            models.NodeSensorHistory.changed.between(start_date, end_date),
            models.NodeSensorHistory.sensor_id == sensor_id,
        )
        .group_by(group_field)
        .order_by(group_field)
    )

    return query.all()
