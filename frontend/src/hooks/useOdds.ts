import { useState } from "react";
import { OddArbStatus, OddsData } from "../types";
import { ArbMessage, isValidOddArbStatus } from "../types";

export const useOdds = () => {
  const [odds, setOdds] = useState<OddsData[]>([]);

  const updateOdds = (data: OddsData) => {
    setOdds((prevOdds) => {
      const updatedOdds = prevOdds.map((o) =>
        o.match === data.match && o.bookmaker === data.bookmaker
          ? { ...data, arb_status: null } // Reset arb_status initially
          : o
      );

      if (!updatedOdds.some((o) => o.match === data.match && o.bookmaker === data.bookmaker)) {
        updatedOdds.push({ ...data, arb_status: null });
      }

      return updatedOdds;
    });
  };

  const updateOddsWithArbitrage = (arbData: ArbMessage) => {
    if (!isValidOddArbStatus(arbData.status)) return;
  
    setOdds((prevOdds) =>
      prevOdds.map((o) =>
        (o.match === arbData.match &&
          ((o.bookmaker === arbData.home_win_bookmaker && o.odds?.home_win === arbData.home_win_odds) ||
            (o.bookmaker === arbData.away_win_bookmaker && o.odds?.away_win === arbData.away_win_odds)))
          ? { ...o, arb_status: arbData.status as OddArbStatus } // ✅ Now `arb_status` is guaranteed to be valid
          : o
      )
    );
  };
  
  return { odds, updateOdds, updateOddsWithArbitrage };
};
