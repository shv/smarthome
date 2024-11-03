"""
Nodes ws
https://fastapi.tiangolo.com/advanced/websockets/
"""
import asyncio
from typing import Annotated
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from smarthome import models
from smarthome.auth import get_current_node_for_ws
from smarthome.actions.all_actions import ActionResolver, get_action_resolver
from smarthome.connectors.ws import WSConnectionManager
from smarthome.connectors.bus import Bus, get_bus
from smarthome.depends import get_db
from smarthome.logger import logger
from smarthome.settings import settings
from smarthome.schemas.ws import WSMessage

router = APIRouter(
    prefix=settings.main_url
)

# Объединить в один ws коннект
manager = WSConnectionManager()


@router.websocket("/ws/nodes")
async def websocket_node_endpoint(
        websocket: WebSocket,
        node: Annotated[models.Node, Depends(get_current_node_for_ws)],
        bus: Annotated[Bus, Depends(get_bus)],
        action_resolver: Annotated[ActionResolver, Depends(get_action_resolver)],
        db: Annotated[Session, Depends(get_db)],
):
    """
    Nodes ws endpoint.
    Нода слушает свой канал. Если что-то меняется - данные отправляются ноде.
    При этом все, что с нодой происходит, получают все пользователи ноды.
    """
    await manager.connect(websocket)
    subscriber = await bus.subscribe(websocket, node.bus_id)
    node.is_online = True
    db.commit()

    users = node.users

    for user in users:
        ws_message = WSMessage(
            request_id="1",
            action="updated_node",
            data={"id": node.id, "is_online": node.is_online},
        )
        await bus.publish(user.bus_id, ws_message)

    try:
        while True:
            try:
                message = await websocket.receive_json()
                logger.debug("Get data from websocket: %s", message)
            except RuntimeError as ex:
            #     logger.exception("Wrong message from node %s: %s", node, ex)
            #     await asyncio.sleep(0.5)
            #     continue
            # except Exception as ex:
            #     logger.exception("Wrong message from node %s: %s", node, ex)
            #     await asyncio.sleep(0.5)
                continue

            if message is not None:
                logger.debug("Get data from websocket: %s", message)
                ws_message = WSMessage(**message)
                logger.debug("Get data from websocket: %s", ws_message)
                # Переводим ноду в онлайн - она прислала сообщение
                if not node.is_online:
                    node.is_online = True
                    db.commit()
                    logger.error("Node %s was not online in db but send message: %s", node, ws_message)
                await action_resolver.process(node, ws_message)
            else:
                await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        # TODO перенести возможно в общий метод отписки
        node.is_online = False
        db.commit()
        manager.disconnect(websocket)
        await subscriber.unsubscribe()

        for user in users:
            ws_message = WSMessage(
                request_id="1",
                action="updated_node",
                data={"id": node.id, "is_online": node.is_online},
            )
            await bus.publish(user.bus_id, ws_message)

        logger.warning(f"Node {node.id} disconnected")
