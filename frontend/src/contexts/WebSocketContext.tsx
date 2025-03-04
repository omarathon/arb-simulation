// /context/WebSocketContext.tsx
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

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { odds, updateOdds, updateOddsWithArbitrage } = useOdds();
  const { arbitrages, updateArbitrages } = useArbitrages();
  const { cumulativeProfits, totalProfit, updateProfit } = useProfit();

  useEffect(() => {
    const wsService = new WebSocketService(handleMessage);
    wsService.connect();

    return () => wsService.disconnect();
  }, []);

  const handleMessage = (message: WebSocketMessage) => {
    const { message_type, contents } = message;
  
    if (message_type === "odds_update") {
      updateOdds(contents);
      return;
    }
  
    if (message_type === "arb_detection" || message_type === "arb_execution") {
      updateArbitrages(contents);
      updateOddsWithArbitrage(contents);
    }
  
    if (message_type === "arb_execution" && ["completed", "adjusted", "cancelled"].includes(contents.status)) {
      updateProfit(contents.guaranteed_profit, contents.timestamp);
    }
  
    if (!["odds_update", "arb_detection", "arb_execution"].includes(message_type)) {
      console.warn("Unknown WebSocket message type:", message_type);
    }
  };
  

  return (
    <WebSocketContext.Provider value={{ odds, arbitrages, cumulativeProfits, totalProfit }}>
      {children}
    </WebSocketContext.Provider>
  );
};
