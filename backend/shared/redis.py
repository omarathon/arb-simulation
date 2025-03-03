from typing import Literal, Optional
from pydantic import BaseModel

class OddsValues(BaseModel):
    home_win: float
    away_win: float

class OddsUpdateMessage(BaseModel):
    """Represents a message for an odds update."""
    event: Literal["odds_close", "odds_update"]
    match: str
    bookmaker: str
    odds: Optional[OddsValues]

class ArbMessage(BaseModel):
    id: str
    match: str
    home_win_bookmaker: str
    away_win_bookmaker: str
    home_win_odds: Optional[float]
    away_win_odds: Optional[float]
    home_win_stake: float
    away_win_stake: float
    guaranteed_payout: float
    status: Literal["detected", "completed", "cancelled", "adjusted"] # Adjusted if the odds changed. Cancelled if one of the odds closed.
    timestamp: int # ms since epoch

def get_odds_match_hash(match: str) -> str:
    return f"odds:{match.replace(' ', '_')}"

def get_odds_match_bookmaker_key(bookmaker: str) -> str:
    return bookmaker.replace(' ', '_')

def get_bookmaker_key_full_name(bookmaker_key: str) -> str:
    return bookmaker_key.replace('_', ' ')