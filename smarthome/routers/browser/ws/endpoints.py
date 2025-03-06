"""
Browser WebSocket endpoints.

This module provides WebSocket endpoints for browser clients to connect to the system.
See: https://fastapi.tiangolo.com/advanced/websockets/
"""
import asyncio
from typing import Annotated, Any
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

# TODO: Combine into a single WS connection
manager: WSConnectionManager = WSConnectionManager()


@router.websocket("/ws")
async def websocket_user_endpoint(
        websocket: WebSocket,
        user: Annotated[models.User, Depends(get_current_user_for_ws)],
        bus: Annotated[Bus, Depends(get_bus)],
        action_resolver: Annotated[ActionResolver, Depends(get_action_resolver)],
) -> None:
    """
    WebSocket endpoint for browser clients.
    
    When a user connects, they start receiving messages from all their active nodes
    and all changes related to those nodes. The user subscribes to the bus, not the node.
    Messages from nodes are processed and, if necessary, sent to the appropriate users.
    
    Args:
        websocket: The WebSocket connection from the browser client
        user: The authenticated user making the connection
        bus: The message bus for communication
        action_resolver: The resolver for processing WebSocket actions
    """
    logger.debug("Application state: %s", websocket.application_state)
    await manager.connect(websocket)
    subscriber = await bus.subscribe(websocket, user.bus_id)

    try:
        while True:
            try:
                message: dict[str, Any] = await websocket.receive_json()
                logger.debug("Get data from websocket: %s", message)
            except RuntimeError as ex:
                logger.exception("Wrong message from user %s: %s", user, ex)
                # await asyncio.sleep(0.5)
                continue
            # except Exception as ex:
            #     logger.exception("Wrong message from user %s: %s", user, ex)
            #     await asyncio.sleep(0.5)
            #     continue

            if message is not None:
                logger.debug("Get message from websocket: %s", message)
                # Example message format: {"request_id": "1", "action": "restart_node", "data": {"id": 1}}
                # try:
                ws_message: WSMessage = WSMessage(**message)
                logger.debug("Get ws_message from websocket: %s", ws_message)
                await action_resolver.process(user, ws_message)
                # except Exception:
                #     logger.exception("Wrong message: %s", message)
                #     await asyncio.sleep(0.1)
                #     continue
                # Example: {"request_id": "1", "action": "restart_node", "data": {"id": 1}}
            else:
                await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        # TODO: Consider moving this to a common unsubscribe method
        manager.disconnect(websocket)
        await subscriber.unsubscribe()
        logger.warning("User %s disconnected", user.id)
