from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict
from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .category import Category
    from .file import File
    from .role import Role

__all__ = (
    "Server",
    "BannedUser",
    "Ban",
    "ServerBans",
    "SystemMessagesConfig"
)

class SystemMessagesConfig(TypedDict, total=False):
    user_joined: str
    user_left: str
    user_kicked: str
    user_banned: str


class Server(TypedDict):
    _id: str
    owner: str
    name: str
    channels: list[str]
    default_permissions: int
    nonce: NotRequired[str]
    description: NotRequired[str]
    categories: NotRequired[list[Category]]
    system_messages: NotRequired[SystemMessagesConfig]
    roles: NotRequired[dict[str, Role]]
    icon: NotRequired[File]
    banner: NotRequired[File]
    nsfw: NotRequired[bool]


class BannedUser(TypedDict):
    _id: str
    username: str
    avatar: NotRequired[File]


class BanId(TypedDict):
    server: str
    user: str


class Ban(TypedDict):
    _id: BanId
    reason: NotRequired[str]


class ServerBans(TypedDict):
    users: list[BannedUser]
    bans: list[Ban]


from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Literal, TypedDict
from typing_extensions import NotRequired
from voltage.types.channel import CategoryPayload

if TYPE_CHECKING:
    from .channel import OverrideFieldPayload
    from .file import FilePayload


class _MemberBase(TypedDict):
    nickname: NotRequired[str]
    avatar: NotRequired[FilePayload]
    roles: NotRequired[List[str]]


class MemberIDPayload(_MemberBase):
    server: str
    user: str


class MemberPayload(_MemberBase):
    _id: MemberIDPayload


class PartialRolePayload(TypedDict):
    name: str
    permissions: OverrideFieldPayload


class RolePayload(TypedDict):
    name: str
    permissions: OverrideFieldPayload
    colour: NotRequired[str]
    hoist: NotRequired[bool]
    rank: int


class InvitePayload(TypedDict):
    type: Literal["Server"]
    server_id: str
    server_name: str
    server_icon: NotRequired[str]
    server_banner: NotRequired[str]
    channel_id: str
    channel_name: str
    channel_description: NotRequired[str]
    user_name: str
    user_avatar: NotRequired[str]
    member_count: int


class PartialInvitePayload(TypedDict):
    _id: str
    server: str
    channel: str
    creator: str


class SystemMessagesConfigPayload(TypedDict):
    user_joined: NotRequired[str]
    user_left: NotRequired[str]
    user_kicked: NotRequired[str]
    user_banned: NotRequired[str]


class ServerPayload(TypedDict):
    _id: str
    name: str
    owner: str
    channels: List[str]
    default_permissions: OverrideFieldPayload
    nonce: NotRequired[str]
    description: NotRequired[str]
    categories: NotRequired[List[CategoryPayload]]
    system_messages: NotRequired[SystemMessagesConfigPayload]
    roles: NotRequired[Dict[str, RolePayload]]
    icon: NotRequired[FilePayload]
    banner: NotRequired[FilePayload]
    nsfw: NotRequired[bool]
    flags: NotRequired[int]
    analytics: NotRequired[bool]
    discoverable: NotRequired[bool]


class BannedUserPayload(TypedDict):
    _id: str
    username: str
    avatar: NotRequired[FilePayload]


class BanIdPayload(TypedDict):
    server: str
    user: str


class BanPayload(TypedDict):
    _id: BanIdPayload
    reason: NotRequired[str]


class ServerBansPayload(TypedDict):
    users: List[BannedUserPayload]
    bans: List[BanPayload]
