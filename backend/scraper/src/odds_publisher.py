import redis
import json
import asyncio
import random
from collections import defaultdict
from typing import Optional, Dict
from backend.scraper.src.config import scraper_config
from backend.shared.config import shared_config
from backend.shared.redis import OddsUpdateMessage, OddsValues
from backend.shared.redis import get_odds_match_hash, get_odds_match_bookmaker_key

class OddsPublisher:
    """Handles the probabilistic publishing of odds updates and closings."""

    def __init__(self):
        """Initialize the Redis client and state tracking."""
        self.redis_client = redis.Redis(
            host=shared_config.REDIS_HOST,
            port=shared_config.REDIS_PORT,
            db=0
        )

        self.odds_state: Dict[str, Dict[str, Optional[OddsValues]]] = defaultdict(lambda: {
            "current_odds": self.generate_realistic_odds()
        })

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
                        print(f"🔄 {bookmaker} keeps current odds for {match}")

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
        return {"home_win": home_win_odds, "away_win": away_win_odds}

    def calculate_away_odds(self, home_win_odds: float) -> float:
        """
        Calculate away odds based on home win odds, adjusting for vig.
        """
        home_prob = 1 / home_win_odds
        away_prob = 1 + scraper_config.VIG_PERCENTAGE - home_prob
        away_win_odds = round(1 / away_prob, 2)
        return away_win_odds

    def close_odds(self, match: str, bookmaker: str):
        """Close the odds market, publish an update, and remove from Redis hash."""
        state = self.odds_state[(bookmaker, match)]
        if state["current_odds"] is None:
            return  # Already closed, no need to send duplicate messages

        state["current_odds"] = None  # Setting odds to None means closed

        odds_data: OddsUpdateMessage = {
            "event": "odds_close",
            "match": match,
            "bookmaker": bookmaker,
            "odds": None  # None signifies that the odds are closed
        }

        # Publish odds update
        self.redis_client.publish(shared_config.REDIS_ODDS_UPDATE_CHANNEL, json.dumps(odds_data))

        # Remove odds from Redis hash
        self.redis_client.hdel(get_odds_match_hash(match), get_odds_match_bookmaker_key(bookmaker))

        print(f"❌ {bookmaker} closed odds for {match}")

    def update_odds(self, match: str, bookmaker: str):
        """Update and publish new odds, and store in Redis hash."""
        state = self.odds_state[(bookmaker, match)]
        new_odds = self.generate_realistic_odds()
        state["current_odds"] = new_odds  # If it was closed, it's now open again

        odds_data: OddsUpdateMessage = {
            "event": "odds_update",
            "match": match,
            "bookmaker": bookmaker,
            "odds": new_odds
        }

        # Publish odds update
        self.redis_client.publish(shared_config.REDIS_ODDS_UPDATE_CHANNEL, json.dumps(odds_data))

        # Store latest odds in Redis hash
        self.redis_client.hset(get_odds_match_hash(match),  get_odds_match_bookmaker_key(bookmaker), json.dumps(new_odds))

        print(f"✅ {bookmaker} updated odds for {match}: {new_odds}")