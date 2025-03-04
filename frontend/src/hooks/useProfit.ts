import { useState } from "react";

const PROFIT_WINDOW = 5 * 60 * 1000; // 5-minute window

export const useProfit = () => {
  const [cumulativeProfits, setCumulativeProfits] = useState<{ timestamp: number; profit: number }[]>([]);
  const [totalProfit, setTotalProfit] = useState<number>(0);

  const updateProfit = (profit: number, timestamp: number) => {
    setTotalProfit((prevTotal) => prevTotal + profit);

    setCumulativeProfits((prev) => {
      const newEntry = {
        timestamp,
        profit: (prev.length ? prev[prev.length - 1].profit : 0) + profit,
      };

      return [...prev, newEntry].filter((entry) => timestamp - entry.timestamp <= PROFIT_WINDOW);
    });
  };

  return { cumulativeProfits, totalProfit, updateProfit };
};
