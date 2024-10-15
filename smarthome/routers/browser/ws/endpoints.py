"""
Browser endpoints ans ws
https://fastapi.tiangolo.com/advanced/websockets/
"""
import asyncio
from typing import Annotated
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from smarthome import models
from smarthome.actions.all_actions import ActionResolver, get_action_resolver
from smarthome.auth import get_current_user
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
        user: Annotated[models.User, Depends(get_current_user)],
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
    logger.info("Application stats: %s", websocket.application_state)
    await manager.connect(websocket)
    subscriber = await bus.subscribe(websocket, user.bus_id)

    ws_message = WSMessage(
        request_id="1",
        action="connect",
        data={"message": f"User #{user.id} connected"},
    )
    await manager.broadcast(ws_message.model_dump(exclude_none=True))

    try:
        while True:
            try:
                message = await websocket.receive_json()
                logger.info("Get data from websocket: %s", message)
            except RuntimeError as ex:
                logger.exception("Wrong message from user %s: %s", user, ex)
                continue

            if message is not None:
                logger.info("Get message from websocket: %s", message)
                ws_message = WSMessage(**message)
                logger.info("Get ws_message from websocket: %s", ws_message)
                await action_resolver.process(user, ws_message)
            else:
                await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        # TODO перенести возможно в общий метод отписки
        manager.disconnect(websocket)
        await subscriber.unsubscribe()
        ws_message = WSMessage(
            request_id="1",
            action="disconnect",
            data={"message": f"User {user.id} disconnected"},
        )
        await manager.broadcast(ws_message.model_dump(exclude_none=True))
        logger.error(f"User {user.id} disconnected")
