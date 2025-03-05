export type MessageType = "odds_update" | "arb_detection" | "arb_execution";

export interface WebSocketMessage {
  message_type: MessageType;
  contents: any;
}