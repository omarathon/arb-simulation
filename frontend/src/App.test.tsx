import React from "react";
import { screen } from "@testing-library/react";
import App from "./App";
import { renderWithWebSocket } from "./setupTests";

test("renders Live Odds Table", () => {
  renderWithWebSocket(<App />);
  expect(screen.getByText(/Live Odds Table/i)).toBeInTheDocument();
});
