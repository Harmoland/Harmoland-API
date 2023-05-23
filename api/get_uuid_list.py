from typing import List
from uuid import UUID

from sqlalchemy.sql import select

from libs import db
from libs.database.model import UUIDList
from libs.server import route
from util import BaseModel, BaseResponse


class BannedUUID(BaseModel):
    uuid: UUID
    banStartTime: int
    banEndTime: int
    banReason: str
    operater: int

    class Config:
        orm_mode = True


class UUIDInfo(BaseModel):
    uuid: UUID
    qq: int
    wlAddTime: int
    operater: int
    banned: bool = False

    class Config:
        orm_mode = True


class UUIDListResponse(BaseResponse):
    data: List[UUIDInfo]


@route.get(
    "/api/get_uuid_list",
    response_model=UUIDListResponse,
    summary='获取所有白名单的列表',
    tags=['白名单'],
)
async def get_uuid_list():
    all_uuid = await db.select_all(select(UUIDList))
    return UUIDListResponse(data=[_[0] for _ in all_uuid])
