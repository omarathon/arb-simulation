from fastapi import WebSocket
import asyncio

connected_clients = []

async def websocket_endpoint(websocket: WebSocket):
    """Handles WebSocket connections for real-time updates."""
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except Exception:
        connected_clients.remove(websocket)

async def broadcast_message(data):
    """Send data to all connected WebSocket clients."""
    for ws in connected_clients:
        await ws.send_json(data)