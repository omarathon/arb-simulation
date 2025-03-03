import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.scraper.src.odds_publisher import OddsPublisher

odds_publisher = OddsPublisher()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the odds publisher as a background task on app startup."""
    task = asyncio.create_task(odds_publisher.publish_odds())
    yield
    task.cancel()  # Stop the background task when shutting down
    print("Scraper shutting down...")
    
app = FastAPI(
    title="Scraper API",
    description="API for scraping and publishing odds",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "OK"}