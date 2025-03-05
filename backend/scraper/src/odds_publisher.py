import redis
import asyncio
import random
import logging
from typing import Optional, Dict
from backend.scraper.src.config import scraper_config
from backend.shared.config import shared_config
from backend.shared.redis import OddsUpdateMessage, OddsValues, get_odds_match_hash, get_odds_match_bookmaker_key
from backend.shared.utils import current_milli_time

logging.basicConfig(level=logging.INFO)  # Configure logging

class OddsPublisher:
    """Handles the probabilistic publishing of odds updates and closings."""

    def __init__(self, redis_client: redis.Redis, seed: Optional[int] = None):
        self.redis_client: redis.Redis = redis_client
        self.odds_state: Dict[str, Optional[OddsValues]] = {}

        # Allow determinism
        if seed is not None:
            random.seed(seed)
            logging.info(f"🔢 Random seed set to {seed}")

    async def publish_odds(self):
        """Continuously publish odds updates with probabilistic changes."""
        while True:
            for match in scraper_config.MATCHES:
                for bookmaker in scraper_config.BOOKMAKERS:
                    await asyncio.sleep(scraper_config.ODDS_PUBLISH_INTERVAL)

                    action = self.determine_action()
                    if action == "close":
                        self.close_odds(match, bookmaker)
                    elif action == "update":
                        self.update_odds(match, bookmaker)
                    else:
                        logging.info(f"🔄 {bookmaker} keeps current odds for {match}")

    def determine_action(self) -> str:
        """Decide whether to update, keep, or close odds based on probabilities."""
        p = random.random()
        if p < scraper_config.ODDS_UPDATE_PROBABILITY:
            return "update"
        elif p < scraper_config.ODDS_UPDATE_PROBABILITY + scraper_config.ODDS_CLOSE_PROBABILITY:
            return "close"
        return "keep"

    def generate_realistic_odds(self) -> OddsValues:
        """Generate realistic home and away odds using implied probability and vig."""
        home_win_odds = round(random.uniform(scraper_config.HOME_WIN_ODDS_MIN, scraper_config.HOME_WIN_ODDS_MAX), 2)
        away_win_odds = self.calculate_away_odds(home_win_odds)
        return OddsValues(home_win=home_win_odds, away_win=away_win_odds)

    def calculate_away_odds(self, home_win_odds: float) -> float:
        """Calculate away odds based on home win odds, adjusting for vig."""
        home_prob = 1 / home_win_odds
        away_prob = 1 + scraper_config.VIG_PROBABILITY - home_prob
        return round(1 / away_prob, 2)

    def close_odds(self, match: str, bookmaker: str):
        """Close the odds market, publish an update, and remove from Redis hash."""
        if (bookmaker, match) not in self.odds_state:
            return  # Already closed

        self.odds_state[(bookmaker, match)] = None  # Mark odds as closed

        odds_data = OddsUpdateMessage(event="odds_close", match=match, bookmaker=bookmaker, odds=None, timestamp=current_milli_time())
        self.redis_client.publish(shared_config.REDIS_ODDS_UPDATE_CHANNEL, odds_data.model_dump_json())

        self.redis_client.hdel(get_odds_match_hash(match), get_odds_match_bookmaker_key(bookmaker))

        logging.info(f"❌ {bookmaker} closed odds for {match}")

    def update_odds(self, match: str, bookmaker: str):
        """Update and publish new odds, and store in Redis hash."""
        new_odds = self.generate_realistic_odds()
        self.odds_state[(bookmaker, match)] = new_odds  # Store the updated odds

        odds_data = OddsUpdateMessage(event="odds_update", match=match, bookmaker=bookmaker, odds=new_odds, timestamp=current_milli_time())
        self.redis_client.publish(shared_config.REDIS_ODDS_UPDATE_CHANNEL, odds_data.model_dump_json())

        self.redis_client.hset(get_odds_match_hash(match), get_odds_match_bookmaker_key(bookmaker), new_odds.model_dump_json())

        logging.info(f"✅ {bookmaker} updated odds for {match}: {new_odds}")
