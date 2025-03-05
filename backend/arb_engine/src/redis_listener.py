import logging
import redis
import json
import asyncio
from backend.shared.config import shared_config
from backend.arb_engine.src.arb_engine import ArbEngine
from backend.scraper.src.odds_publisher import OddsUpdateMessage
from pydantic import ValidationError

class RedisListener:
    """Listens to redis for new odds and triggers the ArbDetector on them."""

    def __init__(self, redis_client: redis.Redis, arb_engine: ArbEngine):
        self.redis_client: redis.Redis = redis_client
        self.arb_engine = arb_engine

    async def listen(self):
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(shared_config.REDIS_ODDS_UPDATE_CHANNEL)

        logging.info(f"Subscribed to Redis channel: {shared_config.REDIS_ODDS_UPDATE_CHANNEL}")

        while True:
            try:
                message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    try:
                        data = json.loads(message["data"])
                        odds_update_message = OddsUpdateMessage(**data)
                    
                        logging.info(f"Received valid OddsUpdateMessage: {odds_update_message.model_dump_json()}")

                        await self.arb_engine.detect_arb_and_publish_bets(odds_update_message)

                    except json.JSONDecodeError:
                        logging.error(f"Failed to decode JSON: {repr(message['data'])}", exc_info=True)
                    except ValidationError:
                        logging.error("Invalid OddsUpdateMessage", exc_info=True)

                await asyncio.sleep(0.001)  # Prevent high CPU usage

            except Exception as e:
                logging.error("Redis Listener Error", exc_info=True)