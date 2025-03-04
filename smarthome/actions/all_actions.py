"""
Action handling system for the smart home application.

This module defines the action system that processes WebSocket messages from nodes and users.
It contains base classes and specific implementations for various actions like lamp control,
sensor data processing, and node management. The action resolver routes incoming messages
to the appropriate action handlers.
"""

import datetime
from abc import ABC, abstractmethod
from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from smarthome import models
from smarthome.depends import get_db
from smarthome.connectors.bus import Bus, get_bus
from smarthome.logger import logger
from smarthome.schemas.ws import WSMessage


class BaseAction(ABC):
    """
    Base class for all actions.
    
    If classes inherit from this class, all actions can be automatically collected.
    """
    node: models.Node | None
    user: models.User | None
    
    def __init__(self, client: models.Node | models.User, bus: Bus, db: Session) -> None:
        """
        Initialize the action with a client, bus, and database session.
        
        Args:
            client: Either a Node or User model instance
            bus: Bus instance for message publishing
            db: Database session
        """
        self.node = None
        self.user = None
        
        if isinstance(client, models.Node):
            self.node = client
        elif isinstance(client, models.User):
            self.user = client
        
        self.bus = bus
        self.db = db

    @abstractmethod
    async def process(self, data: dict[str, Any]) -> None:
        """
        Process the action with the given data.
        
        This method must be overridden in each subclass.
        
        Args:
            data: Dictionary containing action parameters
        """


class ActionLampChangedFromNode(BaseAction):
    """
    Process lamp data received from a node.
    
    This action is bound to a node and handles lamp state changes.
    """

    async def process(self, data: dict[str, Any]) -> None:
        """
        Process lamp data from a node.
        
        The data format from the node is expected to be a JSON with parameters in the root.
        
        Args:
            data: Dictionary containing lamp data with 'id' and 'value' keys
        """
        logger.debug("ActionLampChangedFromNode. DATA from ESP32 #%s: %s", self.node.id, data)

        node_lamp_id = data.get("id")
        value = data.get("value")
        db_lamp = self.db.query(models.NodeLamp).filter(
            models.NodeLamp.node_lamp_id == node_lamp_id,
            models.NodeLamp.node == self.node,
        ).first()
        logger.debug("Lamp from db: %s", db_lamp)
        if not db_lamp:
            logger.warning("Lamp %s not found in db", node_lamp_id)
            return

        db_lamp.value = value
        db_lamp.updated = datetime.datetime.now(datetime.timezone.utc)
        self.db.commit()

        users = self.node.users

        # Replace the action and generally improve the action system
        for user in users:
            ws_message = WSMessage(
                request_id="1",
                action="updated_lamp",
                data={"id": db_lamp.id, "value": db_lamp.value, "updated": db_lamp.updated},
            )
            logger.info("Action updated_lamp from Node %s to user %s Message: %s", self.node.id, user.id, ws_message)
            await self.bus.publish(user.bus_id, ws_message)


class ActionSensorChangedFromNode(BaseAction):
    """
    Process sensor data received from a node.
    
    This action is bound to a node and handles sensor value changes.
    """

    async def process(self, data: dict[str, Any]) -> None:
        """
        Process sensor data from a node.
        
        The data format from the node is expected to be a JSON with parameters in the root.
        
        Args:
            data: Dictionary containing sensor data with 'id' and 'value' keys
        """
        logger.debug("ActionSensorChangedFromNode. DATA from ESP32 #%s: %s", self.node.id, data)

        node_sensor_id = data.get("id")
        value = data.get("value")
        db_sensor = self.db.query(models.NodeSensor).filter(
            models.NodeSensor.node_sensor_id == node_sensor_id,
            models.NodeSensor.node == self.node,
        ).first()
        logger.debug("Sensor from db: %s", db_sensor)
        if not db_sensor:
            logger.warning("Sensor %s not found in db", node_sensor_id)
            return

        db_sensor.value = value
        db_sensor.updated = datetime.datetime.now(datetime.timezone.utc)
        logger.debug("Sensor %s updated db: %s (%s)", db_sensor.id, db_sensor.value, db_sensor.updated)
        self.db.commit()

        users = self.node.users

        # Replace the action and generally improve the action system
        for user in users:
            ws_message = WSMessage(
                request_id="1",
                action="updated_sensor",
                data={"id": db_sensor.id, "value": db_sensor.value, "updated": db_sensor.updated},
            )
            logger.info("Action updated_sensor from Node %s to user %s Message: %s", self.node.id, user.id, ws_message)
            await self.bus.publish(user.bus_id, ws_message)


