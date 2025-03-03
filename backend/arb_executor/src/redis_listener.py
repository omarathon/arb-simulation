import redis
import json
import asyncio
from backend.shared.config import shared_config
from backend.arb_executor.src.arb_executor import ArbExecutor
from backend.shared.redis import ArbMessage
from pydantic import ValidationError


class RedisListener:
    """Listens to Redis for new arb detections and executes them asynchronously."""

    def __init__(self, arb_executor: ArbExecutor):
        self.redis_client = redis.Redis(
            host=shared_config.REDIS_HOST,
            port=shared_config.REDIS_PORT,
            db=0,
            decode_responses=True
        )
        self.arb_executor = arb_executor

    async def listen(self):
        """Continuously listens for arbitrage opportunities and executes them."""
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(shared_config.REDIS_ARB_DETECTIONS_CHANNEL)

        print(f"🎧 Subscribed to Redis channel: {shared_config.REDIS_ARB_DETECTIONS_CHANNEL}")

        while True:
            try:
                message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    try:
                        data = json.loads(message["data"])
                        arb_message = ArbMessage(**data)

                        # print(f"✅ Received valid ArbMessage: {arb_message.model_dump_json()}")

                        # Execute arbitrage asynchronously to prevent blocking
                        asyncio.create_task(self.arb_executor.execute_arb(arb_message))

                    except json.JSONDecodeError:
                        print(f"⚠️ Failed to decode JSON: {message['data']}")
                    except ValidationError as e:
                        print(f"⚠️ Invalid ArbMessage format: {e}")

                await asyncio.sleep(0.001)  # Prevent high CPU usage

            except redis.ConnectionError as e:
                print(f"🔴 Redis Connection Error: {e}. Retrying in 5s...")
                await asyncio.sleep(5)  # Wait before retrying connection
            except Exception as e:
                print(f"⚠️ Unexpected Redis Listener Error: {e}")
