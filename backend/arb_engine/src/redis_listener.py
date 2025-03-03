import redis
import json
import asyncio
from backend.shared.config import shared_config
from backend.arb_engine.src.arb_engine import ArbEngine
from backend.scraper.src.odds_publisher import OddsUpdateMessage
from pydantic import ValidationError

class RedisListener:
    """Listens to redis for new odds and triggers the ArbDetector on them."""

    def __init__(self, arb_engine: ArbEngine):
        self.redis_client = redis.Redis(
            host=shared_config.REDIS_HOST,
            port=shared_config.REDIS_PORT,
            db=0,
            decode_responses=True
        )
        self.arb_engine = arb_engine

    async def listen(self):
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(shared_config.REDIS_ODDS_UPDATE_CHANNEL)

        print(f"Subscribed to Redis channel: {shared_config.REDIS_ODDS_UPDATE_CHANNEL}")

        while True:
            try:
                message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    try:
                        data = json.loads(message["data"])
                        odds_update_message = OddsUpdateMessage(**data)
                    
                        print(f"Received valid OddsUpdateMessage: {odds_update_message.model_dump_json()}")

                        await self.arb_engine.detect_arb_and_publish_bets(odds_update_message)

                    except json.JSONDecodeError:
                        print(f"Failed to decode JSON: {message['data']}")
                    except ValidationError as e:
                        print(f"Invalid OddsUpdateMessage: {e}")

                await asyncio.sleep(0.001)  # Prevent high CPU usage
            except Exception as e:
                print(f"⚠️ Redis Listener Error: {e}")