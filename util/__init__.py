from contextlib import suppress
from typing import Any, Dict, List, Union

import orjson
from fastapi import WebSocketDisconnect, status
from fastapi.websockets import WebSocket
from pydantic import BaseModel as PyDanticBaseModel
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK


def orjson_dumps(v, *, default, **dumps_kwargs):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default, **dumps_kwargs).decode()


class BaseModel(PyDanticBaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class BaseResponse(BaseModel):
    code: int = status.HTTP_200_OK
    message: str = "success"
    data: Union[Dict[str, Any], BaseModel, List[Any], List[BaseModel], None] = None


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
