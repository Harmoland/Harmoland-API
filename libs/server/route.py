import functools
from collections.abc import Callable, Sequence
from enum import Enum
from typing import TYPE_CHECKING, Any, Concatenate, Literal, TypeVar

from fastapi import routing
from fastapi.datastructures import Default
from fastapi.params import Depends
from fastapi.types import IncEx
from fastapi.utils import generate_unique_id
from starlette.responses import JSONResponse, Response
from typing_extensions import ParamSpec

from libs.server import fastapi

Method = Literal["GET", "PUT", "POST", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE"]

T_Callable = TypeVar("T_Callable", bound=Callable)
Wrapper = Callable[[T_Callable], T_Callable]
P = ParamSpec("P")
R = TypeVar("R")


if TYPE_CHECKING:

    def route(
        methods: list[Method],
        path: str,
        response_model: Any = Default(None),
        status_code: int | None = None,
        tags: list[str | Enum] | None = None,
        dependencies: Sequence[Depends] | None = None,
        summary: str | None = None,
        description: str | None = None,
        response_description: str = "Successful Response",
        responses: dict[int | str, dict[str, Any]] | None = None,
        deprecated: bool | None = None,
        operation_id: str | None = None,
        response_model_include: IncEx | None = None,
        response_model_exclude: IncEx | None = None,
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        response_model_exclude_defaults: bool = False,
        response_model_exclude_none: bool = False,
        include_in_schema: bool = True,
        response_class: type[Response] = Default(JSONResponse),
        name: str | None = None,
        openapi_extra: dict[str, Any] | None = None,
        generate_unique_id_function: Callable[[routing.APIRoute], str] = Default(generate_unique_id),
    ) -> Wrapper:
        ...

else:

    def route(methods: list[Method], path: str, **params: Any):
        return fastapi.api_route(path, methods=methods, **params)


def __wrap_route(method: Method, func: Callable[Concatenate[list[Method], P], R] = route) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func([method], *args, **kwargs)

    return wrapper


websocket = fastapi.websocket

ws = websocket

get = __wrap_route("GET")

put = __wrap_route("PUT")

post = __wrap_route("POST")

delete = __wrap_route("DELETE")

options = __wrap_route("OPTIONS")

head = __wrap_route("HEAD")

patch = __wrap_route("PATCH")

trace = __wrap_route("TRACE")
