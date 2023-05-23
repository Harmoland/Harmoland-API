import asyncio
import importlib
import pkgutil
from pathlib import Path

from uvicorn import Config

from libs import app, db
from libs.server import UvicornService

# 加载api
core_modules_path = Path('api')
for module in pkgutil.iter_modules([str(core_modules_path)]):
    importlib.import_module(f'api.{module.name}', f'api.{module.name}')


service = UvicornService(Config(app, host='127.0.0.1', port=8080))


async def main():
    await db.initialize()
    await service.start()
    await service.serve_task


loop = asyncio.get_event_loop()


try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    loop.run_until_complete(service.stop())
    print("Received exit, exiting")
