from fastapi import Depends

from libs.server import route
from util import BaseModel, BaseResponse, oauth2_scheme


class HomeItem(BaseModel):
    player_count: int
    white_count: int


@route.get("/api/home", response_model=BaseResponse)
async def home(token=Depends(oauth2_scheme)):
    return BaseResponse(data=HomeItem(player_count=114, white_count=514))
