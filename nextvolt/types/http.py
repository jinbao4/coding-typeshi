from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict
from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .member import MemberPayload
    from .message import MessagePayload
    from .user import UserPayload
    from .role import RolePayload

__all__ = (
    "ApiFeaturePayload",
    "VosoFeaturePayload",
    "FeaturesPayload",
    "ApiInfoPayload",
    "AutumnPayload",
    "GetServerMembersPayload",
    "MessageWithUserDataPayload",
    "CreateRolePayload",
    "HTTPError",  # Added here
)


class ApiFeaturePayload(TypedDict):
    enabled: bool
    url: str


class VosoFeaturePayload(ApiFeaturePayload):
    ws: str


class FeaturesPayload(TypedDict):
    email: bool
    invite_only: bool
    captcha: ApiFeaturePayload
    autumn: ApiFeaturePayload
    january: ApiFeaturePayload
    voso: VosoFeaturePayload


class ApiInfoPayload(TypedDict):
    revolt: str
    features: FeaturesPayload
    ws: str
    app: str
    vapid: str


class AutumnPayload(TypedDict):
    id: str


class GetServerMembersPayload(TypedDict):
    members: list[MemberPayload]
    users: list[UserPayload]


class MessageWithUserDataPayload(TypedDict):
    messages: list[MessagePayload]
    users: list[UserPayload]
    members: NotRequired[list[MemberPayload]]  # Marked as NotRequired for optional field


class CreateRolePayload(TypedDict):
    id: str
    role: RolePayload


class HTTPErrorMeta(TypedDict): 
    details: str


class HTTPError(TypedDict): 
    code: str
    message: str
    meta: NotRequired[HTTPErrorMeta]