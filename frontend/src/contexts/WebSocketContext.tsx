import React, { createContext, useEffect } from "react";
import { WebSocketService } from "../services/WebSocketService";
import { useOdds } from "../hooks/useOdds";
import { useArbitrages } from "../hooks/useArbitrages";
import { useProfit } from "../hooks/useProfit";
import { WebSocketMessage } from "../types";

interface WebSocketContextProps {
  odds: any[];
  arbitrages: Record<string, any>;
  cumulativeProfits: { timestamp: number; profit: number }[];
  totalProfit: number;
}

export const WebSocketContext = createContext<WebSocketContextProps | undefined>(undefined);

// Pure message-handling function that can be tested independently.
export const handleMessage = (
  message: WebSocketMessage,
  handlers: {
    updateOdds: (contents: any) => void;
    updateOddsWithArbitrage: (contents: any) => void;
    updateArbitrages: (contents: any) => void;
    updateProfit: (profit: number, timestamp: number) => void;
  }
) => {
  const { message_type, contents } = message;

  if (message_type === "odds_update") {
    handlers.updateOdds(contents);
    return;
  }

  if (message_type === "arb_detection" || message_type === "arb_execution") {
    handlers.updateArbitrages(contents);
    handlers.updateOddsWithArbitrage(contents);
  }

  if (
    message_type === "arb_execution" &&
    ["completed", "adjusted", "cancelled"].includes(contents.status)
  ) {
    handlers.updateProfit(contents.guaranteed_profit, contents.timestamp);
  }

  if (!["odds_update", "arb_detection", "arb_execution"].includes(message_type)) {
    console.warn("Unknown WebSocket message type:", message_type);
  }
};

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { odds, updateOdds, updateOddsWithArbitrage } = useOdds();
  const { arbitrages, updateArbitrages } = useArbitrages();
  const { cumulativeProfits, totalProfit, updateProfit } = useProfit();

  const handleMessageWrapper = (message: WebSocketMessage) =>
    handleMessage(message, {
      updateOdds,
      updateOddsWithArbitrage,
      updateArbitrages,
      updateProfit,
    });

  useEffect(() => {
    const wsService = new WebSocketService(handleMessageWrapper);
    wsService.connect();
    return () => wsService.disconnect();
  }, []);

  return (
    <WebSocketContext.Provider value={{ odds, arbitrages, cumulativeProfits, totalProfit }}>
      {children}
    </WebSocketContext.Provider>
  );
};
