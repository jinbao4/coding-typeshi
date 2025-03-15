from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, TypedDict, Union
from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .embed import EmbedPayload
    from .file import FilePayload

class UserAddContent(TypedDict):
    id: str
    by: str

class UserRemoveContent(TypedDict):
    id: str
    by: str

class UserJoinedContent(TypedDict):
    id: str
    by: str

class UserLeftContent(TypedDict):
    id: str

class UserKickedContent(TypedDict):
    id: str

class UserBannedContent(TypedDict):
    id: str

class ChannelRenameContent(TypedDict):
    name: str
    by: str

class ChannelDescriptionChangeContent(TypedDict):
    by: str

class ChannelIconChangeContent(TypedDict):
    by: str

class Masquerade(TypedDict, total=False):
    name: str
    avatar: str
    colour: str

class MessageInteractionsPayload(TypedDict):
    reactions: NotRequired[List[str]]
    restrict_reactions: NotRequired[bool]

SystemMessageContent = Union[
    UserAddContent,
    UserRemoveContent,
    UserJoinedContent,
    UserLeftContent,
    UserKickedContent,
    UserBannedContent,
    ChannelRenameContent,
    ChannelDescriptionChangeContent,
    ChannelIconChangeContent
]

class Message(TypedDict):
    _id: str
    channel: str
    author: str
    content: NotRequired[str]
    system: NotRequired[SystemMessageContent]
    attachments: NotRequired[List[FilePayload]]
    embeds: NotRequired[List[EmbedPayload]]
    mentions: NotRequired[List[str]]
    replies: NotRequired[List[str]]
    edited: NotRequired[Union[str, int]]
    masquerade: NotRequired[Masquerade]
    interactions: NotRequired[MessageInteractionsPayload]
    reactions: NotRequired[Dict[str, List[str]]]

class MessageReplyPayload(TypedDict):
    id: str
    mention: bool
