import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.scraper.src.odds_publisher import OddsPublisher
from backend.shared.logging import setup_logging
from backend.shared.redis_client import redis_client
from backend.scraper.src.config import scraper_config

setup_logging()

odds_publisher = OddsPublisher(redis_client, scraper_config.ODDS_SEED)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(odds_publisher.publish_odds())
    yield
    task.cancel()
    
app = FastAPI(
    title="Scraper",
    description="Server which scrapes and publishes odds.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "OK"}