from launart import Launart
from loguru import logger

from libs.rcon.interface import Rcon
from libs.server import route


@route.post("/rcon")
async def rcon(command: str):
    """JUST FOR DEVELOPMENT ONLY"""
    launart = Launart.current()
    rcon = launart.get_interface(Rcon)

    logger.info(await rcon.send(command))
