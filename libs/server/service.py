import asyncio
import logging
from collections.abc import Callable
from typing import Any, Union

from fastapi import FastAPI
from launart import Launart, Service
from launart.utilles import wait_fut
from loguru import logger
from uvicorn import Config, Server
from uvicorn._types import ASGIApplication

from util import LoguruHandler, loguru_handler


class WithoutSigHandlerServer(Server):
    def install_signal_handlers(self) -> None:
        pass


class FastAPIService(Service):
    id = "http.server/starlette"
    supported_interface_types = tuple[Any]
    fastapi: FastAPI

    def __init__(self, fastapi: FastAPI | None = None) -> None:
        self.fastapi = fastapi or FastAPI()
        super().__init__()

    @property
    def stages(self):
        return set()

    @property
    def required(self):
        return set()

    async def launch(self, _):
        pass


class UvicornService(Service):
    supported_interface_types = set()
    id = "http.asgi_runner/uvicorn"
    server: Server
    host: str
    port: int
    app: Union["ASGIApplication", Callable, str]

    def __init__(
        self, app: Union["ASGIApplication", Callable, str], host: str = "127.0.0.1", port: int = 8000, **kwargs
    ):
        self.config = kwargs
        self.host = host
        self.port = port
        self.app = app
        super().__init__()

    @property
    def required(self) -> set[str]:
        return set()

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    async def launch(self, mgr: Launart):
        async with self.stage("preparing"):
            self.server = WithoutSigHandlerServer(Config(self.app, host=self.host, port=self.port, **self.config))
            del self.config
            PATCHES = "uvicorn.error", "uvicorn.asgi", "uvicorn.access", ""
            level = logging.getLevelName(20)  # default level for uvicorn
            logging.basicConfig(handlers=[loguru_handler], level=level)
            for name in PATCHES:
                target = logging.getLogger(name)
                target.handlers = [LoguruHandler(level=level)]
                target.propagate = False
            serve_task = asyncio.create_task(self.server.serve())

        async with self.stage("cleanup"):
            logger.warning("try to shutdown uvicorn server...")
            self.server.should_exit = True
            await wait_fut([serve_task, asyncio.sleep(10)], return_when=asyncio.FIRST_COMPLETED)
            if not serve_task.done():
                logger.warning("timeout, force exit uvicorn server...")
