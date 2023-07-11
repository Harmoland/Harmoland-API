from pydantic import BaseModel

from util import BaseResponse


class HttpResp(BaseModel):
    status: int
    headers: dict[str, str]
    charset: str | None
    content: str


class HttpErrorResponse(BaseResponse):
    data: HttpResp
