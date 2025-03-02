import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ArbDetectorConfig:
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    ARB_THRESHOLD = float(os.getenv("ARB_THRESHOLD", 0.02))  # Arbitrage detection threshold

arb_detector_config = ArbDetectorConfig()
