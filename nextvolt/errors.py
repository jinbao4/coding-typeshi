from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientResponse
    from .types.http import HTTPError as HTTPErrorPayload

__all__ = (
    "RevoltException",
    "ClientException",
    "HTTPException",
    "BadRequest",
    "Forbidden",
    "NotFound",
    "ImATeapot",
    "TooManyRequests",
    "RevoltServerError",
    "InvalidData",
    "InvalidArgument",
)


class RevoltException(Exception):
    pass


class ClientException(RevoltException):
    pass


class HTTPException(RevoltException):
    def __init__(self, response: ClientResponse, data: HTTPErrorPayload):
        self.response = response
        self.status = response.status
        self.message: str = ''
        self.code: str = 'UnknownCode'

        if isinstance(data, dict): 
            self.message = data.get('message', '')
            self.code = data.get('code', 'UnknownCode')

        super().__init__(f"{self.status} {self.code}: {self.message}")


class BadRequest(HTTPException):
    pass


class Forbidden(HTTPException):
    def __init__(self, response: ClientResponse, data: HTTPErrorPayload):
        super().__init__(response, data)

        self.raw_missing_permissions = None
        if isinstance(data, dict) and "meta" in data and "missingPermissions" in data["meta"]:
            self.raw_missing_permissions = data["meta"]["missingPermissions"]


class NotFound(HTTPException):
    pass


class ImATeapot(HTTPException):
    def __init__(self, response: ClientResponse, data: HTTPErrorPayload):
        super().__init__(response, data)

        self.raw_missing_permissions = None
        if isinstance(data, dict) and "meta" in data and "missingPermissions" in data["meta"]:
            self.raw_missing_permissions = data["meta"]["missingPermissions"]


class TooManyRequests(HTTPException):
    pass


class RevoltServerError(HTTPException):
    pass


class InvalidData(HTTPException):
    pass


class InvalidArgument(HTTPException):
    pass
