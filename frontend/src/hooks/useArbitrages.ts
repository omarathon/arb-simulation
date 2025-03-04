import { useState } from "react";
import { ArbMessage } from "../types";

const ARB_WINDOW = 5 * 60 * 1000; // 5-minute window

export const useArbitrages = () => {
  const [arbitrages, setArbitrages] = useState<Record<string, ArbMessage>>({});

  const updateArbitrages = (arbData: ArbMessage) => {
    const now = Date.now();

    setArbitrages((prevArbs) => {
      const filteredArbs = Object.fromEntries(
        Object.entries(prevArbs).filter(([_, arb]) => now - arb.timestamp <= ARB_WINDOW)
      );

      return {
        ...filteredArbs,
        [arbData.id]: arbData, // ✅ Add new or updated arbitrage
      };
    });
  };

  return { arbitrages, updateArbitrages };
};
