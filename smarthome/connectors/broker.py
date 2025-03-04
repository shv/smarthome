"""
Redis Broker Module for Smart Home System.

This module provides Redis-based publish/subscribe functionality for the smart home system,
enabling asynchronous communication between different components through message channels.
It handles connection management, message publishing, and channel subscriptions.
"""

import redis.asyncio as aioredis
from smarthome.logger import logger
from smarthome.settings import settings


class RedisPubSubManager:
    """
    Redis Publish/Subscribe Manager for handling message communication.
    
    This class manages Redis pub/sub connections for asynchronous messaging.

    Args:
        host (str): Redis server host.
        port (int): Redis server port.
    """

    def __init__(self, host: str = settings.redis_host, port: int = settings.redis_port) -> None:
        logger.info("Initializing RedisPubSubManager with host: %s, port: %s", host, port)
        self.redis_host: str = host
        self.redis_port: int = port
        self.pubsub: aioredis.client.PubSub | None = None
        self.redis_connection: aioredis.Redis | None = None

    async def _get_redis_connection(self) -> aioredis.Redis:
        """
        Establishes a connection to Redis.

        Returns:
            aioredis.Redis: Redis connection object.
        """
        logger.debug("Getting Redis connection")
        return aioredis.Redis(host=self.redis_host,
                              port=self.redis_port,
                              # password="my-password",
                              auto_close_connection_pool=False)

    async def connect(self) -> None:
        """
        Connects to the Redis server and initializes the pubsub client.
        
        Raises:
            aioredis.RedisError: If connection to Redis server fails.
        """
        logger.debug("Start connecting to Redis server")
        self.redis_connection = await self._get_redis_connection()
        self.pubsub = self.redis_connection.pubsub()
        # TODO сделать 1 коннект, а не каждый раз
        logger.debug("self.redis_connection: %s", self.redis_connection)
        logger.info("Redis server connected")

    async def publish(self, channel: str, message: str) -> None:
        """
        Publishes a message to a specific Redis channel.

        Args:
            channel (str): Channel to publish to.
            message (str): Message to be published.
            
        Raises:
            aioredis.RedisError: If publishing fails.
        """
        logger.debug("Publishing to Redis channel %s message: %s", channel, message)
        await self.redis_connection.publish(channel, message)

    async def subscribe(self, channel: str) -> aioredis.client.PubSub:
        """
        Subscribes to a Redis channel.

        Args:
            channel (str): Channel to subscribe to.

        Returns:
            aioredis.client.PubSub: PubSub object for the subscribed channel.
            
        Raises:
            aioredis.RedisError: If subscription fails.
        """
        logger.debug("Subscribing to Redis channel: %s start", channel)
        try:
            await self.pubsub.subscribe(channel)
        except aioredis.RedisError as e:
            logger.exception("Failed to subscribe to Redis channel: %s", channel)
            raise e
        logger.info("Subscribing to Redis channel: %s done", channel)
        return self.pubsub

    async def unsubscribe(self, bus_id: str) -> None:
        """
        Unsubscribes from a Redis channel.

        Args:
            bus_id (str): Channel or room ID to unsubscribe from.
            
        Raises:
            aioredis.RedisError: If unsubscribing fails.
        """
        logger.debug("Unsubscribing from Redis channel: %s start", bus_id)
        await self.pubsub.unsubscribe(bus_id)
        logger.info("Unsubscribing from Redis channel: %s done", bus_id)
