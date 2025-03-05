import { useState } from "react";
import { OddArbStatus, OddsData } from "../types";
import { ArbMessage, isValidOddArbStatus } from "../types";

export const useOdds = () => {
  // Collection of odds for every (match,bookmaker)
  const [odds, setOdds] = useState<OddsData[]>([]);

  // Update the stored odds for the given (match,bookmaker)
  const updateOdds = (newOdds: OddsData) => {
    setOdds((prevOdds) => {
      // Update odds for the existing (match,bookmaker) if we already have odds for them.
      const updatedOdds = prevOdds.map((o) =>
        o.match === newOdds.match && o.bookmaker === newOdds.bookmaker
          ? { ...newOdds, arb_status: null } // Reset arb_status if the odds are updated
          : o
      );

      // Add a new odd for a new (match,bookmaker) if we don't have odds for them yet.
      if (!updatedOdds.some((o) => o.match === newOdds.match && o.bookmaker === newOdds.bookmaker)) {
        updatedOdds.push({ ...newOdds, arb_status: null }); // New odd
      }

      return updatedOdds;
    });
  };

  // Updates the arb_status of odds contained in an arbitrage.
  const updateOddsWithArbitrage = (arbData: ArbMessage) => {
    
    if (!isValidOddArbStatus(arbData.status)) 
      return; // Not possible to transition an odd to this arb status (e.g. adjusted) 
  
    // The arb status is valid for an odd. Update the arb status of matching odds (i.e. odds which are part of the arb)
    setOdds((prevOdds) =>
      prevOdds.map((o) =>
        (o.match === arbData.match &&
          ((o.bookmaker === arbData.home_win_bookmaker && o.odds?.home_win === arbData.home_win_odds) ||
            (o.bookmaker === arbData.away_win_bookmaker && o.odds?.away_win === arbData.away_win_odds)))
          ? { ...o, arb_status: arbData.status as OddArbStatus }
          : o
      )
    );
  };
  
  return { odds, updateOdds, updateOddsWithArbitrage };
};
