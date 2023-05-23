from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.sql import select

from libs import db
from libs.database.model import Player, UUIDList
from libs.server import route
from util import BaseResponse


@route.post(
    "/api/del_uuid",
    response_model=BaseResponse,
    summary='删除一个白名单',
    tags=['白名单'],
)
async def del_uuid(uuid: UUID):
    wl_result = await db.select_first(select(UUIDList).where(UUIDList.uuid == uuid))
    if wl_result is None:
        raise HTTPException(status_code=400, detail='该UUID没有白名单')
    await db.delete_exist(wl_result)

    wl_result = await db.select_all(select(UUIDList).where(UUIDList.uuid == uuid))
    if wl_result is None or len(wl_result) == 0:
        player_result = await db.select_first(select(Player).where(Player.qq == wl_result[0].qq))
        if player_result is not None and player_result[0].hadWhitelist:
            await db.update_or_add(
                Player(
                    qq=player_result[0].qq,
                    joinTime=player_result[0].joinTime,
                    leaveTime=player_result[0].leaveTime,
                    inviter=player_result[0].inviter,
                    hadWhitelist=False,
                )
            )
    return BaseResponse()
