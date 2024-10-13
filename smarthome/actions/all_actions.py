from typing import Annotated

from abc import ABC, abstractmethod
from fastapi import Depends
from sqlalchemy.orm import Session

from smarthome import cruds, models, schemas
from smarthome.depends import get_db
from smarthome.connectors.bus import Bus, get_bus
from smarthome.logger import logger
from smarthome.schemas.ws import WSMessage


class BaseAction(ABC):
    """ Если наследовать классы от этого класса, то можно автоматически собирать все экшны """
    def __init__(self, client: models.Node | models.User, bus: Bus, db: Session):
        if isinstance(client, models.Node):
            self.node = client
        elif isinstance(client, models.User):
            self.user = client
        self.bus = bus
        self.db = db

    @abstractmethod
    async def process(self, data: dict):
        """ Нужно переопределить в каждом наследнике """


class ActionPutDataFromNode(BaseAction):
    """
    Получение данных от ноды.
    Класс привязывается к клиенту (ноде или пользователю)
    """

    async def process(self, data: dict):
        """
        Пока условно формат данных от ноды - json с параметрами в корне
        """
        logger.info("DATA from ESP32 #%s: %s", self.node.id, data)

        # Сюда пишем полный ответ ноды
        cruds.create_node_state(self.db, schemas.NodeStateCreate(data=data, node_id=self.node.id))

        for key, value in data.items():
            cruds.upsert_node_current_values(
                self.db, self.node.id,
                schemas.NodeCurrentValueCreate(name=key, value=value),
            )

        logger.info("DATA from ESP32 #%s received", self.node.id)

        users = self.node.users

        for user in users:
            ws_message = WSMessage(
                request_id="1",
                action="put_data",
                data=data,
            )
            logger.info("ActionPutData from Node %s to user %s Message: %s", self.node.id, user.id, ws_message)
            await self.bus.publish(user.bus_id, ws_message)


class ActionResolver:
    """ Singleton через Depends """
    def __init__(self, db: Session, bus: Bus):
        self.db = db
        self.bus = bus

    async def process(self, client: models.Node | models.User, ws_message: WSMessage) -> None:
        """
        Обработка экшнов от вебсокетов нод и пользователей
        :param client: пользователь или нода - инициатор экшна
        :param ws_message:
        :return:
        """
        # Маппер экшнов. По экшну из сообщения выбирает класс экшна
        action_map = {
            "put_data": ActionPutDataFromNode,
        }

        action_class = action_map[ws_message.action]
        logger.info("ActionResolver %s Message: %s", action_class, ws_message)

        try:
            await action_class(client=client, bus=self.bus, db=self.db).process(data=ws_message.data)
        except AttributeError as ex:
            logger.exception("Failed process in action %s: %s", action_class, ex)


async def get_action_resolver(db: Session = Depends(get_db), bus: Bus = Depends(get_bus)) -> ActionResolver:
    """ Только через Depends """
    action_resolver = ActionResolver(db=db, bus=bus)
    return action_resolver
