import { renderHook, act } from "@testing-library/react";
import { useOdds } from "../../hooks";
import { OddsData, ArbMessage, ArbStatus } from "../../types";

describe("useOdds Hook", () => {
  test("adds odds correctly", () => {
    // Arrange
    const { result } = renderHook(() => useOdds());
    const newOdds: OddsData = {
      event: "odds_update",
      match: "Team A vs Team B",
      bookmaker: "Bookmaker 1",
      odds: { home_win: 2.0, away_win: 3.5 },
      arb_status: null,
      timestamp: Date.now(),
    };

    // Act - add new odd
    act(() => {
      result.current.updateOdds(newOdds);
    });

    // Assert odd was added
    expect(result.current.odds).toHaveLength(1);
    expect(result.current.odds[0]).toEqual(newOdds);
  });

  test("updates odds correctly", () => {
    // Arrange
    const { result } = renderHook(() => useOdds());
    const initialOdds: OddsData = {
      event: "odds_update",
      match: "Team A vs Team B",
      bookmaker: "Bookmaker 1",
      odds: { home_win: 2.0, away_win: 3.5 },
      arb_status: null,
      timestamp: Date.now(),
    };
    const updatedOdds: OddsData = {
      event: "odds_update",
      match: "Team A vs Team B",
      bookmaker: "Bookmaker 1",
      odds: { home_win: 1.5, away_win: 2.7 },
      arb_status: null,
      timestamp: Date.now(),
    };

    // Act - add initial odds
    act(() => {
        result.current.updateOdds(initialOdds);
    });

    // Act - update odd
    act(() => {
      result.current.updateOdds(updatedOdds);
    });

    // Assert odd was updated
    expect(result.current.odds).toHaveLength(1);
    expect(result.current.odds[0]).toEqual(updatedOdds);
  });

  describe("useOdds Hook", () => {
    it.each([
      ["detected" as ArbStatus],
      ["completed" as ArbStatus],
    ])("updates arbitrage status to %s in existing odds", (status) => {
      // Arrange
      const { result } = renderHook(() => useOdds());
  
      const initialOdds: OddsData = {
        event: "odds_update",
        match: "Team A vs Team B",
        bookmaker: "Bookmaker 1",
        odds: { home_win: 2.0, away_win: 3.5 },
        arb_status: null,
        timestamp: Date.now(),
      };
      const arbMessage: ArbMessage = {
        id: "arb-1",
        match: "Team A vs Team B",
        home_win_bookmaker: "Bookmaker 1",
        away_win_bookmaker: "Bookmaker 2",
        home_win_odds: 2.0,
        away_win_odds: 3.5,
        home_win_stake: 100,
        away_win_stake: 50,
        guaranteed_profit: 20,
        status,
        timestamp: Date.now(),
      };
  
      // Act - set initial odds
      act(() => {
        result.current.updateOdds(initialOdds);
      });
  
      // Act - update status of any odds within the arbitrage
      act(() => {
        result.current.updateOddsWithArbitrage(arbMessage);
      });
  
      // Assert - ensure arbitrage status was updated for the odds in the arb
      expect(result.current.odds).toHaveLength(1);
      expect(result.current.odds[0].arb_status).toBe(status);
      expect(result.current.odds[0].odds).toEqual({ home_win: 2.0, away_win: 3.5 }); // Ensure odds remain unchanged
    });
  });

  test("does not update arbitrage status in non-matching existing odds", () => {
    // Arrange
    const { result } = renderHook(() => useOdds());
    const initialOdds: OddsData = {
      event: "odds_update",
      match: "Team C vs Team D",
      bookmaker: "Bookmaker X",
      odds: { home_win: 1.5, away_win: 2.8 },
      arb_status: null,
      timestamp: Date.now(),
    };
    const arbMessage: ArbMessage = {
      id: "arb-2",
      match: "Team A vs Team B", // Doesn't match the oddsEntry match
      home_win_bookmaker: "Bookmaker 1",
      away_win_bookmaker: "Bookmaker 2",
      home_win_odds: 2.0,
      away_win_odds: 3.5,
      home_win_stake: 100,
      away_win_stake: 50,
      guaranteed_profit: 20,
      status: "detected",
      timestamp: Date.now(),
    };

    // Act - add the initial odds
    act(() => {
      result.current.updateOdds(initialOdds);
    });

    // Act - update status of any odds within the arbitrage
    act(() => {
      result.current.updateOddsWithArbitrage(arbMessage);
    });

    // Assert - ensure that the unrelated odds were not affected
    expect(result.current.odds).toHaveLength(1);
    expect(result.current.odds[0].arb_status).toBeNull();
  });
});
