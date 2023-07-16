from uuid import UUID

from fastapi import Depends, status
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.sql import select

from libs.database import db
from libs.database.model import BannedQQList, BannedUUIDList, Player, UUIDList
from libs.server import route
from util import BaseResponse, get_rcon_client, oauth2_scheme
from util.minecraft import get_mc_id


class BanResult(BaseModel):
    success_uuid: list[UUID]
    failed_uuid: list[UUID]
    success_remove_whitelist_id: list[str]
    failed_remove_whitelist_id: list[str]
    success_ban_id: list[str]
    failed_ban_id: list[str]


class BanResponse(BaseResponse):
    data: BanResult


@route.post("/api/ban_player", response_model=BanResponse, summary="Ban 一个玩家（QQ群成员）", tags=["封禁"])
async def ban_player(
    qq: int, ban_start_time: int, ban_end_time: int, ban_reason: str, operater: int, token=Depends(oauth2_scheme)
):
    await db.add(
        BannedQQList(
            qq=qq,
            banStartTime=ban_start_time,
            banEndTime=ban_end_time,
            banReason=ban_reason,
            operater=operater,
        )
    )

    # 搜索是否已有白名单
    wl_result = await db.select_all(select(UUIDList).where(UUIDList.qq == qq))
    if not any(wl_result):
        return BaseResponse()

    # 有白名单，删除白名单
    await db.delete_exist(wl_result)
    success_uuid: list[UUID] = []
    failed_uuid: list[UUID] = []
    ids: list[str] = []
    for wl in wl_result:
        uuid = wl.uuid
        try:
            mc_id = await get_mc_id(uuid)
        except Exception as e:
            logger.exception(f"无法查询【{uuid}】对应的正版id", e)
            failed_uuid.append(uuid)
        else:
            if not isinstance(mc_id, str):
                failed_uuid.append(uuid)
                logger.error(f"向 mojang 查询【{uuid}】的正版 id 时获得意外内容", mc_id)
            else:
                success_uuid.append(uuid)
                ids.append(mc_id)

    success_remove_whitelist_id: list[str] = []
    failed_remove_whitelist_id: list[str] = []
    success_ban_id: list[str] = []
    failed_ban_id: list[str] = []
    rcon_client = await get_rcon_client()
    for mc_id in ids:
        try:
            result = await rcon_client.send(f"whitelist remove {mc_id}")
        except Exception as e:
            logger.exception(f"无法执行 Rcon 命令：【whitelist remove {mc_id}】", e)
        else:
            if result.startswith("Removed"):
                success_remove_whitelist_id.append(mc_id)
            else:
                failed_remove_whitelist_id.append(mc_id)
    for mc_id in ids:
        try:
            result = await rcon_client.send(f"ban {mc_id} {ban_reason}")
        except Exception as e:
            logger.exception(f"无法执行 Rcon 命令：【ban {mc_id} {ban_reason}】", e)
        else:
            if result.startswith("Banned"):
                success_ban_id.append(mc_id)
            else:
                failed_ban_id.append(mc_id)

    # 删除白名单后将玩家标记为无白名单
    if (not any(failed_remove_whitelist_id)) and (not any(failed_uuid)):
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

    return BanResponse(
        data=BanResult(
            success_uuid=success_uuid,
            failed_uuid=failed_uuid,
            success_remove_whitelist_id=success_remove_whitelist_id,
            failed_remove_whitelist_id=failed_remove_whitelist_id,
            success_ban_id=success_ban_id,
            failed_ban_id=failed_ban_id,
        )
    )


