from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from libs.rcon.client import RconClient


class RconImpl:
    client: "RconClient"

    def __init__(self, client: "RconClient"):
        self.client = client

    if not TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any:
            return self.client.__getattribute__(name)


class RconStub:
    client: "RconClient"

    def __init__(self, client: "RconClient"):
        self.client = client

    async def send(self, command: str, *arguments: str) -> str:
        ...


Rcon = RconStub if TYPE_CHECKING else RconImpl
