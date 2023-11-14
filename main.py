#!/usr/bin/env python3

import importlib
import logging
import pkgutil
import sys
from logging import StreamHandler
from pathlib import Path

from launart import Launart, Service
from loguru import logger

from libs.aiohttp_service import AiohttpClientService
from libs.database.service import DatabaseService
from libs.rcon.service import RconService
from libs.server import fastapi
from libs.server.service import FastAPIService, UvicornService
from util import loguru_handler


class MainLoop(Service):
    id = "main"

    @property
    def stages(self):
        return {"blocking"}

    @property
    def required(self):
        return set()

    async def launch(self, mgr: Launart):
        async with self.stage("blocking"):
            await mgr.status.wait_for_sigexit()


launart = Launart()

launart.add_component(FastAPIService(fastapi))
launart.add_component(UvicornService(app=fastapi, host="127.0.0.1", port=8000))
launart.add_component(AiohttpClientService())
launart.add_component(DatabaseService())
launart.add_component(RconService("127.0.0.1", 25575, passwd="111funnyguy"))
launart.add_component(MainLoop())

# 加载api
core_modules_path = Path("api")
for module in pkgutil.iter_modules([str(core_modules_path)]):
    importlib.import_module(f"api.{module.name}", f"api.{module.name}")

logging.basicConfig(handlers=[loguru_handler], level=0, force=True)
for name in logging.root.manager.loggerDict:
    _logger = logging.getLogger(name)
    for handler in _logger.handlers:
        if isinstance(handler, StreamHandler):
            _logger.removeHandler(handler)

logger.remove()
logger.add(sys.stderr, level="INFO", enqueue=True)


launart.launch_blocking()
