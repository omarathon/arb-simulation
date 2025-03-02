import pytest
import time
from backend.scraper.src.config import scraper_config

@pytest.mark.timeout(scraper_config.ODDS_PUBLISH_INTERVAL + 10)
def test_websocket_receives_odds():
    """Test if WebSocket sends live odds to clients."""
    
    ws_url = "ws://test_scraper:8001/ws"
    
    import websocket
    
    ws = websocket.create_connection(ws_url)

    try:
        ws.send("subscribe")
        time.sleep(scraper_config.ODDS_PUBLISH_INTERVAL + 2)
        response = ws.recv()
        assert response is not None, "No data received from WebSocket!"
        assert "match" in response, f"Unexpected response: {response}"
    finally:
        ws.close()
