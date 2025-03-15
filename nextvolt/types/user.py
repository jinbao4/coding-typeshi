from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal, TypedDict
from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .file import File

__all__ = (
    "UserPayload",
    "UserRelationPayload",
    "UserBotPayload",
    "StatusPayload",
    "UserProfilePayload",
    "RelationPayload",
)

#User relationships
RelationPayload = Literal["Blocked", "BlockedOther", "Friend", "Incoming", "None", "Outgoing", "User"]

class UserBotPayload(TypedDict):
    """Represents a bot's owner info."""
    owner: str

class StatusPayload(TypedDict, total=False):
    """Represents a user's status."""
    text: NotRequired[str]
    presence: NotRequired[Literal["Busy", "Idle", "Online", "Invisible"]]

class UserRelationPayload(TypedDict):
    """Represents a user's relation to another user."""
    status: RelationPayload
    _id: str

class User(TypedDict):
    """Represents a full user object from the Revolt API."""
    _id: str
    username: str
    discriminator: str
    avatar: NotRequired[FilePayload]
    bot: NotRequired[UserBotPayload]
    relations: NotRequired[List[UserRelationPayload]]
    badges: NotRequired[int]
    status: NotRequired[StatusPayload]
    online: NotRequired[bool]
    relationship: NotRequired[RelationPayload]
    flags: NotRequired[int]
    privileged: NotRequired[bool]
    display_name: NotRequired[str]

class UserProfilePayload(TypedDict, total=False):
    """Represents a user's profile details."""
    content: NotRequired[str]
    background: NotRequired[FilePayload]
