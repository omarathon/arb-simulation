import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ScraperConfig:
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    ODDS_PUBLISH_INTERVAL = int(os.getenv("ODDS_PUBLISH_INTERVAL", 5))

scraper_config = ScraperConfig()
