from __future__ import annotations
import asyncio
import aiohttp
import ulid
import json as _json
from typing import (TYPE_CHECKING, Any, Coroutine, Literal, Optional, TypeVar,
                    Union, overload)

from .errors import HTTPException, Forbidden, NotFound, RevoltServerError, ServerError

if TYPE_CHECKING:
    import aiohttp

    from .enums import SortType
    from .file import File
    from .types import Autumn as AutumnPayload
    from .types import Emoji as EmojiPayload
    from .types import Interactions as InteractionsPayload
    from .types import Masquerade as MasqueradePayload
    from .types import Member as MemberPayload
    from .types import Message as MessagePayload
    from .types import SendableEmbed as SendableEmbedPayload
    from .types import User as UserPayload
    from .types import (Server, ServerBans, TextChannel, UserProfile, VoiceChannel, Member, Invite, ApiInfo, Channel, SavedMessages,
                        DMChannel, EmojiParent, GetServerMembers, GroupDMChannel, MessageReplyPayload, MessageWithUserData, PartialInvite, CreateRole)


T = TypeVar("T")
Request = Coroutine[Any, Any, T]

class HTTPClient:
    __slots__ = ("session", "token", "api_url", "api_info", "auth_header")

    def __init__(self, session: aiohttp.ClientSession, token: str, api_url: str, api_info: dict[str, Any], bot: bool = True):
        self.session: aiohttp.ClientSession = session
        self.token: str = token
        self.api_url: str = api_url
        self.api_info: dict[str, Any] = api_info
        self.auth_header: str = "x-bot-token" if bot else "x-session-token"

    async def request(
        self, 
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"], 
        route: str, 
        *, 
        json: Optional[dict[str, Any]] = None, 
        nonce: bool = True, 
        params: Optional[dict[str, Any]] = None
    ) -> Any:
        """Send an HTTP request to the Revolt API."""
        
        url = f"{self.api_url}{route}"
        headers = {
            "User-Agent": "NextVolt (https://github.com/sparkles-devs/NextVolt)", 
            self.auth_header: self.token
        }
        
        kwargs = {"headers": headers}

        if json:
            headers["Content-Type"] = "application/json"
            if nonce and isinstance(json, dict) and "nonce" not in json:
                json["nonce"] = ulid.new().str
            kwargs["data"] = _json.dumps(json)

        if params:
            kwargs["params"] = params

        async with self.session.request(method, url, **kwargs) as resp:
            text = await resp.text()
            try:
                response_data = _json.loads(text) if text else None
            except ValueError:
                raise HTTPException(resp, f"Invalid JSON response:\n{text}")

            if 200 <= resp.status < 300:
                return response_data  # Successful response
            
            # Handle known HTTP errors
            if resp.status == 400:
                raise HTTPException(resp, response_data or "400: Bad Request")
            elif resp.status == 401:
                raise Forbidden(resp, response_data or "401: Unauthorized")
            elif resp.status == 403:
                raise Forbidden(resp, response_data or "403: Forbidden")
            elif resp.status == 404:
                raise NotFound(resp, response_data or "404: Not Found")
            elif resp.status == 429:
                retry_after = response_data.get("retry_after", 1) if isinstance(response_data, dict) else 1
                if isinstance(retry_after, (int, float)):
                    await asyncio.sleep(retry_after)
                    return await self.request(method, route, json=json, nonce=nonce, params=params)
            elif resp.status >= 500:
                raise RevoltServerError(resp, response_data or f"{resp.status}: Server Error")

            raise HTTPException(resp, f"Unexpected error: {resp.status} {text}")

    async def upload_file(self, file: File, tag: Literal["attachments", "avatars", "backgrounds", "icons", "banners", "emojis"]) -> AutumnPayload:
        """Uploads a file to Revolt's Autumn file server."""
        
        autumn_url = self.api_info.get("features", {}).get("autumn", {}).get("url")
        if not autumn_url:
            raise HTTPException(None, "Autumn file server URL is missing from API info.")

        url = f"{autumn_url}/{tag}"
        headers = {
            "User-Agent": "NextVolt (https://github.com/sparkles-devs/NextVolt)",
            self.auth_header: self.token
        }

        form = aiohttp.FormData()
        form.add_field("file", await file.read(), filename=file.filename)

        async with self.session.post(url, data=form, headers=headers) as resp:
            text = await resp.text()
            try:
                response_data = _json.loads(text)
            except ValueError:
                raise HTTPException(resp, f"Invalid JSON response from Autumn:\n{text}")

            if resp.status == 400:
                raise HTTPError(response_data)
            elif 500 <= resp.status < 600:
                raise ServerError(resp, response_data)

            return response_data

    
    async def send_message(
        self, 
        channel: str, 
        content: Optional[str] = None, 
        embeds: Optional[list[SendableEmbedPayload]] = None, 
        attachments: Optional[list[File]] = None, 
        replies: Optional[list[MessageReplyPayload]] = None, 
        masquerade: Optional[MasqueradePayload] = None, 
        interactions: Optional[InteractionsPayload] = None
    ) -> MessagePayload:
        """Send a message to a channel."""
        
        json: dict[str, Any] = {}

        if content:
            json["content"] = content

        if embeds:
            json["embeds"] = embeds

        if attachments:
            attachment_ids: list[str] = []

            for attachment in attachments:
                data = await self.upload_file(attachment, "attachments")
                attachment_ids.append(data["id"])

            json["attachments"] = attachment_ids

        if replies:
            json["replies"] = replies

        if masquerade:
            json["masquerade"] = masquerade

        if interactions:
            json["interactions"] = interactions

        return await self.request("POST", f"/channels/{channel}/messages", json=json)

    def edit_message(self, channel: str, message: str, content: Optional[str] = None, embeds: Optional[list[SendableEmbedPayload]] = None) -> Request[None]:
        """Edit a message in a channel."""
        
        json: dict[str, Any] = {}

        if content is not None:
            json["content"] = content

        if embeds is not None:
            json["embeds"] = embeds

        return self.request("PATCH", f"/channels/{channel}/messages/{message}", json=json)

    @overload
    def fetch_messages(
        self,
        channel: str,
        sort: SortType,
        *,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        nearby: Optional[str] = None,
        include_users: Literal[True] = True
    ) -> Request[MessageWithUserData]: ...

    @overload
    def fetch_messages(
        self,
        channel: str,
        sort: SortType,
        *,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        nearby: Optional[str] = None,
        include_users: Literal[False] = False
    ) -> Request[list[MessagePayload]]: ...

    def fetch_messages(
        self,
        channel: str,
        sort: SortType,
        *,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        nearby: Optional[str] = None,
        include_users: bool = False
    ) -> Request[Union[list[MessagePayload], MessageWithUserData]]:

        params: dict[str, Any] = {
            "sort": sort.value,
            "include_users": include_users,
            **{k: v for k, v in {
                "limit": limit,
                "before": before,
                "after": after,
                "nearby": nearby
            }.items() if v is not None}
        }

        return self.request("GET", f"/channels/{channel}/messages", params=params)

    @overload
    def search_messages(
        self,
        channel: str,
        query: str,
        *,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        sort: Optional[SortType] = None,
        include_users: Literal[False] = False
    ) -> Request[list[MessagePayload]]: ...

    @overload
    def search_messages(
        self,
        channel: str,
        query: str,
        *,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        sort: Optional[SortType] = None,
        include_users: Literal[True] = True
    ) -> Request[MessageWithUserData]: ...

    def search_messages(
        self,
        channel: str,
        query: str,
        *,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        sort: Optional[SortType] = None,
        include_users: bool = False
    ) -> Request[Union[list[MessagePayload], MessageWithUserData]]:

        json: dict[str, Any] = {
            "query": query,
            "include_users": include_users,
            **{k: v for k, v in {
                "limit": limit,
                "before": before,
                "after": after,
                "sort": sort.value if sort else None
            }.items() if v is not None}
        }

        return self.request("POST", f"/channels/{channel}/search", json=json)

    async def request_file(self, url: str) -> bytes:
        async with self.session.get(url) as resp:
            return await resp.read()
    
        def fetch_user(self, user_id: str) -> Request[UserPayload]:
        return self.request("GET", f"/users/{user_id}")

    def fetch_profile(self, user_id: str) -> Request[UserProfile]:
        return self.request("GET", f"/users/{user_id}/profile")

    def fetch_default_avatar(self, user_id: str) -> Request[bytes]:
        return self.request_file(f"{self.api_url}/users/{user_id}/default_avatar")

    def fetch_dm_channels(self) -> Request[list[Union[DMChannel, GroupDMChannel]]]:
        return self.request("GET", "/users/dms")

    def open_dm(self, user_id: str) -> Request[Union[DMChannel, SavedMessages]]:
        return self.request("GET", f"/users/{user_id}/dm")

    def fetch_channel(self, channel_id: str) -> Request[Channel]:
        return self.request("GET", f"/channels/{channel_id}")

    def close_channel(self, channel_id: str) -> Request[None]:
        return self.request("DELETE", f"/channels/{channel_id}")

    def fetch_server(self, server_id: str) -> Request[Server]:
        return self.request("GET", f"/servers/{server_id}")

    def delete_leave_server(self, server_id: str) -> Request[None]:
        return self.request("DELETE", f"/servers/{server_id}")

    @overload
    def create_channel(self, server_id: str, channel_type: Literal["Text"], name: str, description: Optional[str]) -> Request[TextChannel]: ...

    @overload
    def create_channel(self, server_id: str, channel_type: Literal["Voice"], name: str, description: Optional[str]) -> Request[VoiceChannel]: ...

    def create_channel(
        self, server_id: str, channel_type: Literal["Text", "Voice"], name: str, description: Optional[str]
    ) -> Request[Union[TextChannel, VoiceChannel]]:
        payload = {"type": channel_type, "name": name, **({"description": description} if description else {})}
        return self.request("POST", f"/servers/{server_id}/channels", json=payload)
    

    def fetch_server_invites(self, server_id: str) -> Request[list[PartialInvite]]:
        return self.request("GET", f"/servers/{server_id}/invites")

    def fetch_member(self, server_id: str, member_id: str) -> Request[Member]:
        return self.request("GET", f"/servers/{server_id}/members/{member_id}")

    def kick_member(self, server_id: str, member_id: str) -> Request[None]:
        return self.request("DELETE", f"/servers/{server_id}/members/{member_id}")

    def fetch_members(self, server_id: str) -> Request[GetServerMembers]:
        return self.request("GET", f"/servers/{server_id}/members")

    def ban_member(self, server_id: str, member_id: str, reason: Optional[str]) -> Request[None]:
        return self.request("PUT", f"/servers/{server_id}/bans/{member_id}", json={"reason": reason} if reason else None, nonce=False)

    def unban_member(self, server_id: str, member_id: str) -> Request[None]:
        return self.request("DELETE", f"/servers/{server_id}/bans/{member_id}")

    def fetch_bans(self, server_id: str) -> Request[ServerBans]:
        return self.request("GET", f"/servers/{server_id}/bans")

    def create_role(self, server_id: str, name: str) -> Request[CreateRole]:
        return self.request("POST", f"/servers/{server_id}/roles", json={"name": name}, nonce=False)

    def delete_role(self, server_id: str, role_id: str) -> Request[None]:
        return self.request("DELETE", f"/servers/{server_id}/roles/{role_id}")

    def fetch_invite(self, code: str) -> Request[Invite]:
        return self.request("GET", f"/invites/{code}")

    def delete_invite(self, code: str) -> Request[None]:
        return self.request("DELETE", f"/invites/{code}")

    def edit_channel(self, channel_id: str, remove: Optional[list[str]], values: dict[str, Any]) -> Request[None]:
        return self.request("PATCH", f"/channels/{channel_id}", json={**values, **({"remove": remove} if remove else {})})

    def edit_role(self, server_id: str, role_id: str, remove: Optional[list[str]], values: dict[str, Any]) -> Request[None]:
        return self.request("PATCH", f"/servers/{server_id}/roles/{role_id}", json={**values, **({"remove": remove} if remove else {})})

    async def edit_self(self, remove: Optional[list[str]], values: dict[str, Any]) -> Request[None]:
        if remove:
            values["remove"] = remove

        if "avatar" in values:
            asset = await self.upload_file(values["avatar"], "avatars")
            values["avatar"] = asset["id"]

        if "profile" in values:
            profile = values["profile"]
            if background := profile.get("background"):
                asset = await self.upload_file(background, "backgrounds")
                profile["background"] = asset["id"]

        return await self.request("PATCH", "/users/@me", json=values)

    def set_permissions(self, endpoint: str, entity_id: str, allow: int, deny: int) -> Request[None]:
        return self.request("PUT", f"/{endpoint}/{entity_id}/permissions", json={"permissions": {"allow": allow, "deny": deny}})

    def add_reaction(self, channel_id: str, message_id: str, emoji: str) -> Request[None]:
        return self.request("PUT", f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}")

    def remove_reaction(self, channel_id: str, message_id: str, emoji: str, user_id: Optional[str] = None, remove_all: bool = False) -> Request[None]:
        params = {k: v for k, v in {"user_id": user_id, "remove_all": remove_all}.items() if v is not None}
        return self.request("DELETE", f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}", params=params)

    def remove_all_reactions(self, channel_id: str, message_id: str) -> Request[None]:
        return self.request("DELETE", f"/channels/{channel_id}/messages/{message_id}/reactions")

    def delete_emoji(self, emoji_id: str) -> Request[None]:
        return self.request("DELETE", f"/custom/emoji/{emoji_id}")

    def fetch_emoji(self, emoji_id: str) -> Request[EmojiPayload]:
        return self.request("GET", f"/custom/emoji/{emoji_id}")

    async def create_emoji(self, name: str, file: File, nsfw: bool, parent: EmojiParent) -> Request[EmojiPayload]:
        asset = await self.upload_file(file, "emojis")
        return await self.request("PUT", f"/custom/emoji/{asset['id']}", json={"name": name, "parent": parent, "nsfw": nsfw})

    def edit_member(self, server_id: str, member_id: str, remove: Optional[list[str]], values: dict[str, Any]) -> Request[MemberPayload]:
        return self.request("PATCH", f"/servers/{server_id}/members/{member_id}", json={**values, **({"remove": remove} if remove else {})})

    def delete_messages(self, channel_id: str, messages: list[str]) -> Request[None]:
        return self.request("DELETE", f"/channels/{channel_id}/messages/bulk", json={"ids": messages})
    
    async def my_id(self) -> str:
        user_data = await self.request("GET", "/users/@me")
        return user_data["id"]
    

    def fetch_all_emojis(self) -> Request[list[EmojiPayload]]:
        """Fetch all custom emojis available to the bot."""
        return self.request("GET", "/custom/emoji")

    def fetch_all_private_dms(self) -> Request[list[Union[DMChannel, GroupDMChannel]]]:
        """Fetch all private DM channels."""
        return self.request("GET", "/users/dms")

    def emojis(self) -> list[EmojiPayload]:
        """Get all custom emojis."""
        return self.fetch_all_emojis()

    def private_dms(self) -> list[Union[DMChannel, GroupDMChannel]]:
        """Get all private DM channels."""
        return self.fetch_all_private_dms()

    async def ws_connect(self) -> aiohttp.ClientWebSocketResponse:
        self.session = self.session if self.session and not self.session.closed else aiohttp.ClientSession()
        params = {
            'version' : '1',
            'format' : 'json',
            'token' : self.token
        }
        return await self.session.ws_connect('wss://ws.revolt.chat', params=params)
    
    def add_to_server_cache(self, server: Server):
        self._servers[server.id] = server