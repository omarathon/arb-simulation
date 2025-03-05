import { handleMessage } from "../../contexts/WebSocketContext";
import { WebSocketMessage } from "../../types";

// Test the correct react hooks are called based on the received messages from the WebSocket

describe("handleMessage", () => {
  let updateOdds: jest.Mock;
  let updateOddsWithArbitrage: jest.Mock;
  let updateArbitrages: jest.Mock;
  let updateProfit: jest.Mock;
  let handlers: {
    updateOdds: jest.Mock;
    updateOddsWithArbitrage: jest.Mock;
    updateArbitrages: jest.Mock;
    updateProfit: jest.Mock;
  };

  beforeEach(() => {
    updateOdds = jest.fn();
    updateOddsWithArbitrage = jest.fn();
    updateArbitrages = jest.fn();
    updateProfit = jest.fn();
    handlers = { updateOdds, updateOddsWithArbitrage, updateArbitrages, updateProfit };
  });

  test("calls updateOdds hook for 'odds_update' message from web socket", () => {
    const message: WebSocketMessage = {
      message_type: "odds_update",
      contents: { odds: "some odds data" },
    };

    handleMessage(message, handlers);

    expect(updateOdds).toHaveBeenCalledWith(message.contents);
    expect(updateArbitrages).not.toHaveBeenCalled();
    expect(updateOddsWithArbitrage).not.toHaveBeenCalled();
    expect(updateProfit).not.toHaveBeenCalled();
  });

  test("calls updateArbitrages and updateOddsWithArbitrage hooks for 'arb_detection' messages from web socket", () => {
    const message: WebSocketMessage = {
      message_type: "arb_detection",
      contents: { arb: "arb detection data" },
    };

    handleMessage(message, handlers);

    expect(updateArbitrages).toHaveBeenCalledWith(message.contents);
    expect(updateOddsWithArbitrage).toHaveBeenCalledWith(message.contents);
    expect(updateOdds).not.toHaveBeenCalled();
    expect(updateProfit).not.toHaveBeenCalled();
  });

  test.each(["completed", "cancelled", "adjusted"])( // All these statuses are terminal for an arb and lead to a profit change
    "calls updateArbitrages, updateOddsWithArbitrage and updateProfit for 'arb_execution' message with '%s' status",
    (status) => {
      const message: WebSocketMessage = {
        message_type: "arb_execution",
        contents: {
          guaranteed_profit: 100,
          timestamp: 123456789,
          status,
        },
      };

      handleMessage(message, handlers);

      expect(updateArbitrages).toHaveBeenCalledWith(message.contents);
      expect(updateOddsWithArbitrage).toHaveBeenCalledWith(message.contents);
      expect(updateProfit).toHaveBeenCalledWith(100, 123456789);
      expect(updateOdds).not.toHaveBeenCalled();
    }
  );

  test("does not call updateProfit hook for 'arb_execution' message with 'detected' status from web socket ", () => {
    const message: WebSocketMessage = {
      message_type: "arb_execution",
      contents: {
        guaranteed_profit: 100,
        timestamp: 123456789,
        status: "detected", // not triggering profit update
      },
    };

    handleMessage(message, handlers);

    expect(updateArbitrages).toHaveBeenCalledWith(message.contents);
    expect(updateOddsWithArbitrage).toHaveBeenCalledWith(message.contents);
    expect(updateProfit).not.toHaveBeenCalled();
  });
});
