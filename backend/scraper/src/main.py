from fastapi import FastAPI, WebSocket
from backend.scraper.src.websocket_handler import websocket_endpoint
from backend.scraper.src.redis_listener import start_redis_listener
from backend.scraper.src.odds_publisher import start_odds_publisher
from backend.shared.database import init_db

app = FastAPI(
    title="Scraper API",
    description="API for scraping and publishing odds",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "OK"}

init_db()

app.add_api_websocket_route("/ws", websocket_endpoint)

# Start backend processes
start_redis_listener()
start_odds_publisher()
