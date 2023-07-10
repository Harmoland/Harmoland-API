import asyncio
from collections.abc import Coroutine, Iterable
from typing import Optional, Union

from uvicorn import Config, Server


async def wait_fut(
    coros: Iterable[Coroutine | asyncio.Task],
    *,
    timeout: float | None = None,
    return_when: str = asyncio.ALL_COMPLETED,
) -> None:
    tasks = []
    for c in coros:
        if asyncio.iscoroutine(c):
            tasks.append(asyncio.create_task(c))
        else:
            tasks.append(c)
    if tasks:
        await asyncio.wait(tasks, timeout=timeout, return_when=return_when)


class WithoutSigHandlerServer(Server):
    def install_signal_handlers(self) -> None:
        pass


class UvicornService:
    def __init__(self, config: Config) -> None:
        self.server = WithoutSigHandlerServer(config)

    async def start(self):
        self.serve_task = asyncio.create_task(self.server.serve())

    async def stop(self):
        self.server.should_exit = True
        await wait_fut([self.serve_task, asyncio.sleep(10)], return_when=asyncio.FIRST_COMPLETED)
        if not self.serve_task.done():
            self.server.force_exit = True
