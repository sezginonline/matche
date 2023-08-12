from __future__ import annotations
import asyncio
import json
from sanic.server.websockets.impl import WebsocketImplProtocol
from aioredis import Redis
from aioredis.client import PubSub
from aioredis.exceptions import PubSubError, ConnectionError
from sanic import Sanic
from sanic.log import logger


class Broadcast:

    def __init__(self, redis: Redis, pubsub: PubSub) -> None:
        self.redis = redis
        self.pubsub = pubsub
        self.clients = {}

    @classmethod
    async def connect(cls):
        app = Sanic.get_app()
        app.ctx.pubsub = app.ctx.redis.pubsub()
        await app.ctx.pubsub.subscribe("main")
        app.ctx.broadcast = cls(app.ctx.redis, app.ctx.pubsub)
        app.add_task(app.ctx.broadcast.receiver())

    async def reconnect(self):
        try:
            await self.connect()
        except ConnectionError:
            logger.error("Error connecting to Redis, retrying in 5 seconds...")
            await asyncio.sleep(5)
            await self.reconnect()

    async def receiver(self) -> None:
        try:
            async for raw in self.pubsub.listen():
                if raw and raw["type"] == "message":
                    message = raw["data"]
                    msg = json.loads(message)
                    if "to" in msg:
                        msg_to = str(msg["to"])
                        if isinstance(msg_to, list):
                            for to in msg_to[:100]:  # Limit 100
                                if to in self.clients:
                                    try:
                                        await self.clients[to].send(message)
                                    except Exception as e:
                                        self.clients.pop(to)
                        elif msg_to in self.clients:
                            try:
                                await self.clients[msg_to].send(message)
                            except Exception as e:
                                self.clients.pop(msg_to)
        except (ConnectionError, PubSubError) as e:
            await self.reconnect()

    async def register(self, ws: WebsocketImplProtocol, uid) -> bool:
        uid = str(uid)
        if not uid in self.clients:
            self.clients[uid] = ws
            await self.redis.incr("online")
            return True
        return False

    async def unregister(self, uid) -> None:
        uid = str(uid)
        if uid in self.clients:
            await self.clients[uid].close()
            self.clients.pop(uid)
            await self.redis.decr("online")

    async def publish(self, message: str) -> None:
        await self.redis.publish("main", message)
