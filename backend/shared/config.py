import os

class SharedConfig:
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

    REDIS_ODDS_UPDATE_CHANNEL = os.getenv("REDIS_ODDS_UPDATE_CHANNEL", "odds_update")
    REDIS_ARB_DETECTIONS_CHANNEL = os.getenv("REDIS_ARB_DETECTIONS_CHANNEL", "arb_detection")
    REDIS_ARB_EXECUTIONS_CHANNEL = os.getenv("REDIS_ARB_EXECUTIONS_CHANNEL", "arb_execution")

shared_config = SharedConfig()
