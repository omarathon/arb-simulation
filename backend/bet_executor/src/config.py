import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class BetExecutorConfig:
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    EXECUTION_DELAY = int(os.getenv("EXECUTION_DELAY", 2))  # Simulated execution delay in seconds

bet_executor_config = BetExecutorConfig()
