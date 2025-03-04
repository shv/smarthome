"""
Bus Module for Smart Home System.

This module provides a message bus implementation using Redis pub/sub for communication
between different components of the smart home system. It handles WebSocket connections,
message broadcasting, and subscription management.
"""

import asyncio
import json
from starlette.websockets import WebSocket, WebSocketState

from smarthome.logger import logger
from smarthome.connectors.broker import RedisPubSubManager
from smarthome.schemas.ws import WSMessage


class BusSubscriber:
    """
    Manages subscriber data and lifecycle.
    
    This class collects and manages all data related to a single subscriber,
    including the WebSocket connection, bus ID, and Redis pubsub subscription.
    
    Args:
        websocket: The WebSocket connection for this subscriber
        bus_id: Unique identifier for the subscription channel
        pubsub_subscriber: Redis pubsub subscription object
        task: Optional asyncio task that handles message reading
    """
    def __init__(
        self, 
        websocket: WebSocket, 
        bus_id: str, 
        pubsub_subscriber: any,  # Redis pubsub type
        task: asyncio.Task | None = None
    ) -> None:
        self.websocket: WebSocket = websocket
        self.bus_id: str = bus_id
        self.pubsub_subscriber: any = pubsub_subscriber
        self.task: asyncio.Task | None = task

    async def unsubscribe(self) -> None:
        """
        Unsubscribes from the pubsub channel and cancels the listening task.
        
        This method handles the cleanup of resources when a subscriber disconnects.
        """
        # TODO: Remove connection from WS manager as well
        logger.warning("Unsubscribe: %s", self.bus_id)
        await self.pubsub_subscriber.unsubscribe(self.bus_id)
        logger.warning("Killing task: %s", self.task)
        if self.task and not self.task.cancelled():
            self.task.cancel()
        else:
            self.task = None


class Bus:
    """
    Message bus for handling communication between system components.
    
    This class provides methods for publishing messages to channels and
    subscribing to receive messages from channels using Redis pub/sub.
    """
    pubsub_client: RedisPubSubManager = RedisPubSubManager()
    pubsub_connected: bool = False

    def __init__(self) -> None:
        """Initialize a new Bus instance."""
        pass

    async def connect(self) -> None:
        """
        Connect to the Redis pub/sub system.
        
        This method ensures we only connect once to the Redis server.
        """
        if not self.pubsub_connected:
            await self.pubsub_client.connect()
            self.pubsub_connected = True

    async def pubsub_data_reader(self, subscriber: BusSubscriber) -> None:
        """
        Reads and broadcasts messages received from Redis PubSub.

        This method continuously polls for new messages from Redis and forwards
        them to the appropriate WebSocket connection.

        Args:
            subscriber: The subscriber object containing connection information
        """
        logger.debug("Starting pubsub subscriber")
        while True:
            # Если будет чаще чем нужно отписывать, можно использовать WebSocketState.DISCONNECTED
            if subscriber.websocket.client_state != WebSocketState.CONNECTED:
                # Это надо делать на дисконнекте. Но там не все данные есть, поэтому пока тут
                await subscriber.unsubscribe()

            redis_message = await subscriber.pubsub_subscriber.get_message(ignore_subscribe_messages=True)
            if redis_message is not None:
                logger.debug("State: %s", subscriber.websocket.application_state.value)
                logger.debug("Get message from redis: %s", redis_message)
                data = json.loads(redis_message['data'].decode('utf-8'))
                logger.debug("Get data from redis: %s", data)
                ws_message = WSMessage(**data)
                logger.debug(">>Application stats: %s", subscriber.websocket.application_state.value)
                try:
                    await subscriber.websocket.send_json(ws_message.model_dump(exclude_none=True))
                except Exception as ex:
                    logger.exception("Failed to send message to websocket: %s. Ex: %s", ws_message, ex)
            else:
                await asyncio.sleep(0.1)

    async def publish(self, bus_id: str, message: WSMessage) -> None:
        """
        Publish a message to the specified bus channel.
        
        Args:
            bus_id: The channel identifier to publish to
            message: The WebSocket message to publish
        """
        redis_message = message.model_dump_json(exclude_none=True)
        await self.pubsub_client.publish(bus_id, redis_message)

    async def subscribe(self, websocket: WebSocket, bus_id: str) -> BusSubscriber:
        """
        Subscribe a WebSocket connection to a bus channel.
        
        This method creates a new subscription to the specified channel and
        starts a background task to listen for messages.
        
        Args:
            websocket: The WebSocket connection to send messages to
            bus_id: The channel identifier to subscribe to
            
        Returns:
            A BusSubscriber object representing the subscription
        """
        pubsub_subscriber = await self.pubsub_client.subscribe(bus_id)
        subscriber = BusSubscriber(websocket, bus_id, pubsub_subscriber)
        task = asyncio.create_task(self.pubsub_data_reader(subscriber))
        subscriber.task = task
        logger.info("Pubsub for client %s connected with task: %s", bus_id, task)
        return subscriber


async def get_bus() -> Bus:
    """
    Factory function to get a connected Bus instance.
    
    This function is designed to be used with FastAPI's dependency injection system.
    
    Returns:
        A connected Bus instance
    """
    bus = Bus()
    await bus.connect()
    return bus
