from __future__ import annotations

import asyncio 
import logging
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Literal, Optional, TypeVar, Union, cast, overload
from typing_extensions import ParamSpec

from .http import HTTPClient
from .invite import Invite
from .server import Server
from .user import ClientUser, User
from .utils import MISSING


__all__ = ("Client",)

_log = logging.getLogger(__name__)


class Client:
    def __init__(
        self,
        *,
        max_messages: Optional[int] = MISSING,
        api_url: Optional[str] = "https://api.revolt.chat"
    ) -> None:
        self.max_messages: int = 1000 if max_messages is MISSING else max_messages
        try:
            self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._listeners: Dict[str, List[Tuple[asyncio.Future, Callable[..., bool]]]] = {}
        self.extra_events: Dict[str, List[CoroFunc]] = {}

        self._closed: bool = False
        self._ready: asyncio.Event = MISSING
        
        self.internal_server_id = internal_server_id
        self.ws: Optional[RevoltWebSocket] = None
        self.http: HTTPClient = HTTPClient(api_url=api_url, loop=self.loop)

    @property
    def user(self) -> Optional[User]:
        return self.http.user
    
    @property
    def user_id(self) -> Optional[str]:
        return self.http.my_id
    
    @property
    def servers(self) -> Dict[str, Server]:
        return list(self.http.servers.values())
    
    @property
    def users(self) -> Dict[str, User]:
        return list(self.http.users.values())
    
    @property
    def dm_channels(self) -> Dict[str, Channel]:
        return list(self.http.private_dms.values())
    
    @property
    def emojis(self) -> Dict[str, Emoji]:
        return list(self.http.emojis.values())

    @property
    def guilds(self) -> Dict[str, Guild]:
        return list(self.http.servers.values())
    
    @property
    def latency(self) -> float:
        return float('nan') if self.ws is None else self.ws.latency
    
    @property
    def closed(self) -> bool:
        return self._closed

    def is_ready(self) -> bool:
        return self._ready.is_set()
    
    async def fetch_user(self, user_id: str) -> User:
        payload = await self.http.fetch_user(user_id)
        return User(payload)
    
    async def fetch_dm_channels(self) -> List[Channel]:
        channel_payloads = await self.http.fetch_dm_channels()
        return cast(list[Union[DMChannel, GroupDMChannel]], [channel_factory(payload, self.state) for payload in channel_payloads])

    async def fetch_channel(self, channel_id: str) -> Union[DMChannel, GroupDMChannel, SavedMessageChannel, TextChannel, VoiceChannel]:
        payload = await self.http.fetch_channel(channel_id)

        return channel_factory(payload, self.state)

    async def fetch_invite(self, code: str) -> Invite:
        payload = await self.http.fetch_invite(code)
        return Invite(payload, code, self.state)

    def get_message(self, message_id: str) -> Message:
        for message in self.state.messages:
            if message.id == message_id:
                return message
        raise LookupError

    async def edit_self(self, **kwargs: Any) -> None:
        if kwargs.get("avatar", Missing) is None:
            del kwargs["avatar"]
            remove = ["Avatar"]
        else:
            remove = None

        await self.state.http.edit_self(remove, kwargs)

    async def edit_status(self, **kwargs: Any) -> None:
        if kwargs.get("text", Missing) is None:
            del kwargs["text"]
            remove = ["StatusText"]
        else:
            remove = None

        if presence := kwargs.get("presence"):
            kwargs["presence"] = presence.value

        await self.state.http.edit_self(remove, {"status": kwargs})

    async def edit_profile(self, **kwargs: Any) -> None:
        remove: list[str] = []

        if kwargs.get("content", Missing) is None:
            del kwargs["content"]
            remove.append("ProfileContent")

        if kwargs.get("background", Missing) is None:
            del kwargs["background"]
            remove.append("ProfileBackground")

        await self.state.http.edit_self(remove, {"profile": kwargs})

    async def fetch_emoji(self, emoji_id: str) -> Emoji:
        emoji = await self.state.http.fetch_emoji(emoji_id)
        return Emoji(emoji, self.state)

    async def upload_file(self, file: File, tag: Literal['attachments', 'avatars', 'backgrounds', 'icons', 'banners', 'emojis']) -> Ulid:
        asset = await self.http.upload_file(file, tag)
        ulid = Ulid()
        ulid.id = asset["id"]
        return ulid
    
    async def fetch_servers(self) -> List[Server]:
        server_payloads = await self.http.fetch_servers()
    
    async def on_ready(self) -> None:
        pass

    async def on_message(self, message: revolt.Message) -> None:
        pass

    async def on_raw_message_update(self, payload: revolt.types.MessageUpdateEventPayload) -> None:
        pass

    async def on_message_update(self, before: revolt.Message, after: revolt.Message) -> None:
        pass

    async def on_raw_message_delete(self, payload: revolt.types.MessageDeleteEventPayload) -> None:
        pass

    async def on_message_delete(self, message: revolt.Message) -> None:
        pass

    async def on_channel_create(self, channel: revolt.Channel) -> None:
        pass

    async def on_channel_update(self, before: revolt.Channel, after: revolt.Channel) -> None:
        pass

    async def on_channel_delete(self, channel: revolt.Channel) -> None:
        pass

    async def on_typing_start(self, channel: revolt.Channel, user: revolt.User) -> None:
        pass

    async def on_typing_stop(self, channel: revolt.Channel, user: revolt.User) -> None:
        pass

    async def on_server_update(self, before: revolt.Server, after: revolt.Server) -> None:
        pass

    async def on_server_delete(self, server: revolt.Server) -> None:
        pass

    async def on_server_join(self, server: revolt.Server) -> None:
        pass

    async def on_member_update(self, before: revolt.Member, after: revolt.Member) -> None:
        pass

    async def on_member_join(self, member: revolt.Member) -> None:
        pass

    async def on_member_leave(self, member: revolt.Member) -> None:
        pass

    async def on_role_create(self, role: revolt.Role) -> None:
        pass

    async def on_role_update(self, before: revolt.Role, after: revolt.Role) -> None:
        pass

    async def on_role_delete(self, role: revolt.Role) -> None:
        pass

    async def on_user_update(self, before: revolt.User, after: revolt.User) -> None:
        pass

    async def on_user_relationship_update(self, user: revolt.User, before: revolt.RelationshipType, after: revolt.RelationshipType) -> None:
        pass

    async def on_raw_reaction_add(self, payload: revolt.types.MessageReactEventPayload) -> None:
        pass

    async def on_reaction_add(self, message: revolt.Message, user: revolt.User, emoji_id: str) -> None:
        pass

    async def on_raw_reaction_remove(self, payload: revolt.types.MessageUnreactEventPayload) -> None:
        pass

    async def on_reaction_remove(self, message: revolt.Message, user: revolt.User, emoji_id: str) -> None:
        pass

    async def on_raw_reaction_clear(self, payload: revolt.types.MessageRemoveReactionEventPayload) -> None:
        pass

    async def on_reaction_clear(self, message: revolt.Message, user: revolt.User, emoji_id: str) -> None:
        pass

    async def raw_bulk_message_delete(self, payload: revolt.types.BulkMessageDeleteEventPayload) -> None:
        pass

    async def bulk_message_delete(self, messages: list[revolt.Message]) -> None:
        pass
    
    def wait_for(
        self,
        event: str,
        *,
        check: Optional[Callable[..., bool]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """Waits for a WebSocket event to be dispatched in Revolt."""
        
        future = self.loop.create_future()
        
        if check is None:
            def _check(*args):
                return True
            check = _check

        ev = event.lower()
        
        listeners = self._listeners.setdefault(ev, [])
        listeners.append((future, check))
        
        return asyncio.wait_for(future, timeout)

    async def _run_event(self, coro: Coroutine, event_name: str, *args: Any, **kwargs: Any) -> None:
        """Executes an event coroutine and handles errors."""
        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            try:
                await self.on_error(event_name, e, *args, **kwargs)
            except asyncio.CancelledError:
                pass
    
    def start(self, token: str = None, *, reconnect: bool = True) -> None:
        self.http.token = token or self.http.token
        if not self.http.token:
            raise ClientException("Token is missing.. Are you a bit lose in the head?")
        
        self.http.session = aiohttp.ClientSession()
        self.connect(self, reconnect=reconnect)

        
    async def _connect(self, token: str = None, * reconnect: bool = True) -> None:
        self.http.token = token or self.http.token
        if not self.http.token:
            raise ClientException("Token is missing.. Are you a bit lose in the head?")

        while not self._closed:
            ws_build = RevoltWebSocket.build(self, loop=self.loop)
            rws = await asyncio.wait_for(ws_build, timeout=60)
            if type(rws) != RevoltWebSocket:
                self.dispatch('error', rws)
                return
            
            self.ws = rws
            self.http.ws = self.ws
            self.dispatch('connect')

    def dispatch(self, event: Union[str, BaseEvent], *args: Any, **kwargs: Any) -> None:
        if isinstance(event, BaseEvent):
            event_name = event.__dispatch_event__
            args = (event,)
        else:
            event_name = event

        log.debug('Dispatching event %s', event_name)
        method = 'on_' + event_name

        listeners = self._listeners.get(event_name)
        if listeners:
            removed = []
            for i, (future, condition) in enumerate(listeners):
                if future.cancelled():
                    removed.append(i)
                    continue

                try:
                    result = condition(*args)
                except Exception as exc:
                    future.set_exception(exc)
                    removed.append(i)
                else:
                    if result:
                        if len(args) == 0:
                            future.set_result(None)
                        elif len(args) == 1:
                            future.set_result(args[0])
                        else:
                            future.set_result(args)
                        removed.append(i)

            if len(removed) == len(listeners):
                self._listeners.pop(event_name)
            else:
                for idx in reversed(removed):
                    del listeners[idx]

        try:
            coro = getattr(self, method)
        except AttributeError:
            pass
        else:
            self._schedule_event(coro, method, *args, **kwargs)

    async def close(self) -> None:
        if self._closed:
            return

        await self.http.close()
        self._closed = True

        try:
            await self.ws.close(code=1000)
        except Exception:
            pass

        self._ready.clear()

    def run(self, token: str, *, reconnect=True) -> None:
        async def runner():
            async with self:
                await self.start(
                    token,
                    reconnect=reconnect,
                )
        try:
            asyncio.run(runner())
        except KeyboardInterrupt:
            return