@route.post(
    "/api/ban_uuid",
    response_model=BaseResponse,
    summary="Ban 一个 UUID",
    tags=["封禁"],
)
async def ban_uuid(
    uuid: UUID, ban_start_time: int, ban_end_time: int, ban_reason: str, operater: int, token=Depends(oauth2_scheme)
):
    await db.add(
        BannedUUIDList(
            uuid=uuid,
            banStartTime=ban_start_time,
            banEndTime=ban_end_time,
            banReason=ban_reason,
            operater=operater,
        )
    )

    # 搜索是否已有白名单
    wl_result = await db.select_first(select(UUIDList).where(UUIDList.uuid == uuid))
    if wl_result is None:
        return BaseResponse()

    qq = wl_result.qq
    failure: bool = False
    failure_message: str = 'Failure'

    # 有白名单，删除白名单
    await db.delete_exist(wl_result)
    try:
        mc_id = await get_mc_id(uuid)
    except Exception as e:
        logger.exception(f"无法查询【{uuid}】对应的正版id", e)
        failure = True
        failure_message = f"无法查询【{uuid}】对应的正版id: {e}"
    else:
        if not isinstance(mc_id, str):
            logger.error(f"向 mojang 查询【{uuid}】的正版 id 时获得意外内容", mc_id)
            failure = True
            failure_message = f"向 mojang 查询【{uuid}】的正版 id 时获得意外内容: {mc_id.content}"
        else:
            rcon_client = await get_rcon_client()
            try:
                result = await rcon_client.send(f"whitelist remove {mc_id}")
            except Exception as e:
                logger.exception(f"无法执行 Rcon 命令：【whitelist remove {mc_id}】", e)
                failure = True
                failure_message = f"无法执行 Rcon 命令：【whitelist remove {mc_id}】: {e}"
            else:
                if not result.startswith("Removed"):
                    failure = True
                    failure_message = f"服务器返回意外内容：{result}"

            try:
                result = await rcon_client.send(f"ban {mc_id} {ban_reason}")
            except Exception as e:
                logger.exception(f"无法执行 Rcon 命令：【ban {mc_id} {ban_reason}】", e)
                failure = True
                failure_message = f"无法执行 Rcon 命令：【ban {mc_id} {ban_reason}】: {e}"
            else:
                if not result.startswith("Banned"):
                    failure = True
                    failure_message = f"服务器返回意外内容：{result}"

    # 删除白名单后，若玩家无白名单则将玩家标记为无白名单
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
    "/api/pardon_player",
    response_model=BaseResponse,
    summary="解封一个玩家（QQ群成员）",
    description="",
    tags=["封禁"],
)
async def pardon_player(ban_id: int, token=Depends(oauth2_scheme)):
    result = await db.select_first(select(BannedQQList).where(BannedQQList.qq == ban_id))
    if result is None:
        return BaseResponse(code=status.HTTP_400_BAD_REQUEST, message="该 BanID 不存在")
    await db.update_or_add(
        BannedQQList(
            id=result.id,
            qq=result.qq,
            banStartTime=result.banStartTime,
            banEndTime=result.banEndTime,
            banReason=result.banReason,
            pardon=True,
            operater=result.operater,
        )
    )
    return BaseResponse()


@route.post(
    "/api/pardon_uuid",
    response_model=BaseResponse,
    summary="解封一个UUID",
    description="",
    tags=["封禁"],
)
async def pardon_uuid(ban_id: UUID, token=Depends(oauth2_scheme)):
    result = await db.select_first(select(BannedUUIDList).where(BannedUUIDList.uuid == ban_id))
    if result is None:
        return BaseResponse(code=status.HTTP_400_BAD_REQUEST, message="该 BanID 不存在")
    await db.update_or_add(
        BannedUUIDList(
            id=result.id,
            uuid=result.uuid,
            banStartTime=result.banStartTime,
            banEndTime=result.banEndTime,
            banReason=result.banReason,
            pardon=True,
            operater=result.operater,
        )
    )
    failure: bool = False
    failure_message: str = 'Failure'
    try:
        mc_id = await get_mc_id(result.uuid)
    except Exception as e:
        logger.exception(f"无法查询【{result.uuid}】对应的正版id", e)
        failure = True
        failure_message = f"无法查询【{result.uuid}】对应的正版id: {e}"
    else:
        if not isinstance(mc_id, str):
            logger.error(f"向 mojang 查询【{result.uuid}】的正版 id 时获得意外内容", mc_id)
            failure = True
            failure_message = f"向 mojang 查询【{result.uuid}】的正版 id 时获得意外内容: {mc_id.content}"
        else:
            rcon_client = await get_rcon_client()
            try:
                result = await rcon_client.send(f"padron {mc_id}")
            except Exception as e:
                logger.exception(f"无法执行 Rcon 命令：【padron {mc_id}】", e)
                failure = True
                failure_message = f"无法执行 Rcon 命令：【padron {mc_id}】: {e}"
            else:
                if not result.startswith("Unbanned"):
                    failure = True
                    failure_message = f"服务器返回意外内容：{result}"

    return BaseResponse(message=failure_message) if failure else BaseResponse()
