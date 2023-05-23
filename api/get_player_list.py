from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.sql import select

from libs import db
from libs.database.model import BannedQQList, Player, UUIDList
from libs.server import route
from util import BaseModel, BaseResponse


class PlayerInfo(BaseModel):
    qq: int
    joinTime: int | None
    leaveTime: int | None
    inviter: int | None
    hadWhitelist: bool

    class Config:
        orm_mode = True


class PlayersResponse(BaseResponse):
    data: list[PlayerInfo]


@route.get(
    "/api/get_playerlist",
    response_model=PlayersResponse,
    summary='获取所有玩家列表',
    tags=['玩家'],
)
async def get_players_list():
    result = await db.select_all(select(Player))
    if result is None:
        raise HTTPException(status_code=404, detail="未知的玩家")
    return PlayersResponse(data=[_[0] for _ in result])


class WLInfo(BaseModel):
    uuid: UUID
    wlAddTime: int
    operater: int

    class Config:
        orm_mode = True


class BannedQQ(BaseModel):
    qq: int
    banStartTime: int
    banEndTime: int
    banReason: str
    operater: int

    class Config:
        orm_mode = True


class PlayerInfoFull(BaseModel):
    basic: PlayerInfo
    banInfo: BannedQQ | None
    whitelistInfo: List[WLInfo] | None


class PlayerResponse(BaseResponse):
    data: PlayerInfoFull


@route.get(
    "/api/get_player_info",
    response_model=PlayerResponse,
    summary='获取单个玩家/UUID的信息',
    tags=['玩家', '白名单'],
)
async def get_single_player_info(qq: int | None = None, uuid: UUID | None = None):
    # sourcery skip: remove-redundant-if
    if qq is None and uuid is not None:
        wl_info = await db.select_first(select(UUIDList).where(UUIDList.uuid == uuid))
        if wl_info is None:
            raise HTTPException(status_code=404, detail="未知的玩家")
        info = await db.select_first(select(Player).where(Player.qq == wl_info[0].qq))
        ban_info = await db.select_first(select(BannedQQList).where(BannedQQList.qq == wl_info[0].qq))
        ban_info = None if ban_info is None else ban_info[0]
        wl_info = await db.select_all(select(UUIDList).where(UUIDList.qq == wl_info[0].qq))
        return PlayerResponse(
            data={'basic': info[0], 'banInfo': ban_info, 'whitelistInfo': [_[0] for _ in wl_info]}  # type: ignore
        )
    elif qq is not None and uuid is None:
        info = await db.select_first(select(Player).where(Player.qq == qq))
        if info is None:
            raise HTTPException(status_code=404, detail="未知的玩家")
        ban_info = await db.select_first(select(BannedQQList).where(BannedQQList.qq == qq))
        ban_info = None if ban_info is None else ban_info[0]
        wl_info = await db.select_all(select(UUIDList).where(UUIDList.qq == qq))
        return PlayerResponse(
            data={'basic': info[0], 'banInfo': ban_info, 'whitelistInfo': [_[0] for _ in wl_info]}  # type: ignore
        )
    elif qq is None and uuid is None:
        raise HTTPException(status_code=400, detail="参数错误，至少需要传入一个参数")
    else:
        raise HTTPException(status_code=400, detail="参数错误，QQ和UUID不可同时传入")
