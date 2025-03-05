import logging
import redis
import json
import asyncio
from backend.gateway.src.websocket_handler import broadcast_message
from backend.shared.config import shared_config
from backend.gateway.src.models import WebSocketMessage
from backend.shared.redis import OddsUpdateMessage, ArbMessage
from pydantic import ValidationError

class RedisListener:
    """Handles Redis pub/sub listening and broadcasts messages to WebSockets."""

    def __init__(self, redis_client: redis.Redis):
        self.redis_client: redis.Redis = redis_client

    async def listen(self):
        pubsub = self.redis_client.pubsub()
        
        # Subscribe to all relevant Redis channels
        pubsub.subscribe(
            shared_config.REDIS_ODDS_UPDATE_CHANNEL,
            shared_config.REDIS_ARB_DETECTIONS_CHANNEL,
            shared_config.REDIS_ARB_EXECUTIONS_CHANNEL
        )

        logging.info(f"Subscribed to Redis channels")

        while True:
            try:
                message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    channel = message["channel"]
                    raw_data = message["data"]

                    try:
                        data = json.loads(raw_data)

                        # Determine message type
                        if channel == shared_config.REDIS_ODDS_UPDATE_CHANNEL:
                            parsed_message = WebSocketMessage(
                                message_type="odds_update",
                                contents=OddsUpdateMessage(**data)
                            )
                        elif channel == shared_config.REDIS_ARB_DETECTIONS_CHANNEL:
                            parsed_message = WebSocketMessage(
                                message_type="arb_detection",
                                contents=ArbMessage(**data)
                            )
                        elif channel == shared_config.REDIS_ARB_EXECUTIONS_CHANNEL:
                            parsed_message = WebSocketMessage(
                                message_type="arb_execution",
                                contents=ArbMessage(**data)
                            )
                        else:
                            logging.warning(f"Unrecognized message from {channel}: {data}")
                            continue

                        logging.info(f"Sending WebSocket message: {parsed_message.model_dump_json()}")
                        await broadcast_message(parsed_message)

                    except json.JSONDecodeError:
                        logging.error(f"Failed to decode JSON: {raw_data}", exc_info=True)
                    except ValidationError:
                        logging.error(f"Validation error. Raw data: {raw_data}", exc_info=True)

                await asyncio.sleep(0.001)  # Prevent high CPU usage

            except Exception:
                logging.error("Redis Listener Error.", exc_info=True)
