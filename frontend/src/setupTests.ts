import "@testing-library/jest-dom";
import { WebSocketContext } from "./contexts/WebSocketContext";
import { render } from "@testing-library/react";
import React from "react";

interface MockWebSocketContextProps {
  odds?: any[];
}

export const MockWebSocketProvider: React.FC<MockWebSocketContextProps> = ({ children, odds = [] }) => {
  return <WebSocketContext.Provider value={{ odds }}>{children}</WebSocketContext.Provider>;
};

// ✅ Custom render function with WebSocket Context
export const renderWithWebSocket = (ui: React.ReactElement, { odds = [], ...options } = {}) =>
  render(ui, { wrapper: ({ children }) => <MockWebSocketProvider odds={odds}>{children}</MockWebSocketProvider>, ...options });
