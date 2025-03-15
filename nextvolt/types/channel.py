from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Literal, TypedDict, Union
from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .file import FilePayload
    from .message import MessagePayload


class OverrideFieldPayload(TypedDict):
    a: int
    d: int


class BaseChannelPayload(TypedDict):
    _id: str
    nonce: NotRequired[str]


class SavedMessagePayload(BaseChannelPayload):
    user: str
    channel_type: Literal["SavedMessages"]


class DMChannelPayload(BaseChannelPayload):
    active: bool
    recipients: List[str]
    channel_type: Literal["DirectMessage"]
    last_message: MessagePayload


class GroupDMChannelPayload(BaseChannelPayload):
    recipients: List[str]
    name: str
    owner: str
    channel_type: Literal["Group"]
    icon: NotRequired[FilePayload]
    permissions: NotRequired[int]
    description: NotRequired[str]


class TextChannelPayload(BaseChannelPayload):
    server: str
    name: str
    description: NotRequired[str]
    icon: NotRequired[FilePayload]
    default_permissions: NotRequired[OverrideFieldPayload]
    role_permissions: NotRequired[Dict[str, OverrideFieldPayload]]
    last_message: NotRequired[str]
    channel_type: Literal["TextChannel"]


class VoiceChannelPayload(BaseChannelPayload):
    server: str
    name: str
    description: NotRequired[str]
    icon: NotRequired[FilePayload]
    default_permissions: NotRequired[OverrideFieldPayload]
    role_permissions: NotRequired[Dict[str, OverrideFieldPayload]]
    channel_type: Literal["VoiceChannel"]


ChannelPayload = Union[
    SavedMessagePayload,
    DMChannelPayload,
    GroupDMChannelPayload,
    TextChannelPayload,
    VoiceChannelPayload,
]


class CategoryPayload(TypedDict):
    id: str
    title: str
    channels: List[str]


class BaseChannel(TypedDict):
    _id: str
    nonce: str


class SavedMessages(BaseChannel):
    user: str
    channel_type: Literal["SavedMessages"]


class DMChannel(BaseChannel):
    active: bool
    recipients: list[str]
    last_message_id: NotRequired[str]
    channel_type: Literal["DirectMessage"]


class GroupDMChannel(BaseChannel):
    recipients: list[str]
    name: str
    owner: str
    channel_type: Literal["Group"]
    icon: NotRequired[File]
    permissions: NotRequired[int]
    description: NotRequired[str]
    nsfw: NotRequired[bool]
    last_message_id: NotRequired[str]


class TextChannel(BaseChannel):
    server: str
    name: str
    description: str
    channel_type: Literal["TextChannel"]
    icon: NotRequired[File]
    default_permissions: NotRequired[Overwrite]
    role_permissions: NotRequired[dict[str, Overwrite]]
    nsfw: NotRequired[bool]
    last_message_id: NotRequired[str]


class VoiceChannel(BaseChannel):
    server: str
    name: str
    description: str
    channel_type: Literal["VoiceChannel"]
    icon: NotRequired[File]
    default_permissions: NotRequired[Overwrite]
    role_permissions: NotRequired[dict[str, Overwrite]]
    nsfw: NotRequired[bool]


ServerChannel = Union[TextChannel, VoiceChannel]
Channel = Union[SavedMessages, DMChannel, GroupDMChannel, TextChannel, VoiceChannel]
