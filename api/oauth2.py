from datetime import timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from launart import Launart

from libs.database.interface import Database
from libs.database.model import User
from libs.oauth2 import authenticate_user, create_token, get_password_hash
from libs.oauth2.model import Token
from libs.server import route
from util import BaseResponse, oauth2_scheme

ACCESS_TOKEN_EXPIRE_MINUTES = 120


@route.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_expires = timedelta(seconds=20)
    access_token = create_token(data={"sub": user.qq}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


@route.get("/whoami")
async def who_am_i(token=Depends(oauth2_scheme)):
    return token


@route.post("/add_user")
async def add_user(qq: int, passwd: str, token=Depends(oauth2_scheme)):
    db = Launart.current().get_interface(Database)
    try:
        await db.add(User(qq=qq, passwd=get_password_hash(passwd)))
    except Exception as e:
        return BaseResponse(code=500, message=str(e))
