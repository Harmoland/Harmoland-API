from fastapi import WebSocket

# from loguru import logger
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from libs.server import route
from util import WsConnectionManager

manager = WsConnectionManager()


async def handler(log):
    await manager.broadcast(log)


# logger.add(handler, colorize=True, serialize=True)


@route.ws("/log")
async def logger_broadcast(client: WebSocket):
    # print(client['subprotocols'])  # list[str]
    await manager.connect(client)
    await manager.broadcast('有新连接~')
    await client.send_text('早~哦哈哟')
    while True:
        try:
            text = await client.receive_text()
            if text == '{"messsage": "bye"}':
                manager.disconnect(client)
                break
        except (
            WebSocketDisconnect,
            ConnectionClosedOK,
            ConnectionClosedError,
            RuntimeError,
        ):
            manager.disconnect(client)
            break
