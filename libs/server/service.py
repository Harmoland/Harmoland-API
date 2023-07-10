import asyncio
import logging

from fastapi import FastAPI
from graia.amnesia.builtins.starlette import StarletteService
from graia.amnesia.builtins.uvicorn import WithoutSigHandlerServer
from graia.amnesia.transport.common.asgi import AbstractAsgiService, ASGIHandlerProvider
from launart.manager import Launart
from launart.utilles import wait_fut
from loguru import logger
from uvicorn import Config, Server

from util import LoguruHandler, loguru_handler


class FastAPIService(StarletteService):
    def __init__(self, fastapi: FastAPI | None = None) -> None:
        self.fastapi = fastapi or FastAPI()
        super().__init__(self.fastapi)


class UvicornService(AbstractAsgiService):
    id = "http.asgi_runner/uvicorn"
    server: Server

    def __init__(self, host: str = "127.0.0.1", port: int = 8000, **kwargs):
        super().__init__(host, port)
        self.config = kwargs

    @property
    def required(self):
        return {ASGIHandlerProvider}

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    async def launch(self, mgr: Launart):
        async with self.stage("preparing"):
            asgi_handler = mgr.get_interface(ASGIHandlerProvider).get_asgi_handler()
            self.server = WithoutSigHandlerServer(Config(asgi_handler, host=self.host, port=self.port, **self.config))
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
