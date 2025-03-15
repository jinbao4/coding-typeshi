from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict, Union

from typing_extensions import NotRequired

from .channel import Channel, DMChannel, GroupDMChannel, SavedMessages, TextChannel, VoiceChannel
from .message import Message
from .permissions import Overwrite

if TYPE_CHECKING:
    from .category import Category
    from .embed import Embed
    from .emoji import Emoji
    from .file import File
    from .member import Member, MemberID
    from .server import Server, SystemMessagesConfig
    from .user import Status, User, UserProfile, UserRelation

__all__ = (
    "BasePayload", "AuthenticatePayload", "ReadyEventPayload", "MessageEventPayload",
    "MessageUpdateData", "MessageUpdateEventPayload", "MessageDeleteEventPayload",
    "ChannelCreateEventPayload", "ChannelUpdateEventPayload", "ChannelDeleteEventPayload",
    "ChannelStartTypingEventPayload", "ServerUpdateEventPayload", "ServerDeleteEventPayload",
    "ServerMemberUpdateEventPayload", "ServerMemberJoinEventPayload", "ServerMemberLeaveEventPayload",
    "ServerRoleUpdateEventPayload", "ServerRoleDeleteEventPayload", "UserUpdateEventPayload",
    "UserRelationshipEventPayload", "ServerCreateEventPayload", "MessageReactEventPayload",
    "BulkMessageDeleteEventPayload"
)

class BasePayload(TypedDict):
    type: str

class AuthenticatePayload(BasePayload):
    token: str

class ReadyEventPayload(BasePayload):
    users: list[User]
    servers: list[Server]
    channels: list[Channel]
    members: list[Member]
    emojis: list[Emoji]

class MessageEventPayload(BasePayload, Message):
    pass

class MessageUpdateData(TypedDict):
    content: str
    embeds: list[Embed]
    edited: Union[str, int]

class MessageUpdateEventPayload(BasePayload):
    channel: str
    data: MessageUpdateData
    id: str

class MessageDeleteEventPayload(BasePayload):
    channel: str
    id: str

class ChannelCreateEventPayload(BasePayload):
    type: str
    id: str
    channel_data: Union[GroupDMChannel, TextChannel, VoiceChannel, DMChannel, SavedMessages]

class ChannelUpdateEventPayload(BasePayload):
    id: str
    data: dict
    clear: Literal["Icon", "Description"]

class ChannelDeleteEventPayload(BasePayload):
    id: str

class ChannelStartTypingEventPayload(BasePayload):
    id: str
    user: str

ChannelDeleteTypingEventPayload = ChannelStartTypingEventPayload

class ServerUpdateEventPayload(BasePayload):
    id: str
    data: dict
    clear: Literal["Icon", "Banner", "Description"]

class ServerDeleteEventPayload(BasePayload):
    id: str

class ServerCreateEventPayload(BasePayload):
    id: str
    server: Server
    channels: list[Channel]

class ServerMemberUpdateEventPayload(BasePayload):
    id: MemberID
    data: dict
    clear: Literal["Nickname", "Avatar"]

class ServerMemberJoinEventPayload(BasePayload):
    id: str
    user: str

ServerMemberLeaveEventPayload = ServerMemberJoinEventPayload

class ServerRoleUpdateEventPayload(BasePayload):
    id: str
    role_id: str
    data: dict
    clear: Literal["Colour"]

class ServerRoleDeleteEventPayload(BasePayload):
    id: str
    role_id: str

class UserUpdateEventPayload(BasePayload):
    id: str
    data: dict
    clear: Literal["ProfileContent", "ProfileBackground", "StatusText", "Avatar"]

class UserRelationshipEventPayload(BasePayload):
    id: str
    user: str
    status: Status

class MessageReactEventPayload(BasePayload):
    id: str
    channel_id: str
    user_id: str
    emoji_id: str

MessageUnreactEventPayload = MessageReactEventPayload

class MessageRemoveReactionEventPayload(BasePayload):
    id: str
    channel_id: str
    emoji_id: str

class BulkMessageDeleteEventPayload(BasePayload):
    channel: str
    ids: list[str]
