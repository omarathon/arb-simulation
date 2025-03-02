import time
from sqlalchemy.orm import sessionmaker
from backend.shared.database import engine
from backend.shared.models import Odds
from backend.scraper.src.config import scraper_config

SessionTesting = sessionmaker(bind=engine)

def test_scraper_stores_odds_in_database():
    """Test that the scraper correctly stores odds in the test PostgreSQL database."""

    session = SessionTesting()

    # Wait for odds to be published
    time.sleep(scraper_config.ODDS_PUBLISH_INTERVAL + 2)

    stored_odds = session.query(Odds).all()
    session.close()

    assert stored_odds, "No odds were stored in the database!"
    
    first_odd = stored_odds[0]
    assert first_odd.match, "Missing 'match' field"
    assert first_odd.bookmaker, "Missing 'bookmaker' field"
    assert first_odd.home_win is not None, "Missing 'home_win' field"
    assert first_odd.draw is not None, "Missing 'draw' field"
    assert first_odd.away_win is not None, "Missing 'away_win' field"
