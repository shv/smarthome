"""
Browser endpoints ans ws
https://fastapi.tiangolo.com/advanced/websockets/
"""
import asyncio
from typing import Annotated
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from smarthome import models
from smarthome.actions.all_actions import ActionResolver, get_action_resolver
from smarthome.auth import get_current_user_for_ws
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


@router.websocket("/ws")
async def websocket_user_endpoint(
        websocket: WebSocket,
        user: Annotated[models.User, Depends(get_current_user_for_ws)],
        bus: Annotated[Bus, Depends(get_bus)],
        action_resolver: Annotated[ActionResolver, Depends(get_action_resolver)],
):
    """
    WS for browser endpoint.
    При подключении я должен начать получать сообщения со всех моих активных нод.
    Так же все изменения, связанные с нодами.
    То есть по факту подписывается пользователь, а не нода.
    От ноды получаем сообщение, что-то с ним делаем и, если надо, отправляем пользователям.
    """
    logger.debug("Application state: %s", websocket.application_state)
    await manager.connect(websocket)
    subscriber = await bus.subscribe(websocket, user.bus_id)

    try:
        while True:
            try:
                message = await websocket.receive_json()
                logger.debug("Get data from websocket: %s", message)
            except RuntimeError as ex:
                logger.exception("Wrong message from user %s: %s", user, ex)
            #     await asyncio.sleep(0.5)
            #     continue
            # except Exception as ex:
            #     logger.exception("Wrong message from user %s: %s", user, ex)
            #     await asyncio.sleep(0.5)
                continue

            if message is not None:
                logger.debug("Get message from websocket: %s", message)
                # try:
                ws_message = WSMessage(**message)
                logger.debug("Get ws_message from websocket: %s", ws_message)
                await action_resolver.process(user, ws_message)
                # except Exception:
                #     logger.exception("Wrong message: %s", message)
                #     await asyncio.sleep(0.1)
                #     continue
                #{"request_id": "1", "action": "restart_node", "data": {"id": 1}}
            else:
                await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        # TODO перенести возможно в общий метод отписки
        manager.disconnect(websocket)
        await subscriber.unsubscribe()
        logger.warning(f"User {user.id} disconnected")
