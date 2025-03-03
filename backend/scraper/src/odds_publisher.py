import redis
import json
import asyncio
import random
from decimal import Decimal
from collections import defaultdict
from sqlalchemy.orm import Session
from backend.scraper.src.config import ScraperConfig
from backend.shared.database import get_db
from backend.shared.models import Odds

redis_client = redis.Redis(host=ScraperConfig.REDIS_HOST, port=ScraperConfig.REDIS_PORT, db=0)

# Track state for each (bookmaker, match) pair
odds_state = defaultdict(lambda: {
    "tick": random.randint(0, 9),  # Start at a random tick to desynchronize closings
    "closed": False,
    "closed_ticks": 0
})

def store_odds(db: Session, match: str, bookmaker: str, home_win: float, draw: float, away_win: float, is_active: bool):
    """Stores or updates odds in the database."""
    existing_odd = db.query(Odds).filter_by(match=match, bookmaker=bookmaker, actionable=True).first()
    
    if existing_odd:
        # Mark previous odds as inactive
        existing_odd.actionable = False

    # Insert new odds or closed state
    new_odds = Odds(
        match=match,
        bookmaker=bookmaker,
        home_win=Decimal(home_win) if is_active else None,
        draw=Decimal(draw) if is_active else None,
        away_win=Decimal(away_win) if is_active else None,
        actionable=is_active
    )
    db.add(new_odds)
    db.commit()

async def publish_odds_loop():
    """Generates and publishes mock odds with randomized open/close cycles."""

    matches = ["Man Utd vs Chelsea", "Liverpool vs Arsenal", "Barcelona vs Real Madrid"]
    bookmakers = ["Bet365", "Smarkets", "Betfair"]

    while True:
        db = next(get_db())

        await asyncio.sleep(ScraperConfig.ODDS_PUBLISH_INTERVAL)
        
        for match in matches:
            for bookmaker in bookmakers:
                
                state = odds_state[(bookmaker, match)]

                # Check if odds are currently closed
                if state["closed"]:
                    state["closed_ticks"] += 1

                    if state["closed_ticks"] >= 5:
                        # Reopen odds
                        state["closed"] = False
                        state["tick"] = 0
                        state["closed_ticks"] = 0
                        print(f"🔓 {bookmaker} reopens odds for {match}")

                    
                    continue # Skip publishing odds while closed

                # Every 9 ticks, close odds for 5 ticks
                if state["tick"] >= 9:
                    state["closed"] = True
                    state["closed_ticks"] = 0

                    # Persist closure
                    odds_data = {
                        "event": "odds_update",
                        "match": match,
                        "bookmaker": bookmaker,
                        "odds": {
                            "home_win": None,
                            "draw": None,
                            "away_win": None
                        }
                    }

                    store_odds(db, match, bookmaker, 
                               odds_data["odds"]["home_win"], 
                               odds_data["odds"]["draw"], 
                               odds_data["odds"]["away_win"], 
                               is_active=False)
                    
                    # Notify closure
                    redis_client.publish("odds_update", json.dumps(odds_data))
                    print(f"❌ {bookmaker} closed odds for {match}")

                else: # Odds are open
                    # Persist updated odds
                    odds_data = {
                        "event": "odds_update",
                        "match": match,
                        "bookmaker": bookmaker,
                        "odds": {
                            "home_win": round(random.uniform(1.6, 3.2), 2),
                            "draw": round(random.uniform(2.5, 4.5), 2),
                            "away_win": round(random.uniform(1.6, 3.2), 2)
                        }
                    }

                    store_odds(db, match, bookmaker, 
                               odds_data["odds"]["home_win"], 
                               odds_data["odds"]["draw"], 
                               odds_data["odds"]["away_win"], 
                               is_active=True)
                    
                    # Notify updated odds
                    redis_client.publish("odds_update", json.dumps(odds_data))
                    print(f"✅ {bookmaker} updated odds for {match}")

                # Update tick count
                state["tick"] += 1

def start_odds_publisher():
    """Starts the odds publishing loop in a background thread."""
    import threading
    threading.Thread(target=asyncio.run, args=(publish_odds_loop(),)).start()
