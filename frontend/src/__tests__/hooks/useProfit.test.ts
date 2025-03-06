import { renderHook, act } from "@testing-library/react";
import { PROFIT_WINDOW, useProfit } from "../../hooks/useProfit";

describe("useProfit hook", () => {
  test("accumulates profit correctly with multiple updates", () => {
    // Arrange
    const { result } = renderHook(() => useProfit());
    const now = Date.now(); 

    // Act - add profits
    act(() => {
      result.current.updateProfit(50, now);
      result.current.updateProfit(30, now + 1000);
      result.current.updateProfit(-20, now + 2000);
    });

    // Assert - verify the three profits were added and accumulated
    expect(result.current.totalProfit).toBe(60); // 50 + 30 - 20 = 60
    expect(result.current.cumulativeProfits).toHaveLength(3);
    // The profit in the last entry should equal the accumulated total
    expect(result.current.cumulativeProfits[2].profit).toBe(60);
  });

  test("filters out expired profit entries", () => {
    const { result } = renderHook(() => useProfit());
    const now = Date.now();

    // Add an old entry that's expired
    act(() => {
      result.current.updateProfit(50, now - PROFIT_WINDOW - 1000);
      // Then add a new entry
      result.current.updateProfit(30, now);
    });

    // Assert - pnly the new entry should remain because the old one is filtered out, but accumulation should continue between windows
    expect(result.current.cumulativeProfits).toHaveLength(1); // Old profit is filtered of the cumulative profits array
    expect(result.current.cumulativeProfits[0].profit).toBe(80); // We accumulate forever, so 50 + 30 = 80
  });
});
