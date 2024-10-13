""" WebSocket classes """
from fastapi import WebSocket
from smarthome.logger import logger


class WSConnectionManager:
    """ WS Connection manager """
    def __init__(self) -> None:
        """ Init class """
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """ Connect handler """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """ Disconnect handler """
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket) -> None:
        """ Send message to me """
        await websocket.send_json(message)

    async def broadcast(self, message: dict) -> None:
        """ Send messages to all connections """
        for connection in self.active_connections:
            # logger.info("Broadcasting message to %s", connection.__dict__)
            await connection.send_json(message)
