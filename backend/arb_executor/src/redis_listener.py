import logging
import redis
import json
import asyncio
from backend.shared.config import shared_config
from backend.arb_executor.src.arb_executor import ArbExecutor
from backend.shared.redis import ArbMessage
from pydantic import ValidationError


class RedisListener:
    """Listens to Redis for new arb detections and executes them asynchronously."""

    def __init__(self, redis_client: redis.Redis, arb_executor: ArbExecutor):
        self.redis_client: redis.Redis = redis_client
        self.arb_executor = arb_executor

    async def listen(self):
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(shared_config.REDIS_ARB_DETECTIONS_CHANNEL)

        logging.info(f"Subscribed to Redis channel: {shared_config.REDIS_ARB_DETECTIONS_CHANNEL}")

        while True:
            try:
                message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    try:
                        data = json.loads(message["data"])
                        arb_message = ArbMessage(**data)

                        asyncio.create_task(self.arb_executor.execute_arb(arb_message))

                    except json.JSONDecodeError:
                        logging.error(f"Failed to decode JSON: {message['data']}", exc_info=True)
                    except ValidationError:
                        logging.error(f"Invalid ArbMessage format. Raw data: {message['data']}", exc_info=True)

                await asyncio.sleep(0.001)  # Prevent high CPU usage

            except redis.ConnectionError:
                logging.error("Redis Connection Error. Retrying in 5s...", exc_info=True)
                await asyncio.sleep(5)  # Wait before retrying connection
            except Exception:
                logging.error("Unexpected Redis Listener Error.", exc_info=True)
