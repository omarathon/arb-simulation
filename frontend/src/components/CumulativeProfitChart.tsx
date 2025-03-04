import React, { useContext, useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { WebSocketContext } from "../contexts/WebSocketContext";

const PROFIT_WINDOW = 0.5 * 60 * 1000; // 5-minute window
const UPDATE_INTERVAL = 50; // Fill gaps every 50ms

const CumulativeProfitChart: React.FC = () => {
  const context = useContext(WebSocketContext);
  const cumulativeProfits = context?.cumulativeProfits ?? [];
  const totalProfit = context?.totalProfit ?? 0;

  const [smoothedData, setSmoothedData] = useState<{ timestamp: number; profit: number }[]>([]);
  const [lastUpdate, setLastUpdate] = useState(Date.now());

  // Function to interpolate between two points
  const interpolateProfit = (prev: { timestamp: number; profit: number }, next: { timestamp: number; profit: number }, targetTime: number) => {
    if (next.timestamp === prev.timestamp) return prev.profit;
    const ratio = (targetTime - prev.timestamp) / (next.timestamp - prev.timestamp);
    return prev.profit + ratio * (next.profit - prev.profit);
  };

  useEffect(() => {
    const interval = setInterval(() => {
      setSmoothedData((prevData) => {
        const now = Date.now();
        const lastProfit = prevData.length ? prevData[prevData.length - 1].profit : 0;

        return [...prevData, { timestamp: now, profit: lastProfit }];
      });
      setLastUpdate(Date.now());
    }, UPDATE_INTERVAL);

    return () => clearInterval(interval);
  }, []);

  // **🔥 Main logic: Transform cumulativeProfits into a fully interpolated dataset**
  useEffect(() => {
    if (cumulativeProfits.length === 0) return;

    const now = Date.now();

    // ✅ Step 1: Filter only the last 5 minutes of profit data
    const filteredProfits = cumulativeProfits.filter((entry) => now - entry.timestamp <= PROFIT_WINDOW);

    let interpolatedData: { timestamp: number; profit: number }[] = [];

    // ✅ Step 2: Fill gaps inside the dataset via interpolation
    for (let i = 0; i < filteredProfits.length - 1; i++) {
      const current = filteredProfits[i];
      const next = filteredProfits[i + 1];

      // Insert intermediate points every `UPDATE_INTERVAL`
      for (let t = current.timestamp; t <= next.timestamp; t += UPDATE_INTERVAL) {
        interpolatedData.push({
          timestamp: t,
          profit: interpolateProfit(current, next, t),
        });
      }
    }

    // ✅ Step 3: Extend the line to the current time
    if (filteredProfits.length > 0) {
      const lastPoint = filteredProfits[filteredProfits.length - 1];
      for (let t = lastPoint.timestamp; t <= now; t += UPDATE_INTERVAL) {
        interpolatedData.push({ timestamp: t, profit: lastPoint.profit });
      }
    }

    setSmoothedData(interpolatedData);
  }, [cumulativeProfits, lastUpdate]); // Runs when `cumulativeProfits` changes

  return (
    <div style={{ width: "100%", height: 350, padding: "20px", textAlign: "center" }}>
      <h2>
        Current Total Profit:{" "}
        <span style={{ color: totalProfit >= 0 ? "green" : "red" }}>
          ${totalProfit.toFixed(2)}
        </span>
      </h2>
      <h3>Last 5 Minutes of Cumulative Profit</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={smoothedData}>
          <XAxis
            dataKey="timestamp"
            tickFormatter={(time: number) => new Date(time).toISOString().slice(11, 19)} // ✅ Show HH:mm:ss.SSS
          />
          <YAxis />
          <Tooltip labelFormatter={(time: number) => new Date(time).toISOString().slice(11, 23)} />
          <Line type="monotone" dataKey="profit" stroke="#4CAF50" strokeWidth={2} dot={false} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CumulativeProfitChart;
