import asyncio
from pydantic import ValidationError
import redis
import json
from typing import Optional
from backend.arb_executor.src.config import arb_executor_config
from backend.shared.arb_math import calculate_guaranteed_profit
from backend.shared.config import shared_config

from backend.shared.redis import ArbMessage, OddsValues
from backend.shared.redis import get_odds_match_hash, get_odds_match_bookmaker_key


class ArbExecutor:
    """Executes detected arbs after a simulated delay and publishes the result to Redis."""

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

        # Fetch latest odds
        try:
            latest_home_odds, latest_away_odds, odds_changed = self.fetch_latest_odds(arb_message)
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"🚨 Skipping execution for Arb ID {arb_message.id} due to odds deserialization error: {e}")
            return

        # Update the arb message with new odds
        arb_message.home_win_odds = latest_home_odds
        arb_message.away_win_odds = latest_away_odds

        # Update stakes if there was a cancellation (in which case no money was betted)
        cancelled_home, cancelled_away = self.update_stakes(arb_message)

        # Calculate new profit
        self.calculate_and_update_profit(arb_message)

        # Determine new status
        arb_message.status = self.determine_status(cancelled_home, cancelled_away, odds_changed)

        # Publish and log result
        self.publish_arb_execution(arb_message)
        self.log_execution_status(arb_message.status, arb_message.id)

    def fetch_latest_odds(self, arb_message: ArbMessage):
        """Fetches the latest odds for home and away and determines if they changed."""
        latest_home_odds = self.get_latest_odds(arb_message.match, arb_message.home_win_bookmaker, is_home_win=True)
        latest_away_odds = self.get_latest_odds(arb_message.match, arb_message.away_win_bookmaker, is_home_win=False)

        odds_changed = latest_home_odds != arb_message.home_win_odds or latest_away_odds != arb_message.away_win_odds
        return latest_home_odds, latest_away_odds, odds_changed

    def update_stakes(self, arb_message: ArbMessage):
        """Updates stake values if an outcome is cancelled."""
        cancelled_home = arb_message.home_win_odds is None
        cancelled_away = arb_message.away_win_odds is None

        if cancelled_home:
            arb_message.home_win_stake = 0
        if cancelled_away:
            arb_message.away_win_stake = 0

        return cancelled_home, cancelled_away

    def calculate_and_update_profit(self, arb_message: ArbMessage):
        """Recalculates and updates the guaranteed profit."""
        arb_message.guaranteed_profit = calculate_guaranteed_profit(
            arb_message.home_win_stake,
            arb_message.away_win_stake,
            arb_message.home_win_odds,
            arb_message.away_win_odds
        )

    def determine_status(self, cancelled_home: bool, cancelled_away: bool, odds_changed: bool) -> str:
        """Determines the new status of the arbitrage execution."""
        if cancelled_home or cancelled_away:
            return "cancelled"
        elif odds_changed:
            return "adjusted"
        return "completed"

    def log_execution_status(self, status: str, id: str):
        """Logs the execution status message."""
        messages = {
            "cancelled": "❌ Arb cancelled",
            "adjusted": "⚠️ Arb executed with adjusted odds",
            "completed": "✅ Arb executed"
        }
        print(f"{messages.get(status, '❓ Unknown status')} - ID: {id}")

    def get_latest_odds(self, match: str, bookmaker: str, is_home_win: bool) -> Optional[float]:
        """Fetch the latest odds for a given (match, bookmaker) from Redis."""
        match_hash = get_odds_match_hash(match)
        bookmaker_key = get_odds_match_bookmaker_key(bookmaker)

        odds_json = self.redis_client.hget(match_hash, bookmaker_key)
        if odds_json is None:
            return None  # Odds were removed (cancelled)

        odds_data = json.loads(odds_json)
        odds = OddsValues(**odds_data)
        return odds.home_win if is_home_win else odds.away_win

    
    def publish_arb_execution(self, arb_message: ArbMessage):
        """Publishes the updated arbitrage execution result to Redis."""
        arb_data = json.dumps(arb_message.model_dump())
        self.redis_client.publish(shared_config.REDIS_ARB_EXECUTIONS_CHANNEL, arb_data)
        print(f"📢 Published ArbMessage to Redis: {arb_data}")
