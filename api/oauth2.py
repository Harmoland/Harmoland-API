from datetime import timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from libs.oauth2 import authenticate_user, create_token
from libs.oauth2.model import Token
from libs.server import route
from util import oauth2_scheme

ACCESS_TOKEN_EXPIRE_MINUTES = 120


@route.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_expires = timedelta(seconds=20)
    access_token = create_token(data={"sub": user.qq}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


@route.get('/whoami')
async def who_am_i(token=Depends(oauth2_scheme)):
    return token
