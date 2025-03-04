import React, { createContext, useEffect, useState, ReactNode } from "react";
import { CONFIG } from "../config";

type MessageType = "odds_update" | "arb_detection" | "arb_execution";

interface WebSocketMessage {
  message_type: MessageType;
  contents: any;
}

interface OddsData {
  event: "odds_update" | "odds_close";
  match: string;
  bookmaker: string;
  odds: {
    home_win: number;
    away_win: number;
  } | null;
  arb_status?: "detected" | "completed" | null;
}

interface ArbMessage {
  id: string;
  match: string;
  home_win_bookmaker: string;
  away_win_bookmaker: string;
  home_win_odds?: number;
  away_win_odds?: number;
  home_win_stake: number;
  away_win_stake: number;
  guaranteed_payout: number;
  profit: number;
  status: "detected" | "completed" | "cancelled" | "adjusted";
  timestamp: number;
}

interface WebSocketContextProps {
  odds: OddsData[];
  arbitrages: Record<string, ArbMessage>;
  cumulativeProfits: { timestamp: number; profit: number }[];
  totalProfit: number;
}

export const WebSocketContext = createContext<WebSocketContextProps | undefined>(undefined);

const PROFIT_WINDOW = 5 * 60 * 1000; // 5-minute window

export const WebSocketProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [odds, setOdds] = useState<OddsData[]>([]);
  const [arbitrages, setArbitrages] = useState<Record<string, ArbMessage>>({});
  const [cumulativeProfits, setCumulativeProfits] = useState<{ timestamp: number; profit: number }[]>([]);
  const [totalProfit, setTotalProfit] = useState<number>(0);

  useEffect(() => {
    const ws = new WebSocket(CONFIG.WEBSOCKET_URL);

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);

        switch (message.message_type) {
          case "odds_update": {
            const data: OddsData = message.contents;
            setOdds((prevOdds) => {
              const updatedOdds = prevOdds.map((o) =>
                o.match === data.match && o.bookmaker === data.bookmaker
                  ? { ...data, arb_status: null }
                  : o
              );

              if (!updatedOdds.some((o) => o.match === data.match && o.bookmaker === data.bookmaker)) {
                updatedOdds.push({ ...data, arb_status: null });
              }

              return updatedOdds;
            });
            break;
          }

          case "arb_detection": {
            const arbData: ArbMessage = message.contents;

            // ✅ Store detected arbitrage, but do NOT update profit yet
            setArbitrages((prevArbs) => ({
              ...prevArbs,
              [arbData.id]: { ...arbData, profit: 0 }, // No profit yet
            }));

            setOdds((prevOdds) =>
              prevOdds.map((o) =>
                (o.match === arbData.match &&
                  ((o.bookmaker === arbData.home_win_bookmaker && o.odds?.home_win === arbData.home_win_odds) ||
                    (o.bookmaker === arbData.away_win_bookmaker && o.odds?.away_win === arbData.away_win_odds)))
                  ? { ...o, arb_status: "detected" }
                  : o
              )
            );
            break;
          }

          case "arb_execution": {
            const arbData: ArbMessage = message.contents;

            if (["completed", "adjusted", "cancelled"].includes(arbData.status)) {
              const profit = arbData.guaranteed_payout - (arbData.home_win_stake + arbData.away_win_stake);

              setArbitrages((prevArbs) => ({
                ...prevArbs,
                [arbData.id]: { ...arbData, profit },
              }));

              setTotalProfit((prevTotal) => prevTotal + profit);

              // ✅ Keep only last 5 minutes of profit data
              setCumulativeProfits((prev) => {
                const newEntry = {
                  timestamp: arbData.timestamp,
                  profit: (prev.length ? prev[prev.length - 1].profit : 0) + profit,
                };

                return [...prev, newEntry].filter((entry) => arbData.timestamp - entry.timestamp <= PROFIT_WINDOW);
              });

              // ✅ Update odds status to "completed" if odds didn't change
              setOdds((prevOdds) =>
                prevOdds.map((o) =>
                  (o.match === arbData.match &&
                    ((o.bookmaker === arbData.home_win_bookmaker && o.odds?.home_win === arbData.home_win_odds) ||
                      (o.bookmaker === arbData.away_win_bookmaker && o.odds?.away_win === arbData.away_win_odds)))
                    ? { ...o, arb_status: "completed" }
                    : o
                )
              );
            }

            break;
          }

          default:
            console.warn("Unknown WebSocket message type:", message.message_type);
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    ws.onopen = () => console.log("✅ Connected to WebSocket");
    ws.onerror = (error) => console.error("❌ WebSocket Error:", error);
    ws.onclose = () => console.log("🔴 WebSocket Disconnected");

    return () => ws.close();
  }, []);

  return (
    <WebSocketContext.Provider value={{ odds, arbitrages, cumulativeProfits, totalProfit }}>
      {children}
    </WebSocketContext.Provider>
  );
};
