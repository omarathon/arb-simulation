import React, { useContext, useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, Title, Tooltip, Legend, LinearScale, PointElement, LineElement, CategoryScale } from "chart.js";
import { WebSocketContext } from "../contexts/WebSocketContext";
import { Paper, Typography, TextField } from "@mui/material";

ChartJS.register(Title, Tooltip, Legend, LinearScale, PointElement, LineElement, CategoryScale);

const CumulativeProfitChart: React.FC = () => {
  const { cumulativeProfits } = useContext(WebSocketContext) ?? { cumulativeProfits: [] };
  const [timeWindowSeconds, setTimeWindowSeconds] = useState(30);

  // Generate Data for Time Window Chart
  const getWindowedChartData = () => {
    const currentTime = Date.now();
    const filteredProfits = cumulativeProfits.filter(entry => currentTime - entry.timestamp <= timeWindowSeconds * 1000);
    
    return {
      labels: filteredProfits.map(entry => new Date(entry.timestamp).toLocaleTimeString()),
      datasets: [
        {
          label: "Profit (Windowed)",
          data: filteredProfits.map(entry => entry.profit),
          fill: false,
          borderColor: "#008080", // Smarkets color
          stepped: true
        },
      ],
    };
  };

  // Generate Data for Full Profit Chart
  const getFullChartData = () => {
    return {
      labels: cumulativeProfits.map(entry => new Date(entry.timestamp).toLocaleTimeString()),
      datasets: [
        {
          label: "Total Cumulative Profit",
          data: cumulativeProfits.map(entry => entry.profit),
          fill: false,
          borderColor: "#005f5f", // Darker for contrast
          stepped: true
        },
      ],
    };
  };

  const [windowedChartData, setWindowedChartData] = useState(getWindowedChartData);
  const [fullChartData, setFullChartData] = useState(getFullChartData);

  useEffect(() => {
    setWindowedChartData(getWindowedChartData());
    setFullChartData(getFullChartData());
  }, [cumulativeProfits, timeWindowSeconds]);

  return (
    <Paper elevation={3} sx={{ textAlign: "center", height:"100%", width:"100%" }}>
      <Typography variant="h5" sx={{ padding: "20px" }}>
        Profit Overview
      </Typography>

      {/* Time Window Input */}
      <TextField
        label="Time Window (s)"
        type="number"
        variant="outlined"
        size="small"
        value={timeWindowSeconds}
        onChange={(e) => setTimeWindowSeconds(Math.max(1, parseInt(e.target.value) || 1))}
        sx={{ marginBottom: "20px", width: "140px" }}
      />

      {/* Windowed Profit Chart */}
      <div style={{ width: "98%", height: "300px", paddingBottom: "50px", paddingLeft: "10px" }}>
        <Typography variant="h6" sx={{ marginBottom: "5px" }}>
          Profit in the Last {timeWindowSeconds} Seconds
        </Typography>
        <Line
          data={windowedChartData}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 0 },
            scales: {
              x: {
                ticks: {
                  maxRotation: 45,
                  minRotation: 45,
                  font: { size: 12 },
                },
              },
              y: {
                ticks: {
                  font: { size: 12 },
                },
              },
            },
          }}
        />
      </div>

      {/* Overall Cumulative Profit Chart */}
      <div style={{ width: "98%", height: "300px", paddingBottom: "50px", paddingLeft: "10px" }}>
        <Typography variant="h6" sx={{ marginBottom: "5px" }}>
          Total Cumulative Profit
        </Typography>
        <Line
          data={fullChartData}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 0 },
            scales: {
              x: {
                ticks: {
                  maxRotation: 45,
                  minRotation: 45,
                  font: { size: 12 },
                },
              },
              y: {
                ticks: {
                  font: { size: 12 },
                },
              },
            },
          }}
        />
      </div>
    </Paper>
  );
};

export default CumulativeProfitChart;
