import secrets
from collections.abc import Mapping
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from launart import Launart
from passlib.context import CryptContext
from sqlalchemy.sql import select

from libs.database.interface import Database
from libs.database.model import User

# to get a string like this run:
# openssl rand -hex 32
# SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
SECRET_KEY = secrets.token_urlsafe(64)
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UnauthorizedException(HTTPException):
    def __init__(self, detail="Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_user(qq: str) -> User | None:
    """从数据库中查询用户信息."""
    db = Launart.current().get_interface(Database)
    return await db.select_first(select(User).where(User.qq == qq))


def verify_password(plain_password, hashed_password) -> bool:
    """验证密码.

    Args:
        plain_password(str): 明文密码
        hashed_password(str): 哈希后的密码
    Returns:
        bool: 验证结果
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(plain_password) -> str:
    """获取哈希后的密码.

    Args:
        plain_password(str): 明文密码
    Returns:
        hashed_password(str): 哈希后的密码.
    """
    return pwd_context.hash(plain_password)


async def authenticate_user(qq: str, plain_password: str) -> User:
    """验证用户名和密码.

    Args:
        qq(str): QQ号
        plain_password(str): 明文密码
    Returns:
        user(User): 用户信息
    """
    user = await get_user(qq)
    if user is None:
        raise UnauthorizedException(detail="无效的用户名或密码")
    if not verify_password(plain_password, user.passwd):
        raise UnauthorizedException(detail="无效的用户名或密码")
    return user


def create_token(
    data: dict,
    expires_delta: timedelta | None = timedelta(minutes=30),
    scopes: list[str] | None = None,
) -> str:
    """创建 JWT Token.

    Args:
        data(dict): 包含用户信息的字典. {'sub': user_info}
        expires_delta(Optional[timedelta]): Token 过期时间，默认为 30分钟
        scopes(Optional[list[str]]): Token 授权范围，默认为 None
    Returns:
        token(str): JWT Token
    """
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode["exp"] = expire

    if scopes is not None:
        to_encode["scopes"] = scopes

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
        headers={"typ": "JWT", "alg": ALGORITHM},
    )


async def verify_token(token: str = Depends(oauth2_scheme)) -> User:
    """获取当前用户信息.

    用于验证用户是否登录，作为 FastAPI 的 Depends 使用

    Args:
        token(str): JWT Token
    Returns:
        user(User): 用户信息
    """
    try:
        payload: Mapping = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        qq: str = payload.get("sub", None)
        if qq is None:
            raise UnauthorizedException(detail="无效的用户")
    except JWTError as e:
        raise UnauthorizedException(detail="无效的 Token 或 Token 已过期") from e
    user = await get_user(qq=qq)
    if user is None:
        raise UnauthorizedException(detail="无效的用户")
    return user
