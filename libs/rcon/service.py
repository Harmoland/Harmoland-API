from typing import Literal

from launart import ExportInterface, Launart, Service

from libs.rcon.client import RconClient
from libs.rcon.interface import Rcon


class RconService(Service):
    id = "rcon/client"
    supported_interface_types: set[type[ExportInterface]] | dict[type[ExportInterface], float] = {Rcon}
    client: RconClient
    host: str
    port: int
    passwd: str

    def __init__(
        self,
        host: str,
        port: int,
        *,
        passwd: str,
        encoding: str = 'utf-8',
    ) -> None:
        super().__init__()
        self.encoding = encoding
        self.host = host
        self.port = port
        self.passwd = passwd

    def get_interface(self, typ: type[Rcon]) -> Rcon:
        return Rcon(self.client)

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    @property
    def required(self) -> set[str | type[ExportInterface]]:
        return set()

    async def launch(self, _: Launart):
        async with self.stage("preparing"):
            self.client = RconClient(self.host, self.port, passwd=self.passwd)
            await self.client.connect()

        # print("after preparing")

        # async with self.stage("blocking"):
        #     print("Start blocking!")

        # print("after blocking")

        async with self.stage("cleanup"):
            await self.client.close()

        # print("before finish")
