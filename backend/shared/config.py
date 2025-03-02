import os

class SharedConfig:
    DB_HOST = os.getenv("POSTGRES_HOST", "db")
    DB_NAME = os.getenv("POSTGRES_DB", "odds_db")
    DB_USER = os.getenv("POSTGRES_USER", "admin")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
    DB_PORT = int(os.getenv("POSTGRES_PORT", 5432))
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

shared_config = SharedConfig()
