import { useState } from "react";
import { ArbMessage } from "../types";

export const ARB_WINDOW = 5 * 60 * 1000; // 5-minute window

export const useArbitrages = () => {
  const [arbitrages, setArbitrages] = useState<Record<string, ArbMessage>>({});

  const updateArbitrages = (arbData: ArbMessage) => {
    const now = Date.now();

    setArbitrages((prevArbs) => {
      const newArbs = {
        ...prevArbs,
        [arbData.id]: arbData
      };

      const filteredArbs = Object.fromEntries(
        Object.entries(newArbs).filter(([_, arb]) => now - arb.timestamp <= ARB_WINDOW)
      );

      return filteredArbs;
    });
  };

  return { arbitrages, updateArbitrages };
};
