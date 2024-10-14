from typing import Annotated

from abc import ABC, abstractmethod
from fastapi import Depends
from sqlalchemy.orm import Session

from smarthome import cruds, models, schemas
from smarthome.depends import get_db
from smarthome.connectors.bus import Bus, get_bus
from smarthome.logger import logger
from smarthome.schemas.ws import WSMessage
from smarthome.schemas.nodes import NodeCurrentValue, NodeCurrentValues



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
    Класс привязывается к ноде
    """

    async def process(self, data: dict):
        """
        Пока условно формат данных от ноды - json с параметрами в корне
        """
        logger.info("DATA from ESP32 #%s: %s", self.node.id, data)

        # Сюда пишем полный ответ ноды
        cruds.create_node_state(self.db, schemas.NodeStateCreate(data=data, node_id=self.node.id))

        current_values = []
        for key, value in data.items():
            current_value = cruds.upsert_node_current_values(
                self.db, self.node.id,
                schemas.NodeCurrentValueCreate(name=key, value=value),
            )
            current_values.append(NodeCurrentValue(
                id=current_value.id,
                name=current_value.name,
                value=current_value.value,
            ).model_dump())

        logger.info("DATA from ESP32 #%s received", self.node.id)

        users = self.node.users

        for user in users:
            ws_message = WSMessage(
                request_id="1",
                action="updated_values",
                data={"current_values": current_values},
            )
            logger.info("ActionPutData from Node %s to user %s Message: %s", self.node.id, user.id, ws_message)
            await self.bus.publish(user.bus_id, ws_message)


class ActionSendLampsStateToNodes(BaseAction):
    """
    Управление лампой юзером на нодах.
    Класс привязывается к пользователю
    """

    async def process(self, data: dict):
        """
        Получаем лампу и значение
        {"lamps": [{"id": 1, "value": 0}]}
        где id - это идентификатор лампы в базе

        Отправляем в ноду по каждой лампе:
        {"id": 1, "value": 0}
        где id - это внутренний идентификатор лампы внутри ноды
        """
        logger.info("DATA from User #%s: %s", self.user.id, data)
        for lamp in data["lamps"]:
            db_lamp = self.db.query(models.NodeLamp).filter(models.NodeLamp.id == lamp["id"]).first()
            logger.info("Lamp from db: %s", db_lamp)
            if not db_lamp:
                logger.warning("Lamp %s not found in db", lamp["id"])
                continue

            db_node = db_lamp.node
            logger.info("Node for lamp %s: %s", db_lamp, db_node)
            if self.user not in db_node.users:
                logger.error("Lamp %s is not connected to user %s", db_lamp, self.user)
                continue

            ws_message = WSMessage(
                request_id="1",
                action="set_lamp_state",
                data={"id": db_lamp.node_lamp_id, "value": lamp["value"]},
            )
            logger.info("ActionSendLampsStateToNodes from User %s to Node %s Message: %s",
                        self.user.id, db_node.id, ws_message)
            await self.bus.publish(db_node.bus_id, ws_message)

        # Получить из базы каждую лампу
        # Сверить, нода лампу принадлежит юзеру
        # Если не принадлежит, то просто пропустить
        # Отправить на ноду сообщение
        # Нода должна будет ответить,а вот ответ уже записываем в базу и отправляем юзерам


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
            "send_lamps_state_to_nodes": ActionSendLampsStateToNodes,
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
