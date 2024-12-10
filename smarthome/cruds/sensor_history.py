"""
Sensor history CRUD
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from smarthome import models


def get_aggregated_sensor_history_data(db: Session, sensor_id: int, start_date, end_date, group_by="hour"):
    # Определяем группировку
    if group_by == "minute":
        group_field = func.date_trunc("minute", models.NodeSensorHistory.changed)
    elif group_by == "hour":
        group_field = func.date_trunc("hour", models.NodeSensorHistory.changed)
    elif group_by == "day":
        group_field = func.date_trunc("day", models.NodeSensorHistory.changed)
    elif group_by == "month":
        group_field = func.date_trunc("month", models.NodeSensorHistory.changed)
    else:
        raise ValueError("Invalid group_by value. Use hour, day, or month.")

    # Формируем запрос
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
