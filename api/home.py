from libs.server import route
from util import BaseModel, BaseResponse


class HomeItem(BaseModel):
    player_count: int
    white_count: int


@route.get("/api/home", response_model=BaseResponse)
async def home():
    return BaseResponse(data=HomeItem(player_count=114, white_count=514))
