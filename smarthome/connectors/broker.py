import redis.asyncio as aioredis
from smarthome.logger import logger
from smarthome.settings import settings


class RedisPubSubManager:
    """
        Initializes the RedisPubSubManager.

    Args:
        host (str): Redis server host.
        port (int): Redis server port.
    """

    def __init__(self, host=settings.redis_host, port=settings.redis_port):
        logger.info("Initializing RedisPubSubManager with host: %s, port: %s", host, port)
        self.redis_host = host
        self.redis_port = port
        self.pubsub = None

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
            channel (str): Channel.
            message (str): Message to be published.
        """
        logger.debug("Publishing to Redis channel %s message: %s", channel, message)
        await self.redis_connection.publish(channel, message)

    async def subscribe(self, channel: str) -> aioredis.Redis:
        """
        Subscribes to a Redis channel.

        Args:
            channel (str): Channel to subscribe to.

        Returns:
            aioredis.ChannelSubscribe: PubSub object for the subscribed channel.
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
        """
        logger.debug("Unsubscribing from Redis channel: %s start", bus_id)
        await self.pubsub.unsubscribe(bus_id)
        logger.info("Unsubscribing from Redis channel: %s done", bus_id)
