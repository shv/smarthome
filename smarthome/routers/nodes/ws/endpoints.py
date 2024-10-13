"""
Nodes ws
https://fastapi.tiangolo.com/advanced/websockets/
"""
from typing import Annotated
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from smarthome import models
from smarthome.auth import get_current_node
from smarthome.actions.all_actions import ActionResolver, get_action_resolver
from smarthome.connectors.ws import WSConnectionManager
from smarthome.connectors.bus import Bus, get_bus
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
        node: Annotated[models.Node, Depends(get_current_node)],
        bus: Annotated[Bus, Depends(get_bus)],
        action_resolver: Annotated[ActionResolver, Depends(get_action_resolver)],
):
    """
    Nodes ws endpoint.
    Нода слушает свой канал. Если что-то меняется - данные отправляются ноде.
    При этом все, что с нодой происходит, получают все пользователи ноды.
    """
    await manager.connect(websocket)
    await bus.subscribe(websocket, node.bus_id)
    ws_message = WSMessage(
        request_id="1",
        action="connect",
        data={"message": f"Node #{node.id} connected"},
    )
    await manager.broadcast(ws_message.model_dump(exclude_none=True))

    try:
        while True:
            try:
                message = await websocket.receive_json()
                logger.info("Get data from websocket: %s", message)
            except RuntimeError as ex:
                logger.exception("Wrong message from user %s: %s", node, ex)
                continue

            if message is not None:
                logger.info("Get data from websocket: %s", message)
                ws_message = WSMessage(**message)
                logger.info("Get data from websocket: %s", ws_message)
                await action_resolver.process(node, ws_message)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        ws_message = WSMessage(
            request_id="1",
            action="disconnect",
            data={"message": f"Node {node.id} disconnected"},
        )
        await manager.broadcast(ws_message.model_dump(exclude_none=True))
        logger.error(f"Node {node.id} disconnected")
