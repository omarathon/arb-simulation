import { renderHook, act } from "@testing-library/react";
import { ARB_WINDOW, useArbitrages } from "../../hooks";
import { ArbMessage } from "../../types";

describe("useArbitrages hook", () => {
  test("adds an arbitrage correctly", () => {
    // Arrange
    const { result } = renderHook(() => useArbitrages());
    const arb: ArbMessage = {
      id: "arb-1",
      match: "Team A vs Team B",
      home_win_bookmaker: "Bookmaker 1",
      away_win_bookmaker: "Bookmaker 2",
      home_win_odds: 1.9,
      away_win_odds: 2.4,
      home_win_stake: 100,
      away_win_stake: 50,
      guaranteed_profit: 20,
      status: "detected",
      timestamp: Date.now(),
    };

    // Act - add arb
    act(() => {
      result.current.updateArbitrages(arb);
    });

    // Assert - check arb is added
    const keys = Object.keys(result.current.arbitrages);
    expect(keys).toHaveLength(1);
    expect(result.current.arbitrages[arb.id]).toEqual(arb);
  });

  test("updates arbitrage and filters out expired entries", () => {
    // Arrange
    const { result } = renderHook(() => useArbitrages());
    const now = Date.now();

    const validArb: ArbMessage = {
      id: "arb-1",
      match: "Team A vs Team B",
      home_win_bookmaker: "Bookmaker 1",
      away_win_bookmaker: "Bookmaker 2",
      home_win_odds: 2.0,
      away_win_odds: 3.5,
      home_win_stake: 100,
      away_win_stake: 50,
      guaranteed_profit: 20,
      status: "detected",
      timestamp: now - Math.floor(ARB_WINDOW / 2), // Recent entry
    };

    const expiredArb: ArbMessage = {
      id: "arb-2",
      match: "Team C vs Team D",
      home_win_bookmaker: "Bookmaker 3",
      away_win_bookmaker: "Bookmaker 4",
      home_win_odds: 1.8,
      away_win_odds: 2.9,
      home_win_stake: 80,
      away_win_stake: 40,
      guaranteed_profit: 15,
      status: "completed",
      timestamp: now - 2 * ARB_WINDOW, // Beyond the 5-minute window - expired
    };

    // Act - add the valid and expired arb
    act(() => {
      result.current.updateArbitrages(expiredArb);
      result.current.updateArbitrages(validArb);
    });

    // Assert - only the valid arbitrage should remain since the expired one is filtered out
    const keys = Object.keys(result.current.arbitrages);
    expect(keys).toHaveLength(1);
    expect(result.current.arbitrages[validArb.id]).toEqual(validArb);
  });
});

