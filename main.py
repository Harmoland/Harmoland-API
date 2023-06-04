import asyncio
import importlib
import logging
import pkgutil
import sys
from logging import StreamHandler
from pathlib import Path

from loguru import logger
from uvicorn import Config

from libs import app, db
from libs.server import UvicornService
from util import LoguruHandler

# 加载api
core_modules_path = Path('api')
for module in pkgutil.iter_modules([str(core_modules_path)]):
    importlib.import_module(f'api.{module.name}', f'api.{module.name}')


service = UvicornService(Config(app, host='127.0.0.1', port=8080))
loguru_handler = LoguruHandler()

logging.basicConfig(handlers=[loguru_handler], level=0, force=True)
for name in logging.root.manager.loggerDict:
    _logger = logging.getLogger(name)
    for handler in _logger.handlers:
        if isinstance(handler, StreamHandler):
            _logger.removeHandler(handler)

for name in "uvicorn.error", "uvicorn.asgi", "uvicorn.access":
    target = logging.getLogger(name)
    target.addHandler(loguru_handler)
    target.propagate = False

logger.remove()
logger.add(sys.stderr, level='INFO', enqueue=True)


async def main():
    await db.initialize()
    await service.start()
    await service.serve_task


loop = asyncio.get_event_loop()


try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    loop.run_until_complete(service.stop())
    logger.info("Received exit, exiting")
