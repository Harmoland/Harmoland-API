from __future__ import annotations

import functools
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

from fastapi import routing
from fastapi.datastructures import Default
from fastapi.encoders import DictIntStrAny, SetIntStr
from fastapi.params import Depends
from fastapi.utils import generate_unique_id
from starlette.responses import JSONResponse, Response
from typing_extensions import Concatenate, ParamSpec

from .. import app

Method = Literal["GET", "PUT", "POST", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE"]

T_Callable = TypeVar("T_Callable", bound=Callable)
Wrapper = Callable[[T_Callable], T_Callable]
P = ParamSpec("P")
R = TypeVar("R")


if TYPE_CHECKING:

    def route(
        methods: List[Method],
        path: str,
        response_model: Any = Default(None),
        status_code: Optional[int] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
        dependencies: Optional[Sequence[Depends]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        deprecated: Optional[bool] = None,
        operation_id: Optional[str] = None,
        response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
        response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        response_model_exclude_defaults: bool = False,
        response_model_exclude_none: bool = False,
        include_in_schema: bool = True,
        response_class: Type[Response] = Default(JSONResponse),
        name: Optional[str] = None,
        openapi_extra: Optional[Dict[str, Any]] = None,
        generate_unique_id_function: Callable[[routing.APIRoute], str] = Default(generate_unique_id),
    ) -> Wrapper:
        ...

else:

    def route(methods: List[Method], path: str, **params: Any):
        return app.api_route(path, methods=methods, **params)


def __wrap_route(method: Method, func: Callable[Concatenate[List[Method], P], R] = route) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func([method], *args, **kwargs)

    return wrapper


websocket = app.websocket

ws = websocket

get = __wrap_route("GET")

put = __wrap_route("PUT")

post = __wrap_route("POST")

delete = __wrap_route("DELETE")

options = __wrap_route("OPTIONS")

head = __wrap_route("HEAD")

patch = __wrap_route("PATCH")

trace = __wrap_route("TRACE")
