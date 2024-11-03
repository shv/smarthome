"""
Websocket messages schemas
"""
from enum import Enum
from pydantic import BaseModel


class WSActions(str, Enum):
    get_data = 'get_data'  # Запрос на получение данных
    connect = 'connect'  # Подключение клиента
    disconnect = 'disconnect'  # Отключение клиента
    # put_data = 'put_data'  # Отправка данных
    current_values = "updated_values"  # Текущие значения
    send_lamps_state_to_nodes = "send_lamps_state_to_nodes"  # Отпарвка нового состояния ламп на ноды
    set_lamp_state = "set_lamp_state"  # Установка состояния ламп в ноде
    lamp_changed = "lamp_changed"  # Получено новое состояния ламп от ноды
    updated_lamp = "updated_lamp"  # Сообщение юзеру об обновлении лампы
    sensor_changed = "sensor_changed"  # Получено новое состояние значений сенсоров
    updated_sensor = "updated_sensor"  # Сообщение юзеру об обновлении сенсора
    updated_node = "updated_node"  # Сообщение юзеру об обновлении ноды
    restart = "restart"  # Перезагрузка ноды
    restart_node = "restart_node"  # Перезагрузка ноды, команда от клиента


class WSMessage(BaseModel):
    """ Websocket message schema """
    request_id: str  # Unique request identifier
    action: WSActions
    data: dict | None = None
