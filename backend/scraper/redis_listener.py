import redis
import json
import asyncio
from backend.websocket_handler import broadcast_message

redis_client = redis.Redis(host='redis', port=6379, db=0)

async def redis_listener():
    """Listens for Redis messages and broadcasts them to WebSocket clients."""
    pubsub = redis_client.pubsub()
    pubsub.subscribe("odds_update")

    for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            await broadcast_message(data)

def start_redis_listener():
    """Starts the Redis listener in a background thread."""
    import threading
    threading.Thread(target=asyncio.run, args=(redis_listener(),)).start()
