import React, { createContext, useEffect, useState, ReactNode } from "react";
import { CONFIG } from "../config";

interface OddsData {
  event: string;
  match: string;
  bookmaker: string;
  odds: {
    home_win: number;
    away_win: number;
  } | null;
}

interface WebSocketContextProps {
  odds: OddsData[];
}

export const WebSocketContext = createContext<WebSocketContextProps | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [odds, setOdds] = useState<OddsData[]>([]);

  useEffect(() => {
    const ws = new WebSocket(CONFIG.WEBSOCKET_URL);

    ws.onmessage = (event) => {
      try {
        const data: OddsData = JSON.parse(event.data);
        setOdds((prevOdds) => {
          const existingIndex = prevOdds.findIndex(
            (o) => o.match === data.match && o.bookmaker === data.bookmaker
          );

          if (existingIndex !== -1) {
            const updatedOdds = [...prevOdds];
            updatedOdds[existingIndex] = data;
            return updatedOdds;
          } else {
            return [...prevOdds, data];
          }
        });
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    ws.onopen = () => console.log("Connected to WebSocket");
    ws.onerror = (error) => console.error("WebSocket Error:", error);
    ws.onclose = () => console.log("WebSocket Disconnected");

    return () => ws.close();
  }, []);

  return (
    <WebSocketContext.Provider value={{ odds }}>
      {children}
    </WebSocketContext.Provider>
  );
};
