"""
Websocket messages schemas
"""
from enum import Enum
from pydantic import BaseModel


class WSActions(str, Enum):
    get_data = 'get_data'  # Запрос на получение данных
    connect = 'connect'  # Подключение клиента
    disconnect = 'disconnect'  # Отключение клиента
    put_data = 'put_data'  # Отправка данных


class WSMessage(BaseModel):
    """ Websocket message schema """
    request_id: str  # Unique request identifier
    action: WSActions
    data: dict | None = None