class ActionSendLampsStateToNodes(BaseAction):
    """
    Control lamps on nodes by a user.
    
    This action is bound to a user and sends lamp state changes to nodes.
    """

    async def process(self, data: dict[str, Any]) -> None:
        """
        Process lamp state changes from a user and send them to nodes.
        
        Input data format:
        {"lamps": [{"id": 1, "value": 0}]}
        where 'id' is the lamp identifier in the database.
        
        Output to node for each lamp:
        {"id": 1, "value": 0}
        where 'id' is the internal lamp identifier within the node.
        
        Args:
            data: Dictionary containing lamp state changes
        """
        logger.debug("ActionSendLampsStateToNodes. DATA from User #%s: %s", self.user.id, data)
        for lamp in data["lamps"]:
            db_lamp = self.db.query(models.NodeLamp).filter(models.NodeLamp.id == lamp["id"]).first()
            logger.debug("Lamp from db: %s", db_lamp)
            if not db_lamp:
                logger.warning("Lamp %s not found in db", lamp["id"])
                continue

            db_node = db_lamp.node
            logger.debug("Node for lamp %s: %s", db_lamp, db_node)
            if self.user not in db_node.users:
                logger.error("Lamp %s is not connected to user %s", db_lamp, self.user)
                continue

            ws_message = WSMessage(
                request_id="1",
                action="set_lamp_state",
                data={"id": db_lamp.node_lamp_id, "value": lamp["value"]},
            )
            logger.info("Action set_lamp_state from User %s to Node %s Message: %s",
                        self.user.id, db_node.id, ws_message)
            await self.bus.publish(db_node.bus_id, ws_message)

        # Get each lamp from the database
        # Verify that the lamp's node belongs to the user
        # If it doesn't belong, just skip it
        # Send a message to the node
        # The node should respond, and we record that response in the database and send it to users


class ActionRestartNode(BaseAction):
    """
    Restart a node.
    
    This action is bound to a user and sends restart commands to nodes.
    """

    async def process(self, data: dict[str, Any]) -> None:
        """
        Process node restart request from a user.
        
        Input data format:
        {"id": 1}
        where 'id' is the node identifier in the database.
        
        Sends to the node an action = "restart" without additional data.
        
        Args:
            data: Dictionary containing the node ID to restart
        """
        logger.debug("ActionRestartNode. DATA from User #%s: %s", self.user.id, data)
        db_node = self.db.query(models.Node).filter(models.Node.id == data["id"]).first()
        logger.debug("Node from db: %s", db_node)
        if not db_node:
            logger.warning("Node %s not found in db", data["id"])
            return

        if self.user not in db_node.users:
            logger.error("Node %s is not connected to user %s", db_node, self.user)
            return

        ws_message = WSMessage(
            request_id="1",
            action="restart",
        )
        logger.info("Action restart from User %s to Node %s Message: %s", self.user.id, db_node.id, ws_message)
        await self.bus.publish(db_node.bus_id, ws_message)


class ActionResolver:
    """
    Action resolver that processes WebSocket messages and routes them to appropriate actions.
    
    This class is implemented as a singleton through FastAPI's Depends.
    """
    def __init__(self, db: Session, bus: Bus) -> None:
        """
        Initialize the action resolver.
        
        Args:
            db: Database session
            bus: Bus instance for message publishing
        """
        self.db = db
        self.bus = bus

    async def process(self, client: models.Node | models.User, ws_message: WSMessage) -> None:
        """
        Process actions from WebSockets of nodes and users.
        
        Args:
            client: User or node that initiated the action
            ws_message: WebSocket message containing the action and data
        """
        # Action mapper. Selects the action class based on the action from the message
        action_map = {
            "lamp_changed": ActionLampChangedFromNode,
            "sensor_changed": ActionSensorChangedFromNode,
            "send_lamps_state_to_nodes": ActionSendLampsStateToNodes,
            "restart_node": ActionRestartNode,
        }

        action_class = action_map[ws_message.action]
        logger.info("ActionResolver %s from client %s. Message: %s", action_class, client, ws_message)

        try:
            await action_class(client=client, bus=self.bus, db=self.db).process(data=ws_message.data)
        except AttributeError as ex:
            logger.exception("Failed process in action %s: %s", action_class, ex)


async def get_action_resolver(db: Session = Depends(get_db), bus: Bus = Depends(get_bus)) -> ActionResolver:
    """
    Get an instance of ActionResolver.
    
    This function is designed to be used with FastAPI's dependency injection system.
    
    Args:
        db: Database session obtained through dependency injection
        bus: Bus instance obtained through dependency injection
        
    Returns:
        An instance of ActionResolver
    """
    action_resolver = ActionResolver(db=db, bus=bus)
    return action_resolver
