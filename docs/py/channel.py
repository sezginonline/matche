from __future__ import annotations
import asyncio
from typing import Set
from sanic.server.websockets.impl import WebsocketImplProtocol
from aioredis import Redis
from aioredis.client import PubSub
from aioredis.exceptions import PubSubError, ConnectionError
from app.models.client import Client
from sanic import Sanic
from sanic.log import logger

class Channel:
    """
    Manages WebSocket connections and messages
    """

    def __init__(self, redis: Redis, pubsub: PubSub) -> None:
        """
        Initializes a Channel object

        Args:
        - redis: an aioredis.Redis object representing a Redis connection
        - pubsub: an aioredis.client.PubSub object representing a PubSub connection
        """
        self.redis = redis
        self.pubsub = pubsub
        self.clients: Set[Client] = set()

    @classmethod
    async def connect(cls):
        app = Sanic.get_app()
        app.ctx.pubsub = app.ctx.redis.pubsub()
        await app.ctx.pubsub.subscribe("main")
        app.ctx.channel = cls(app.ctx.redis, app.ctx.pubsub)
        app.add_task(app.ctx.channel.receiver())

    async def reconnect(self):
        try:
            await self.connect()
        except ConnectionError:
            logger.error("Error connecting to Redis, retrying in 5 seconds...")
            await asyncio.sleep(5)
            await self.reconnect()

    async def receiver(self) -> None:
        """
        Listens for new messages from the Redis PubSub connection and sends them to all connected clients
        """
        try:
            async for raw in self.pubsub.listen():
                if raw and raw["type"] == "message":
                    message = raw["data"]
                    for client in self.clients:
                        try:
                            await client.send(message)
                        except Exception as e:
                            logger.debug(
                                f"Error sending message to client {client.uid}: {e}")
                            self.clients.remove(client)
        except (ConnectionError, PubSubError) as e:
            logger.error(f"Error receiving message: {e}")
            await self.reconnect()

    async def register(self, ws: WebsocketImplProtocol) -> Client:
        """
        Registers a new client to the channel and sends a notification to all connected clients

        Args:
        - ws: a sanic.server.websockets.impl.WebsocketImplProtocol object representing a WebSocket connection

        Returns:
        A Client object representing the newly-registered client
        """
        client = Client(ws=ws, redis=self.redis)
        self.clients.add(client)
        await self.publish(f"Client {client.uid} has joined")
        return client

    async def unregister(self, client: Client) -> None:
        """
        Unregisters a client from the channel and sends a notification to all connected clients

        Args:
        - client: a Client object representing the client to unregister
        """
        if client in self.clients:
            await client.shutdown()
            self.clients.remove(client)
            await self.publish(f"Client {client.uid} has left")

    async def publish(self, message: str) -> None:
        """
        Publishes a message to the Redis PubSub connection

        Args:
        - message: a str representing the message to publish
        """
        await self.redis.publish("main", message)
