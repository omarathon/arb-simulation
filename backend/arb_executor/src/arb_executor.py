import asyncio
import redis
import json
from typing import Optional
from backend.arb_executor.src.config import arb_executor_config
from backend.shared.arb_math import calculate_guaranteed_payout
from backend.shared.config import shared_config

from backend.shared.redis import ArbMessage
from backend.shared.redis import get_odds_match_hash, get_odds_match_bookmaker_key


class ArbExecutor:
    """Executes detected arbs and publishes the result to Redis."""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=shared_config.REDIS_HOST,
            port=shared_config.REDIS_PORT,
            db=0,
            decode_responses=True
        )

    async def execute_arb(self, arb_message: ArbMessage):
        """Executes the arbitrage bet after a delay asynchronously."""
        print(f"⏳ Waiting {arb_executor_config.DELAY_SECONDS_TO_EXECUTE_ARB} seconds before executing arb: {arb_message.id}")
        await asyncio.sleep(arb_executor_config.DELAY_SECONDS_TO_EXECUTE_ARB)

        # Fetch latest odds from Redis
        latest_home_odds = self.get_latest_odds(arb_message.match, arb_message.home_win_bookmaker, is_home_win=True)
        latest_away_odds = self.get_latest_odds(arb_message.match, arb_message.away_win_bookmaker, is_home_win=False)

        if latest_home_odds is None or latest_away_odds is None:
            print(f"❌ Arb cancelled: Odds no longer available for arb: {arb_message.id}")
            arb_message.status = "cancelled"
            self.publish_arb_execution(arb_message)
            return

        # Update odds in message
        odds_changed = latest_home_odds != arb_message.home_win_odds or latest_away_odds != arb_message.away_win_odds
        arb_message.home_win_odds = latest_home_odds
        arb_message.away_win_odds = latest_away_odds

        # Calculate new expected payout using the correct EV formula
        latest_guaranteed_payout = calculate_guaranteed_payout(
            arb_message.home_win_stake,
            arb_message.away_win_stake,
            latest_home_odds,
            latest_away_odds
        )

        arb_message.guaranteed_payout = latest_guaranteed_payout
        arb_message.status = "adjusted" if odds_changed else "completed"

        if odds_changed:
            print(f"⚠️ Arb executed with adjusted odds: {arb_message.id}")
        else:
            print(f"✅ Arb executed: {arb_message.id}")
        self.publish_arb_execution(arb_message)

    def get_latest_odds(self, match: str, bookmaker: str, is_home_win: bool) -> Optional[float]:
        """Fetch the latest odds for a given (match, bookmaker) from Redis."""
        match_hash = get_odds_match_hash(match)
        bookmaker_key = get_odds_match_bookmaker_key(bookmaker)

        odds_json = self.redis_client.hget(match_hash, bookmaker_key)
        if odds_json is None:
            return None  # Odds were removed (likely cancelled)

        try:
            odds = json.loads(odds_json)
            return odds.get("home_win" if is_home_win else "away_win")
        except json.JSONDecodeError:
            print(f"⚠️ Failed to decode odds for {match}, {bookmaker}: {odds_json}")
            return None

    def publish_arb_execution(self, arb_message: ArbMessage):
        """Publishes the updated arbitrage execution result to Redis."""
        arb_data = json.dumps(arb_message.model_dump())
        self.redis_client.publish(shared_config.REDIS_ARB_EXECUTIONS_CHANNEL, arb_data)
        print(f"📢 Published ArbMessage to Redis: {arb_data}")
