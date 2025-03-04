import React, { useContext, useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, Title, Tooltip, Legend, LinearScale, PointElement, LineElement, CategoryScale } from "chart.js";
import { WebSocketContext } from "../contexts/WebSocketContext";

// Register necessary chart components
ChartJS.register(Title, Tooltip, Legend, LinearScale, PointElement, LineElement, CategoryScale);

const CumulativeProfitChart: React.FC = () => {
  const { cumulativeProfits } = useContext(WebSocketContext) ?? { cumulativeProfits: [] };
  const [timeWindowSeconds, setTimeWindowSeconds] = useState(30);

  // Update chart data
  const getChartData = () => {
    const currentTime = Date.now();
    const filteredProfits = cumulativeProfits.filter(entry => currentTime - entry.timestamp <= timeWindowSeconds * 1000);
    
    return {
      labels: filteredProfits.map(entry => new Date(entry.timestamp).toLocaleTimeString()),
      datasets: [
        {
          label: "Cumulative Profit",
          data: filteredProfits.map(entry => entry.profit),
          fill: false,
          borderColor: "rgb(0, 0, 0)",
          tension: 0.1,
          stepped: true, // Ensures "step-like" jumps for discrete profit changes
        },
      ],
    };
  };

  const [chartData, setChartData] = useState(getChartData);

  useEffect(() => {
    setChartData(getChartData());
  }, [cumulativeProfits, timeWindowSeconds]);

  return (
    <div style={{ width: "80%", maxWidth: "800px", margin: "auto", textAlign: "center" }}>
      <h2>Live Cumulative Profit Chart</h2>
      
      <label>
        Time Window (seconds): 
        <input
          type="number"
          value={timeWindowSeconds}
          onChange={(e) => setTimeWindowSeconds(Math.max(1, parseInt(e.target.value) || 1))}
          style={{ marginLeft: "10px", width: "60px" }}
        />
      </label>

      <div style={{ width: "100%", height: "400px", marginTop: "10px" }}>
        <Line data={chartData} options={{ animation: { duration: 0 }, responsive: true, maintainAspectRatio: false }} />
      </div>
    </div>
  );
};

export default CumulativeProfitChart;
