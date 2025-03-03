from fastapi import WebSocket
import asyncio

from backend.gateway.src.models import WebSocketMessage

connected_clients = set()

async def websocket_endpoint(websocket: WebSocket):
    """Handles WebSocket connections for real-time updates."""
    await websocket.accept()
    connected_clients.add(websocket)
    print(f"WebSocket connected: {websocket.client}")

    try:
        while True:
            await asyncio.sleep(30)  # Keep the connection alive
            await websocket.send_text("ping")  # Simple keep-alive message
    except Exception:
        print(f"WebSocket disconnected: {websocket.client}")
    finally:
        connected_clients.discard(websocket)

async def broadcast_message(data: WebSocketMessage):
    """Send data to all connected WebSocket clients."""
    disconnected_clients = set()

    for ws in connected_clients:
        try:
            await ws.send_json(data.model_dump())
        except Exception:
            disconnected_clients.add(ws)

    # Remove disconnected clients
    connected_clients.difference_update(disconnected_clients)
