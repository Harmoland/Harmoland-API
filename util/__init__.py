import logging
import sys
from contextlib import suppress
from typing import Any

from fastapi import WebSocketDisconnect, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.websockets import WebSocket
from launart import Launart
from loguru import logger
from pydantic import BaseModel
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from libs.rcon.interface import Rcon


class LoguruHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class BaseResponse(BaseModel):
    code: int = status.HTTP_200_OK
    message: str = "success"
    data: dict[str, Any] | BaseModel | list[Any] | list[BaseModel] | None = None


class WsConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, client: WebSocket):
        await client.accept()
        self.active_connections.append(client)

    def disconnect(self, client: WebSocket):
        with suppress(ValueError):
            self.active_connections.remove(client)

    async def send_personal_message(self, message: str, client: WebSocket):
        try:
            await client.send_text(message)
        except (
            WebSocketDisconnect,
            ConnectionClosedOK,
            ConnectionClosedError,
            RuntimeError,
        ):
            self.disconnect(client)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except (
                WebSocketDisconnect,
                ConnectionClosedOK,
                ConnectionClosedError,
                RuntimeError,
            ):
                self.disconnect(connection)

    async def broadcast_json(self, message: dict[str, str]):
        for connection in self.active_connections:
            try:
                await connection.send_json(str(message))
            except (
                WebSocketDisconnect,
                ConnectionClosedOK,
                ConnectionClosedError,
                RuntimeError,
            ):
                self.disconnect(connection)


async def get_rcon_client() -> Rcon:
    return Launart.current().get_interface(Rcon)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
loguru_handler = LoguruHandler()
