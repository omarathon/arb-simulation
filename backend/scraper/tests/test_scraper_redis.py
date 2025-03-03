import redis
import json
import time
from backend.shared.config import shared_config
from backend.scraper.src.config import scraper_config

redis_client = redis.Redis(host=shared_config.REDIS_HOST, port=shared_config.REDIS_PORT, db=0)

def test_scraper_publishes_odds_to_redis():
    """Test that the scraper correctly publishes odds to Redis."""

    pubsub = redis_client.pubsub()
    pubsub.subscribe("odds_update")

    timeout = scraper_config.ODDS_PUBLISH_INTERVAL + 2
    start_time = time.time()

    message = None
    while time.time() - start_time < timeout:
        message = pubsub.get_message(ignore_subscribe_messages=True)
        if message:
            break

    assert message is not None, "No odds were published to Redis!"
    
    odds_data = json.loads(message["data"])
    assert "match" in odds_data, "Missing 'match' field in Redis odds!"
    assert "bookmaker" in odds_data, "Missing 'bookmaker' field in Redis odds!"
