from uuid import UUID

from fastapi import Depends, status
from launart import Launart
from loguru import logger
from sqlalchemy.sql import select

from libs.database.interface import Database
from libs.database.model import BannedQQList, BannedUUIDList, Player, UUIDList
from libs.server import route
from typings import HttpErrorResponse
from util import BaseResponse, get_rcon_client, oauth2_scheme
from util.minecraft import get_mc_id


@route.post(
    "/api/add_or_modify_player",
    response_model=BaseResponse,
    summary="添加或修改玩家（QQ群成员）",
    description="当有新成员入群时应通过该接口新增一个 Player，当群成员退群或被 T 时应通过该接口修改该 QQ 的退群时间然后移除白名单并将`hadWhitelist`修改为`false`",  # noqa: E501
    tags=["玩家"],
)
async def add_or_modify_player(
    qq: int,
    join_time: int | None = None,
    leave_time: int | None = None,
    inviter: int | None = None,
    had_whitelist: bool = False,
    ignore_ban: bool = False,
    token=Depends(oauth2_scheme),
):
    db = Launart.current().get_interface(Database)
    # 搜索是否已被Ban，有的话就拒绝
    if not ignore_ban:
        ban_info = await db.select_first(select(BannedQQList).where(BannedQQList.qq == qq))
        if ban_info is not None:
            return BaseResponse(code=status.HTTP_403_FORBIDDEN, message="该QQ号已被Ban")

    result = await db.select_first(select(Player).where(Player.qq == qq))
    flag = result is not None
    if result is not None:
        await db.update_or_add(
            Player(
                qq=qq,
                joinTime=join_time or result.joinTime,
                leaveTime=leave_time or result.leaveTime,
                inviter=inviter or result.inviter,
                hadWhitelist=had_whitelist or result.hadWhitelist,
            )
        )
    else:
        await db.update_or_add(
            Player(
                qq=qq,
                joinTime=join_time,
                leaveTime=leave_time,
                inviter=inviter,
                hadWhitelist=had_whitelist,
            )
        )
    if flag:
        return BaseResponse(message="Added!")
    else:
        return BaseResponse(message="Modified!")


@route.post(
    "/api/add_new_whitelist",
    response_model=BaseResponse | HttpErrorResponse,
    summary="添加新UUID（白名单）",
    description="该接口可以添加一个白名单，退群或被 T 或被 Ban 时应移除该白名单",
    tags=["白名单"],
)
async def add_new_whitelist(
    uuid: UUID, qq: int, add_time: int, operater: int, ignore_ban: bool = False, token=Depends(oauth2_scheme)
):
    db = Launart.current().get_interface(Database)
    # 搜索是否已被Ban，有的话就拒绝
    if not ignore_ban:
        ban_qq_info = await db.select_first(select(BannedQQList).where(BannedQQList.qq == qq))
        if ban_qq_info is not None:
            return BaseResponse(code=status.HTTP_403_FORBIDDEN, message="该QQ号已被Ban")
        ban_uuid_info = await db.select_first(select(BannedUUIDList).where(BannedUUIDList.uuid == uuid))
        if ban_uuid_info is not None:
            return BaseResponse(code=status.HTTP_403_FORBIDDEN, message="该UUID已被Ban")

    result = await db.select_first(select(UUIDList).where(UUIDList.uuid == UUID))
    if result is not None:
        return BaseResponse(code=status.HTTP_400_BAD_REQUEST, message="该UUID已被添加白名单")
    result = await db.select_first(select(Player).where(Player.qq == qq))
    if result is None:
        return BaseResponse(code=status.HTTP_400_BAD_REQUEST, message="请先添加该QQ号对应的Player")
    await db.update_or_add(
        Player(
            qq=qq,
            joinTime=result.joinTime,
            leaveTime=result.leaveTime,
            inviter=result.inviter,
            hadWhitelist=True,
        )
    )
    await db.update_or_add(UUIDList(uuid=uuid, qq=qq, wlAddTime=add_time, operater=operater))

    try:
        mc_id = await get_mc_id(uuid)
    except Exception as e:
        logger.exception(f"无法查询【{uuid}】对应的正版id", e)
        return BaseResponse(
            code=status.HTTP_204_NO_CONTENT,
            message=f"查询【{uuid}】对应的正版id时出错",
            data={"error": str(e)},
        )

    if not isinstance(mc_id, str):
        return HttpErrorResponse(
            code=mc_id.status,
            message=f"向 mojang 查询【{uuid}】的正版 id 时获得意外内容",
            data=mc_id,
        )

    rcon_client = await get_rcon_client()
    try:
        result = await rcon_client.send(f"whitelist add {mc_id}")
    except Exception as e:
        logger.exception(f"无法执行 Rcon 命令：【whitelist add {mc_id}】", e)
        return BaseResponse(
            code=status.HTTP_204_NO_CONTENT,
            message=f"无法执行 Rcon 命令：【whitelist add {mc_id}】",
            data={"error": str(e)},
        )
    else:
        return (
            BaseResponse()
            if result.startswith("Added")
            else BaseResponse(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=result)
        )
