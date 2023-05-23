from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.sql import select

from libs import db
from libs.database.model import Player, UUIDList
from libs.server import route
from util import BaseResponse


@route.post(
    "/api/add_or_modify_player",
    response_model=BaseResponse,
    summary='添加或修改玩家（QQ群成员）',
    description='当有新成员入群时应通过该接口新增一个 Player，当群成员退群或被 T 时应通过该接口修改该 QQ 的退群时间然后移除白名单并将`hadWhitelist`修改为`false`',
    tags=['玩家'],
)
async def add_or_modify_player(
    qq: int,
    join_time: int | None = None,
    leave_time: int | None = None,
    inviter: int | None = None,
    had_whitelist: bool = False,
):
    # TODO: 搜索是否已被Ban，有的话就拒绝
    result = await db.select_first(select(Player).where(Player.qq == qq))
    flag = result is not None
    if result is not None:
        await db.update_or_add(
            Player(
                qq=qq,
                joinTime=join_time or result[0].joinTime,
                leaveTime=leave_time or result[0].leaveTime,
                inviter=inviter or result[0].inviter,
                hadWhitelist=had_whitelist or result[0].hadWhitelist,
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
        return BaseResponse(message='Added!')
    else:
        return BaseResponse(message='Modified!')


@route.post(
    "/api/add_new_whitelist",
    response_model=BaseResponse,
    summary='添加新UUID（白名单）',
    description='该接口可以添加一个白名单，退群或被 T 或被 Ban 时应移除该白名单',
    tags=['白名单'],
)
async def add_new_whitelist(
    uuid: UUID,
    qq: int,
    add_time: int,
    operater: int,
):
    # TODO: 搜索是否已被Ban，有的话就拒绝
    result = await db.select_first(select(UUIDList).where(UUIDList.uuid == UUID))
    if result is not None:
        raise HTTPException(status_code=400, detail="该UUID已被添加白名单")
    result = await db.select_first(select(Player).where(Player.qq == qq))
    if result is None:
        raise HTTPException(status_code=400, detail="请先添加该QQ号对应的Player")
    await db.update_or_add(
        Player(
            qq=qq,
            joinTime=result[0].joinTime,
            leaveTime=result[0].leaveTime,
            inviter=result[0].inviter,
            hadWhitelist=True,
        )
    )
    await db.update_or_add(UUIDList(uuid=uuid, qq=qq, wlAddTime=add_time, operater=operater))
    return BaseResponse()
