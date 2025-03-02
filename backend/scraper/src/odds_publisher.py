import redis
import json
import asyncio
import random
from sqlalchemy.orm import Session
from backend.scraper.src.config import ScraperConfig
from backend.shared.database import get_db
from backend.shared.models import Odds

redis_client = redis.Redis(host=ScraperConfig.REDIS_HOST, port=ScraperConfig.REDIS_PORT, db=0)

def store_odds(db: Session, match: str, bookmaker: str, home_win: float, draw: float, away_win: float):
    """Stores odds in the database."""
    new_odds = Odds(
        match=match,
        bookmaker=bookmaker,
        home_win=home_win,
        draw=draw,
        away_win=away_win
    )
    db.add(new_odds)
    db.commit()

async def publish_odds_loop():
    """Generates and publishes mock odds to Redis periodically."""
    matches = ["Man Utd vs Chelsea", "Liverpool vs Arsenal", "Barcelona vs Real Madrid"]
    bookmakers = ["Bet365", "Smarkets"]

    while True:
        db = next(get_db())
        for match in matches:
            for bookmaker in bookmakers:
                odds_data = {
                    "match": match,
                    "bookmaker": bookmaker,
                    "odds": {
                        "home_win": round(random.uniform(1.8, 2.5), 2),
                        "draw": round(random.uniform(3.0, 4.0), 2),
                        "away_win": round(random.uniform(1.8, 2.5), 2)
                    }
                }
                redis_client.publish("odds_update", json.dumps(odds_data))
                
                # Store in PostgreSQL
                store_odds(db, match, bookmaker, 
                           odds_data["odds"]["home_win"], 
                           odds_data["odds"]["draw"], 
                           odds_data["odds"]["away_win"])
        
        await asyncio.sleep(ScraperConfig.ODDS_PUBLISH_INTERVAL)

def start_odds_publisher():
    """Starts the odds publishing loop in a background thread."""
    import threading
    threading.Thread(target=asyncio.run, args=(publish_odds_loop(),)).start()
