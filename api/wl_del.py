from uuid import UUID

from fastapi import Depends, status
from launart import Launart
from loguru import logger
from sqlalchemy.sql import select

from libs.database.interface import Database
from libs.database.model import Player, UUIDList
from libs.server import route
from util import BaseResponse, get_rcon_client, oauth2_scheme
from util.minecraft import get_mc_id


@route.post(
    "/api/del_uuid",
    response_model=BaseResponse,
    summary="删除一个白名单",
    tags=["白名单"],
)
async def del_uuid(uuid: UUID, token=Depends(oauth2_scheme)):
    db = Launart.current().get_interface(Database)
    wl_result = await db.select_first(select(UUIDList).where(UUIDList.uuid == uuid))
    if wl_result is None:
        return BaseResponse(code=status.HTTP_400_BAD_REQUEST, message="该UUID没有白名单")

    qq = wl_result.qq
    failure: bool = False
    failure_message: str = "Failure"

    await db.delete_exist(wl_result)
    try:
        mc_id = await get_mc_id(uuid)
    except Exception as e:
        logger.exception(f"无法查询【{uuid}】对应的正版id", e)
        failure = True
        failure_message = f"无法查询【{uuid}】对应的正版id：{e}"
    else:
        if not isinstance(mc_id, str):
            logger.error(f"向 mojang 查询【{uuid}】的正版 id 时获得意外内容", mc_id)
        else:
            rcon_client = await get_rcon_client()
            try:
                result = await rcon_client.send(f"whitelist remove {mc_id}")
            except Exception as e:
                logger.exception(f"无法执行 Rcon 命令：【whitelist remove {mc_id}】", e)
            else:
                if not result.startswith("Removed"):
                    failure = True
                    failure_message = f"服务器返回意外内容：{result}"

    wl_result = await db.select_all(select(UUIDList).where(UUIDList.uuid == uuid))
    if not any(wl_result):
        player_result = await db.select_first(select(Player).where(Player.qq == qq))
        if player_result is not None and player_result.hadWhitelist:
            await db.update_or_add(
                Player(
                    qq=player_result.qq or qq,
                    joinTime=player_result.joinTime or None,
                    leaveTime=player_result.leaveTime or None,
                    inviter=player_result.inviter or None,
                    hadWhitelist=False,
                )
            )
    return BaseResponse(message=failure_message) if failure else BaseResponse()


@route.post(
    "/api/del_uuid_by_qq",
    response_model=BaseResponse,
    summary="删除一个QQ号对应的白名单",
    tags=["白名单"],
)
async def del_uuid_by_qq(qq: int, token=Depends(oauth2_scheme)):
    db = Launart.current().get_interface(Database)
    wl_result = await db.select_all(select(UUIDList).where(UUIDList.qq == qq))

    if not any(wl_result):
        return BaseResponse(code=status.HTTP_400_BAD_REQUEST, message="该QQ没有白名单")

    player_result = await db.select_first(select(Player).where(Player.qq == wl_result[0].qq))
    if player_result is not None and player_result.hadWhitelist:
        await db.update_or_add(
            Player(
                qq=player_result.qq or wl_result[0].qq,
                joinTime=player_result.joinTime or None,
                leaveTime=player_result.leaveTime or None,
                inviter=player_result.inviter or None,
                hadWhitelist=False,
            )
        )

    await db.delete_exist(wl_result)
    failure = []

    for wl in wl_result:
        try:
            mc_id = await get_mc_id(wl.uuid)
        except Exception as e:
            logger.exception(f"无法查询【{wl.uuid}】对应的正版id", e)
            failure.append({"uuid": wl.uuid, "message": f"无法查询【{wl.uuid}】对应的正版id"})
        else:
            if not isinstance(mc_id, str):
                logger.error(f"向 mojang 查询【{wl.uuid}】的正版 id 时获得意外内容", mc_id)
            else:
                rcon_client = await get_rcon_client()
                try:
                    result = await rcon_client.send(f"whitelist remove {mc_id}")
                except Exception as e:
                    logger.exception(f"无法执行 Rcon 命令：【whitelist remove {mc_id}】", e)
                else:
                    if not result.startswith("Removed"):
                        failure.append({"uuid": wl.uuid, "message": f"服务器返回意外内容：{result}"})
    if any(failure):
        return BaseResponse(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="error", data=failure)
    return BaseResponse()
