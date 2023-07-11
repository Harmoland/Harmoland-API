from uuid import UUID

from fastapi import Depends, status
from sqlalchemy.sql import select

from libs.database import db
from libs.database.model import Player, UUIDList
from libs.server import route
from util import BaseResponse, oauth2_scheme


@route.post(
    "/api/del_uuid",
    response_model=BaseResponse,
    summary="删除一个白名单",
    tags=["白名单"],
)
async def del_uuid(uuid: UUID, token=Depends(oauth2_scheme)):
    wl_result = await db.select_first(select(UUIDList).where(UUIDList.uuid == uuid))
    if wl_result is None:
        return BaseResponse(code=status.HTTP_400_BAD_REQUEST, message="该UUID没有白名单")
    await db.delete_exist(wl_result)

    wl_result = await db.select_all(select(UUIDList).where(UUIDList.uuid == uuid))
    if wl_result is None or len(wl_result) == 0:
        player_result = await db.select_first(select(Player).where(Player.qq == wl_result[0].qq))
        if player_result is not None and player_result[0].hadWhitelist:
            await db.update_or_add(
                Player(
                    qq=player_result[0].qq or wl_result[0].qq,
                    joinTime=player_result[0].joinTime or None,
                    leaveTime=player_result[0].leaveTime or None,
                    inviter=player_result[0].inviter or None,
                    hadWhitelist=False,
                )
            )
    return BaseResponse()


@route.post(
    "/api/del_uuid_by_qq",
    response_model=BaseResponse,
    summary="删除一个QQ号对应的白名单",
    tags=["白名单"],
)
async def del_uuid_by_qq(qq: int, token=Depends(oauth2_scheme)):
    wl_result = await db.select_all(select(UUIDList).where(UUIDList.qq == qq))

    if wl_result is None or len(wl_result) == 0:
        return BaseResponse(code=status.HTTP_400_BAD_REQUEST, message="该QQ没有白名单")

    player_result = await db.select_first(select(Player).where(Player.qq == wl_result[0].qq))
    if player_result is not None and player_result[0].hadWhitelist:
        await db.update_or_add(
            Player(
                qq=player_result[0].qq or wl_result[0].qq,
                joinTime=player_result[0].joinTime or None,
                leaveTime=player_result[0].leaveTime or None,
                inviter=player_result[0].inviter or None,
                hadWhitelist=False,
            )
        )

    await db.delete_exist(wl_result)
    return BaseResponse()
