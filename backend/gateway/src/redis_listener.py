import redis
import json
import asyncio
from backend.gateway.src.websocket_handler import broadcast_message
from backend.shared.config import shared_config

class RedisListener:
    """Handles Redis pub/sub listening and broadcasts messages to WebSockets."""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=shared_config.REDIS_HOST,
            port=shared_config.REDIS_PORT,
            db=0,
            decode_responses=True
        )

    async def listen(self):
        """Listens for Redis messages asynchronously and broadcasts updates."""
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(shared_config.REDIS_ODDS_UPDATE_CHANNEL)

        print(f"Subscribed to Redis channel: {shared_config.REDIS_ODDS_UPDATE_CHANNEL}")

        while True:
            try:
                message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    data = json.loads(message["data"])
                    print(f"Received message from Redis: {data}")
                    await broadcast_message(data)

                await asyncio.sleep(0.001)  # Prevent high CPU usage
            except Exception as e:
                print(f"⚠️ Redis Listener Error: {e}")