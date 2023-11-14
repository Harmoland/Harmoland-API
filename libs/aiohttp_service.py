from __future__ import annotations

from typing import Any, cast

from aiohttp import ClientSession, ClientTimeout
from launart.manager import Launart, Service


class AiohttpClientInterface:
    def __init__(self, service: AiohttpClientService) -> None:
        self.service = service


class AiohttpClientService(Service):
    id = "http.client/aiohttp"
    session: ClientSession
    supported_interface_types: set[Any] = {AiohttpClientInterface}

    def __init__(self, session: ClientSession | None = None) -> None:
        self.session = cast(ClientSession, session)
        super().__init__()

    def get_interface(self, _):
        return AiohttpClientInterface(self)

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    @property
    def required(self) -> set[str]:
        return set()

    async def launch(self, mgr: Launart):
        async with self.stage("preparing"):
            if not self.session:
                self.session = ClientSession(timeout=ClientTimeout(total=None))
        async with self.stage("cleanup"):
            await self.session.close()
