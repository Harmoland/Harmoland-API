from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.sql import select

from libs import db
from libs.database.model import BannedQQList, BannedUUIDList
from libs.server import route
from util import BaseResponse


@route.post(
    "/api/ban_player",
    response_model=BaseResponse,
    summary='Ban 一个玩家（QQ群成员）',
    tags=['封禁'],
)
async def ban_player(
    qq: int,
    ban_start_time: int,
    ban_end_time: int,
    ban_reason: str,
    operater: int,
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
    # TODO: 搜索是否已有白名单，有的话就删除
    return BaseResponse()


@route.post(
    "/api/ban_uuid",
    response_model=BaseResponse,
    summary='Ban 一个 UUID',
    tags=['封禁'],
)
async def ban_uuid(
    uuid: UUID,
    ban_start_time: int,
    ban_end_time: int,
    ban_reason: str,
    operater: int,
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
    # TODO: 搜索是否已有白名单，有的话就删除
    return BaseResponse()


@route.post(
    "/api/pardon_player",
    response_model=BaseResponse,
    summary='解封一个玩家（QQ群成员）',
    description='',
    tags=['封禁'],
)
async def pardon_player(ban_id: int):
    result = await db.select_first(select(BannedQQList).where(BannedQQList.id == ban_id))
    if result is None:
        raise HTTPException(status_code=400, detail='该 BanID 不存在')
    await db.update_or_add(
        BannedQQList(
            id=result[0].id,
            qq=result[0].qq,
            banStartTime=result[0].ban_start_time,
            banEndTime=result[0].ban_end_time,
            banReason=result[0].ban_reason,
            pardon=True,
            operater=result[0].operater,
        )
    )
    return BaseResponse()


@route.post(
    "/api/pardon_uuid",
    response_model=BaseResponse,
    summary='解封一个UUID',
    description='',
    tags=['封禁'],
)
async def pardon_uuid(ban_id: int):
    result = await db.select_first(select(BannedUUIDList).where(BannedUUIDList.id == ban_id))
    if result is None:
        raise HTTPException(status_code=400, detail='该 BanID 不存在')
    await db.update_or_add(
        BannedUUIDList(
            id=result[0].id,
            uuid=result[0].uuid,
            banStartTime=result[0].ban_start_time,
            banEndTime=result[0].ban_end_time,
            banReason=result[0].ban_reason,
            pardon=True,
            operater=result[0].operater,
        )
    )
    return BaseResponse()
