import redis
import json
import asyncio
import random
import psycopg2

redis_client = redis.Redis(host='redis', port=6379, db=0)

# PostgreSQL Connection
conn = psycopg2.connect(
    dbname='odds_db', user='admin', password='password', host='db', port=5432
)
cursor = conn.cursor()

async def publish_odds_loop():
    """Generates and publishes mock odds to Redis periodically."""
    matches = ["Man Utd vs Chelsea", "Liverpool vs Arsenal", "Barcelona vs Real Madrid"]
    bookmakers = ["Bet365", "Smarkets"]

    while True:
        for match in matches:
            for bookmaker in bookmakers:
                odds = {
                    "match": match,
                    "bookmaker": bookmaker,
                    "odds": {
                        "home_win": round(random.uniform(1.8, 2.5), 2),
                        "draw": round(random.uniform(3.0, 4.0), 2),
                        "away_win": round(random.uniform(1.8, 2.5), 2)
                    }
                }
                redis_client.publish("odds_update", json.dumps(odds))
                
                # Store in PostgreSQL
                cursor.execute(
                    "INSERT INTO Odds (match, bookmaker, home_win, draw, away_win) VALUES (%s, %s, %s, %s, %s)",
                    (match, bookmaker, odds["odds"]["home_win"], odds["odds"]["draw"], odds["odds"]["away_win"])
                )
                conn.commit()
        
        await asyncio.sleep(5)  # Publish new odds every 5 seconds

def start_odds_publisher():
    """Starts the odds publishing loop in a background thread."""
    import threading
    threading.Thread(target=asyncio.run, args=(publish_odds_loop(),)).start()
