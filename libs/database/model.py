from dataclasses import dataclass
from enum import Enum
from typing import Literal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm import mapped_column as col
from sqlalchemy.types import BIGINT, BOOLEAN, INTEGER, VARCHAR, Uuid


class Base(AsyncAttrs, DeclarativeBase):
    pass


@dataclass
class User(Base):
    __tablename__ = "harmoland_users"

    qq: Mapped[int] = col(BIGINT(), nullable=False, index=True, unique=True, primary_key=True)
    passwd: Mapped[str] = col(VARCHAR(260), nullable=False)


@dataclass
class Player(Base):
    __tablename__ = "harmoland_player"

    qq: Mapped[int] = col(BIGINT(), nullable=False, index=True, unique=True, primary_key=True)
    joinTime: Mapped[int | None] = col(BIGINT(), nullable=True, default=None, comment="入群时间")
    leaveTime: Mapped[int | None] = col(BIGINT(), nullable=True, default=None, comment="退群时间")
    inviter: Mapped[int | None] = col(BIGINT(), nullable=True, default=None, comment="邀请人QQ")
    hadWhitelist: Mapped[bool] = col(BOOLEAN(), nullable=False, default=False, comment="是否有白名单")


@dataclass
class UUIDList(Base):
    __tablename__ = "harmoland_uuid"

    uuid: Mapped[UUID] = col(Uuid(), nullable=False, index=True, unique=True, primary_key=True)
    qq: Mapped[int] = col(BIGINT(), nullable=False, index=True, comment="白名单对应QQ，非唯一")
    wlAddTime: Mapped[int] = col(BIGINT(), nullable=False, comment="白名单添加时间")
    operater: Mapped[int] = col(BIGINT(), nullable=False, comment="添加白名单操作者QQ")


@dataclass
class BannedUUIDList(Base):
    __tablename__ = "harmoland_banned_uuid"

    id: Mapped[int] = col(INTEGER(), primary_key=True)
    uuid: Mapped[UUID] = col(Uuid(), nullable=False, index=True, comment="被ban的uuid，非唯一")
    banStartTime: Mapped[int] = col(BIGINT(), nullable=False, comment="封禁时间")
    banEndTime: Mapped[int] = col(
        BIGINT(), nullable=False, comment="封禁结束时间，永封则应至少到2030年，需定期检查并解封，不用清空或删除"
    )  # noqa: E501
    banReason: Mapped[str] = col(VARCHAR(300), nullable=False, comment="封禁原因")
    pardon: Mapped[bool] = col(BOOLEAN(), nullable=False, default=False, comment="已解封")
    operater: Mapped[int] = col(BIGINT(), nullable=False, comment="封禁操作者QQ")


@dataclass
class BannedQQList(Base):
    __tablename__ = "harmoland_banned_qq"

    id: Mapped[int] = col(INTEGER(), primary_key=True)
    qq: Mapped[int] = col(BIGINT(), nullable=False, index=True, comment="被ban的qq，非唯一")
    banStartTime: Mapped[int] = col(BIGINT(), nullable=False, comment="封禁时间")
    banEndTime: Mapped[int] = col(
        BIGINT(), nullable=False, comment="封禁结束时间，永封则应至少到2030年，需定期检查并解封，不用清空或删除"
    )  # noqa: E501
    banReason: Mapped[str] = col(VARCHAR(300), nullable=False, comment="封禁原因")
    pardon: Mapped[bool] = col(BOOLEAN(), nullable=False, default=False, comment="已解封")
    operater: Mapped[int] = col(BIGINT(), nullable=False, comment="封禁操作者QQ")


class Operate(Enum):
    newMember = 0
    addWhitelist = 1
    delWhitelist = 2
    banUUID = 3
    banQQ = 4
    pardonUUID = 5
    pardonQQ = 6
    login = 7
    getBannedQQ = 8
    getBannedUUID = 9
    getPlayersList = 10
    getPlayerInfo = 11


# @dataclass
# class OperateLog(Base):
#     __tablename__ = "harmoland_operate_log"

#     id: Mapped[int] = col(INTEGER(), primary_key=True)
#     operater: Mapped[int] = col(BIGINT(), nullable=False, index=True, comment="操作者")
#     type: Mapped[Literal['add', 'ban', 'pardon', 'login', 'del', 'get']]
