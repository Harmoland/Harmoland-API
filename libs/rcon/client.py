from asyncio import StreamReader, StreamWriter, open_connection

from loguru import logger
from rcon.exceptions import SessionTimeout, WrongPassword
from rcon.source.proto import Packet, Type


class RconClient:
    reader: StreamReader
    writer: StreamWriter
    connected: bool = False
    host: str
    port: int
    passwd: str
    frag_threshold: int
    frag_detect_cmd: str
    retry_count: int = 0

    def __init__(
        self,
        host: str,
        port: int,
        *,
        passwd: str,
        encoding: str = "utf-8",
        frag_threshold: int = 4096,
        frag_detect_cmd: str = "",
    ) -> None:
        self.encoding = encoding
        self.host = host
        self.port = port
        self.passwd = passwd
        self.frag_threshold = frag_threshold
        self.frag_detect_cmd = frag_detect_cmd

    async def connect(self):
        if self.connected:
            return
        try:
            self.reader, self.writer = await open_connection(self.host, self.port)
            response = await self.communicate(Packet.make_login(self.passwd, encoding=self.encoding))
        except Exception as e:
            logger.exception("Failed to connect rcon server", e)
        else:
            # Wait for SERVERDATA_AUTH_RESPONSE according to:
            # https://developer.valvesoftware.com/wiki/Source_RCON_Protocol
            while response.type != Type.SERVERDATA_AUTH_RESPONSE:
                response = await Packet.aread(self.reader)

            if response.id == -1:
                await self.close()
                raise WrongPassword()

            self.connected = True

    async def close(self) -> None:
        """Close socket asynchronously."""
        if self.connected:
            self.writer.close()
            await self.writer.wait_closed()
            self.connected = False

    async def communicate(
        self,
        packet: Packet,
    ) -> Packet:
        """Make an asynchronous request."""
        self.writer.write(bytes(packet))
        await self.writer.drain()
        response = await Packet.aread(self.reader)

        if len(response.payload) < self.frag_threshold:
            return response

        self.writer.write(bytes(Packet.make_command(self.frag_detect_cmd)))
        await self.writer.drain()

        while (successor := await Packet.aread(self.reader)).id == response.id:
            response += successor

        return response

    async def send(self, command: str, *arguments: str) -> str:
        """Run a command asynchronously."""
        if not self.connected:
            await self.connect()
        request = Packet.make_command(command, *arguments, encoding=self.encoding)
        response = await self.communicate(request)

        if response.id != request.id:
            raise SessionTimeout()

        return response.payload.decode(self.encoding)
