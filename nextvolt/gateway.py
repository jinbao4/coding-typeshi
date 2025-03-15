import aiohttp
import asyncio
import json
import logging

from .errors import RevoltException, HTTPException

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .types import gateway as gw
    from .client import Client

_log = logging.getLogger(__name__)

class RevoltWebSocket:
    MISSABLE = 0
    WELCOME = 1
    RESUMED = 2
    INVALID_CURSOR = 8
    INTERNAL_ERROR = 9

    def __init__(
        self,
        socket: aiohttp.ClientWebSocketResponse,
        client: Client,
        *,
        loop: asyncio.AbstractEventLoop
    ):
        self.client = client
        self.loop = loop
        self._heartbeater = None

        # socket
        self.socket: aiohttp.ClientWebSocketResponse = socket
        self._close_code: Optional[int] = None
        
        # ws
        self._last_message_id: Optional[str] = None
    
    @property
    def latency(self):
        return float('inf') if self._heartbeater is None else self._heartbeater.latency
    
    async def poll_event(self) -> Optional[int]:
        msg = await self.socket.receive()
        if msg.type is aiohttp.WSMsgType.TEXT:
            try:
                data = json.loads(msg.data)
                op = await self.received_event(data)
            except G as e:
                _log.error(f"Error receiving WebSocket message: {e}")
                self.client.dispatch('error', e)
            else:
                return op
        elif msg.type is aiohttp.WSMsgType.PONG:
            if self._heartbeater:
                self._heartbeater.record_pong()
        
        elif msg.type is aiohttp.WSMsgType.ERROR:   
            raise Exception(f"WebSocket error: {msg.data}")
        
        elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING):
            return "WebSocket is in a closed or closing state."
    
    async def send(self, payload: dict) -> None:
        payload = json.dumps(payload)
        self.client.dispatch('socket_raw_send', payload)
        await self.socket.send_str(payload)

    async def ping(self) -> None:
        _log.debug('Sending heartbeat')
        await self.socket.ping()

    async def close(self, code: int = 1000) -> None:
        log.debug('Closing websocket connection with code %s', code)
        if self._heartbeater:
            self._heartbeater.stop()
            self._heartbeater = None

        self._close_code = code
        await self.socket.close(code=code)
    
    @classmethod
    async def build(cls, client, *, loop: asyncio.AbstractEventLoop = None) -> "WebSocketClient":
        try:
            socket = await client.http.ws_connect()  
        except aiohttp.client_exceptions.WSServerHandshakeError as exc:
            _log.error('Failed to connect to the gateway: %s', exc)
            return exc
        else:
            _log.info('Connected to the gateway')
        ws = cls(socket, client, loop=loop or asyncio.get_event_loop())
        ws._parsers = ws._parsers = WebSocketEventParsers(client)
        await ws.ping()

        return ws