import React from "react";
import { WebSocketProvider } from "./contexts/WebSocketContext";
import OddsTable from "./components/OddsTable";
import ArbitrageTable from "./components/ArbitrageTable";
import CumulativeProfitChart from "./components/CumulativeProfitChart"; // ✅ Changed to Cumulative Profit

const App: React.FC = () => {
  return (
    <WebSocketProvider>
      {/* ✅ Top Section: Live Odds (Left) | Cumulative Profit (Right) */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "flex-start",
          gap: "20px",
          padding: "10px",
          maxWidth: "1200px",
          margin: "0 auto",
        }}
      >
        {/* ✅ Live Odds Table (Left) */}
        <div style={{ flex: 1, minWidth: "48%" }}>
          <OddsTable />
        </div>

        {/* ✅ Cumulative Profit Chart (Right) */}
        <div style={{ flex: 1, minWidth: "48%" }}>
          <CumulativeProfitChart />
        </div>
      </div>

      {/* ✅ Full-Width Arbitrage Opportunities Table (Below) */}
      <div
        style={{
          width: "100%",
          maxWidth: "1200px",
          margin: "0 auto",
          padding: "20px 10px",
        }}
      >
        <ArbitrageTable />
      </div>
    </WebSocketProvider>
  );
};

export default App;
