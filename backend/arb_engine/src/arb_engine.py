import uuid
import redis
import json
from typing import List, Dict
from backend.arb_engine.src.config import arb_engine_config
from backend.shared.config import shared_config
from backend.shared.arb_math import calculate_guaranteed_profit

from backend.scraper.src.odds_publisher import OddsUpdateMessage

from backend.shared.redis import ArbMessage, OddsValues
from backend.shared.redis import get_odds_match_hash, get_bookmaker_key_full_name

from pydantic import ValidationError

from backend.shared.utils import current_milli_time
import logging
    

class ArbOpportunity:
    """Math for valid arb opportunities."""

    match: str
    bookmaker_home_win: str
    bookmaker_away_win: str
    odds_home_win: float
    odds_away_win: float

    def __init__(self, match: str, bookmaker_home_win: str, bookmaker_away_win: str, odds_home_win: float, odds_away_win: float):
        self.match = match
        self.bookmaker_home_win = bookmaker_home_win
        self.bookmaker_away_win = bookmaker_away_win
        self.odds_home_win = odds_home_win
        self.odds_away_win = odds_away_win

    def get_probability_home_win(self) -> float:
        return 1.0 / self.odds_home_win
    
    def get_probability_away_win(self) -> float:
        return 1.0 / self.odds_away_win
    
    def get_combined_market_margin(self) -> float:
        return self.get_probability_home_win() + self.get_probability_away_win()

    def is_net_gain(self) -> bool:
        return self.get_combined_market_margin() < 1.0

    # Based on https://help.smarkets.com/hc/en-gb/articles/115001175531-How-to-calculate-arbitrage-betting#:~:text=stake%20%C2%A3100%20overall.-,Stake%20at%20each%20bookmaker%20%3D%20(Overall%20stake%20*%20Bookmaker%20implied%20probability)/Combined%20market%20margin,-Example%3A%20Bookmaker%20A 
    def compute_stake_at_bookmaker(self, is_home_win_bookmaker: bool, overall_stake: float) -> float:
        implied_probability = self.get_probability_home_win() if is_home_win_bookmaker else self.get_probability_away_win()
        return (overall_stake * implied_probability) / self.get_combined_market_margin()
    

class ArbEngine:
    """Detects and publishes valid arbitrage opportunities to Redis."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client: redis.Redis = redis_client

    async def detect_arb_and_publish_bets(self, odds_update: OddsUpdateMessage):
        all_bookmaker_odds = self.get_all_odds_for_match(odds_update.match)

        if not all_bookmaker_odds:
            logging.info(f"No other odds found for match: {odds_update.match}")
            return

        arbs = self.find_arbitrage_opportunities(odds_update, all_bookmaker_odds)

        for arb in arbs:
            if arb.is_net_gain():
                arb_message = self.create_arb_message(arb)
                self.publish_arb_message(arb_message)
                logging.info(f"📢 Published ArbOpportunity: {arb.match} | {arb.bookmaker_home_win} vs {arb.bookmaker_away_win}")

    def get_all_odds_for_match(self, match: str) -> Dict[str, OddsValues]:
        """Retrieve all stored odds for a given match from Redis."""
        match_hash = get_odds_match_hash(match)
        odds_data = self.redis_client.hgetall(match_hash)

        all_odds = {}
        for bookmaker_key, odds_json in odds_data.items():
            bookmaker = get_bookmaker_key_full_name(bookmaker_key)

            try:
                odds_dict = json.loads(odds_json)
                odds = OddsValues(**odds_dict)
                all_odds[bookmaker] = odds
            except json.JSONDecodeError:
                logging.error(f"Failed to decode JSON for match={match}, bookmaker={bookmaker}: {repr(odds_json)}", exc_info=True)
            except ValidationError:
                logging.error(f"Invalid OddsValues format for match={match}, bookmaker={bookmaker}", exc_info=True)

        return all_odds

    def find_arbitrage_opportunities(self, odds_update: OddsUpdateMessage, all_bookmaker_odds: Dict[str, OddsValues]) -> List[ArbOpportunity]:
        """Find arbitrage opportunities using the newly received odds and other bookmakers' odds."""
        if not odds_update.odds:
            return []

        arbs = []
        used_bookmakers = {odds_update.bookmaker}

        for bookmaker, odds in all_bookmaker_odds.items():
            if bookmaker in used_bookmakers or odds is None:
                continue

            # Create arbitrage opportunity where `odds_update.bookmaker` is home
            arb1 = ArbOpportunity(
                match=odds_update.match,
                bookmaker_home_win=odds_update.bookmaker,
                bookmaker_away_win=bookmaker,
                odds_home_win=odds_update.odds.home_win,
                odds_away_win=odds.away_win
            )

            # Create arbitrage opportunity where `bookmaker` is home
            arb2 = ArbOpportunity(
                match=odds_update.match,
                bookmaker_home_win=bookmaker,
                bookmaker_away_win=odds_update.bookmaker,
                odds_home_win=odds.home_win,
                odds_away_win=odds_update.odds.away_win
            )

            if arb1.is_net_gain():
                arbs.append(arb1)
                used_bookmakers.add(arb1.bookmaker_home_win)
                used_bookmakers.add(arb1.bookmaker_away_win)
            elif arb2.is_net_gain():
                arbs.append(arb2)
                used_bookmakers.add(arb2.bookmaker_home_win)
                used_bookmakers.add(arb2.bookmaker_away_win)

        return arbs


    def create_arb_message(self, arb: ArbOpportunity) -> ArbMessage:
        """Create an ArbMessage for Redis publishing."""
        overall_stake = arb_engine_config.TOTAL_STAKE_PER_ARB

        stake_home = arb.compute_stake_at_bookmaker(is_home_win_bookmaker=True, overall_stake=overall_stake)
        stake_away = arb.compute_stake_at_bookmaker(is_home_win_bookmaker=False, overall_stake=overall_stake)

        guaranteed_profit = calculate_guaranteed_profit(
            stake_home, stake_away, arb.odds_home_win, arb.odds_away_win
        )

        return ArbMessage(
            id=str(uuid.uuid4()),  # Generate unique ID for tracking
            match=arb.match,
            home_win_bookmaker=arb.bookmaker_home_win,
            away_win_bookmaker=arb.bookmaker_away_win,
            home_win_odds=arb.odds_home_win,
            away_win_odds=arb.odds_away_win,
            home_win_stake=stake_home,
            away_win_stake=stake_away,
            guaranteed_profit=guaranteed_profit,
            status="detected",
            timestamp=current_milli_time()
        )

    def publish_arb_message(self, arb_message: ArbMessage):
        """Publish the detected arbitrage opportunity to Redis."""
        arb_data = json.dumps(arb_message.model_dump())
        self.redis_client.publish(shared_config.REDIS_ARB_DETECTIONS_CHANNEL, arb_data)
        logging.info(f"Published ArbMessage to Redis: {arb_data}")