# import asyncio
# from collections.abc import Coroutine, Iterable

# from uvicorn import Config, Server


# async def wait_fut(
#     coros: Iterable[Coroutine | asyncio.Task],
#     *,
#     timeout: float | None = None,
#     return_when: str = asyncio.ALL_COMPLETED,
# ) -> None:
#     tasks = []
#     for c in coros:
#         if asyncio.iscoroutine(c):
#             tasks.append(asyncio.create_task(c))
#         else:
#             tasks.append(c)
#     if tasks:
#         await asyncio.wait(tasks, timeout=timeout, return_when=return_when)


# class WithoutSigHandlerServer(Server):
#     def install_signal_handlers(self) -> None:
#         pass


# class UvicornService:
#     def __init__(self, config: Config) -> None:
#         self.server = WithoutSigHandlerServer(config)

#     async def start(self):
#         self.serve_task = asyncio.create_task(self.server.serve())

#     async def stop(self):
#         self.server.should_exit = True
#         await wait_fut([self.serve_task, asyncio.sleep(10)], return_when=asyncio.FIRST_COMPLETED)
#         if not self.serve_task.done():
#             self.server.force_exit = True

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

fastapi = FastAPI(
    title="Harmoland Console",
    description="API of Harmoland Console",
    default_response_class=ORJSONResponse,
)

fastapi.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
