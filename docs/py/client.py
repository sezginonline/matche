from dataclasses import dataclass, field
from uuid import UUID, uuid4

from aioredis import Redis
from sanic.server.websockets.impl import WebsocketImplProtocol


@dataclass
class Client:
    ws: WebsocketImplProtocol
    redis: Redis
    uid: UUID = field(default_factory=uuid4)

    def __hash__(self) -> int:
        return self.uid.int

    async def send(self, message: str):
        await self.ws.send(message)

    async def shutdown(self):
        await self.ws.close()
