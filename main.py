#!/usr/bin/env python3

import importlib
import logging
import pkgutil
import sys
from logging import StreamHandler
from pathlib import Path

from graia.amnesia.builtins.aiohttp import AiohttpClientService
from launart import Launart, Launchable
from loguru import logger

from libs.database.service import DatabaseInitService
from libs.rcon.service import RconService
from libs.server import fastapi
from libs.server.service import FastAPIService, UvicornService
from util import loguru_handler

logging.basicConfig(handlers=[loguru_handler], level=0, force=True)
for name in logging.root.manager.loggerDict:
    _logger = logging.getLogger(name)
    for handler in _logger.handlers:
        if isinstance(handler, StreamHandler):
            _logger.removeHandler(handler)

logger.remove()
logger.add(sys.stderr, level="INFO", enqueue=True)


class MainLoop(Launchable):
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

launart.add_service(FastAPIService(fastapi))
launart.add_service(UvicornService())
launart.add_service(AiohttpClientService())
launart.add_service(DatabaseInitService())
launart.add_service(RconService("127.0.0.1", 25575, passwd="111funnyguy"))
launart.add_launchable(MainLoop())

# 加载api
core_modules_path = Path("api")
for module in pkgutil.iter_modules([str(core_modules_path)]):
    importlib.import_module(f"api.{module.name}", f"api.{module.name}")


launart.launch_blocking()
