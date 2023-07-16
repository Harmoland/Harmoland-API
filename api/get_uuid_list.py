from typing import cast
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.sql import select

from libs.database import db
from libs.database.model import UUIDList
from libs.server import route
from util import BaseResponse, oauth2_scheme


class BannedUUID(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    banStartTime: int
    banEndTime: int
    banReason: str
    operater: int


class UUIDInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    qq: int
    wlAddTime: int
    operater: int
    banned: bool = False


class UUIDListResponse(BaseResponse):
    data: list[UUIDInfo]


@route.get(
    "/api/get_uuid_list",
    response_model=UUIDListResponse,
    summary="获取所有白名单的列表",
    tags=["白名单"],
)
async def get_uuid_list(token=Depends(oauth2_scheme)):
    all_uuid = await db.select_all(select(UUIDList))
    return UUIDListResponse(data=[cast(UUIDInfo, _[0]) for _ in all_uuid])
