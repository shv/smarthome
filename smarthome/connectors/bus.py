import asyncio
import json
from smarthome.logger import logger
from smarthome.connectors.broker import RedisPubSubManager
from smarthome.schemas.ws import WSMessage
from starlette.websockets import WebSocketState

class BusSubscriber:
    """
    Собирает данные подписчика в одном месте
    """
    def __init__(self, websocket, bus_id, pubsub_subscriber, task=None):
        self.websocket = websocket
        self.bus_id = bus_id
        self.pubsub_subscriber = pubsub_subscriber
        self.task = task

    async def unsubscribe(self):
        """
        Отписывается от пабсаб и убивает таску, которая слушает пабсаб
        """
        # TODO где-то в этом же районе нужно из WS менеджера убирать коннект
        logger.warning("Unsubscribe: %s", self.bus_id)
        await self.pubsub_subscriber.unsubscribe(self.bus_id)
        logger.warning("Killing  task: %s", self.task)
        if not self.task.cancelled():
            self.task.cancel()
        else:
            self.task = None


class Bus:
    pubsub_client = RedisPubSubManager()
    pubsub_connected = False

    def __init__(self):
        pass

    async def connect(self):
        if not self.pubsub_connected:
            await self.pubsub_client.connect()
            self.pubsub_connected = True

    async def pubsub_data_reader(self, subscriber):
        """
        Reads and broadcasts messages received from Redis PubSub.

        Args:
            subscriber: subscriber info
        """
        logger.info("Starting pubsub subscriber")
        while True:
            # Если будет чаще чем нужно отписывать, можно использовать WebSocketState.DISCONNECTED
            if subscriber.websocket.client_state != WebSocketState.CONNECTED:
                # Это надо делать на дисконнекте. Но там не все данные есть, поэтому пока тут
                await subscriber.unsubscribe()

            redis_message = await subscriber.pubsub_subscriber.get_message(ignore_subscribe_messages=True)
            if redis_message is not None:
                logger.info("State: %s", subscriber.websocket.application_state.value)
                logger.info("Get message from redis: %s", redis_message)
                data = json.loads(redis_message['data'].decode('utf-8'))
                logger.info("Get data from redis: %s", data)
                ws_message = WSMessage(**data)
                # logger.info("Send message to: %s", subscriber.websocket.__dict__)
                logger.info(">>Application stats: %s", subscriber.websocket.application_state.value)
                try:
                    await subscriber.websocket.send_json(ws_message.model_dump(exclude_none=True))
                except RuntimeError as ex:
                    logger.exception("Failed to send message to websocket: %s. Ex: %s", ws_message, ex)
            else:
                await asyncio.sleep(0.1)

    async def publish(self, bus_id: str, message: WSMessage) -> None:
        redis_message = message.model_dump_json(exclude_none=True)

        await self.pubsub_client.publish(bus_id, redis_message)

    async def subscribe(self, websocket, bus_id: str) -> BusSubscriber:
        pubsub_subscriber = await self.pubsub_client.subscribe(bus_id)
        subscriber = BusSubscriber(websocket, bus_id, pubsub_subscriber)
        task = asyncio.create_task(self.pubsub_data_reader(subscriber))
        subscriber.task = task
        logger.info("Pubsub for client %s connected with task: %s", bus_id, task)
        return subscriber


async def get_bus() -> Bus:
    bus = Bus()
    await bus.connect()
    return bus
