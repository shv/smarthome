"""
WebSocket Connection Management Module.

This module provides classes for managing WebSocket connections in the smart home system,
including connection handling, message broadcasting, and disconnection management.
"""
from typing import Any

from fastapi import WebSocket
from smarthome.logger import logger


class WSConnectionManager:
    """
    WebSocket Connection Manager.
    
    This class manages active WebSocket connections and provides methods for
    sending messages to individual connections or broadcasting to all connections.
    """
    
    def __init__(self) -> None:
        """Initialize a new WebSocket connection manager with empty connections list."""
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accept a new WebSocket connection and add it to active connections.
        
        Args:
            websocket: The WebSocket connection to accept and manage
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection from active connections.
        
        Args:
            websocket: The WebSocket connection to remove
        """
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict[str, Any], websocket: WebSocket) -> None:
        """
        Send a message to a specific WebSocket connection.
        
        Args:
            message: The message to send as JSON
            websocket: The WebSocket connection to send to
        """
        await websocket.send_json(message)

    async def broadcast(self, message: dict[str, Any]) -> None:
        """
        Broadcast a message to all active WebSocket connections.
        
        This method attempts to send the message to all connections and handles
        exceptions by disconnecting problematic connections.
        
        Args:
            message: The message to broadcast as JSON
        """
        for connection in self.active_connections:
            logger.debug("Broadcasting message %s", message)
            try:
                await connection.send_json(message)
            except Exception as ex:
                logger.exception("Problem with broadcast message %s: %s", message, ex)
                # Remove the connection when an error occurs during broadcast
                self.disconnect(connection)
