# backend/main.py

from fastapi import FastAPI
from websocket_handler import websocket_endpoint
from redis_listener import start_redis_listener
from odds_publisher import start_odds_publisher

app = FastAPI()

# Include WebSocket endpoint
app.add_api_websocket_route("/ws", websocket_endpoint)

# Start background processes
start_redis_listener()
start_odds_publisher()
