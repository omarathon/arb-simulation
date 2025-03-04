import { CONFIG } from "../config";
import { WebSocketMessage } from "../types";

export class WebSocketService {
  private ws: WebSocket | null = null;
  private onMessageHandler: (message: WebSocketMessage) => void;

  constructor(onMessageHandler: (message: WebSocketMessage) => void) {
    this.onMessageHandler = onMessageHandler;
  }

  connect() {
    this.ws = new WebSocket(CONFIG.WEBSOCKET_URL);

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.onMessageHandler(message);
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    this.ws.onopen = () => console.log("✅ Connected to WebSocket");
    this.ws.onerror = (error) => console.error("❌ WebSocket Error:", error);
    this.ws.onclose = () => console.log("🔴 WebSocket Disconnected");
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
