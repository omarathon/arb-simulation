import React, { useContext, useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, Title, Tooltip, Legend, LinearScale, PointElement, LineElement, CategoryScale } from "chart.js";
import { WebSocketContext } from "../contexts/WebSocketContext";
import { Paper, Typography, TextField } from "@mui/material";
import "./styles/Graphs.css"; // Import the new graph styles

ChartJS.register(Title, Tooltip, Legend, LinearScale, PointElement, LineElement, CategoryScale);

const CumulativeProfitChart: React.FC = () => {
  const { cumulativeProfits } = useContext(WebSocketContext) ?? { cumulativeProfits: [] };
  const [timeWindowSeconds, setTimeWindowSeconds] = useState(30);

  // Generate data for filtered profits graph
  const getWindowedChartData = () => {
    const currentTime = Date.now();
    // Filter profits into window
    const filteredProfits = cumulativeProfits.filter(entry => currentTime - entry.timestamp <= timeWindowSeconds * 1000);
    
    return {
      labels: filteredProfits.map(entry => new Date(entry.timestamp).toLocaleTimeString()),
      datasets: [
        {
          label: "Profit (Windowed)",
          data: filteredProfits.map(entry => entry.profit),
          fill: false,
          borderColor: "#00c853", // Bright green
          stepped: true
        },
      ],
    };
  };

  // Generate data for full profits graph
  const getFullChartData = () => {
    return {
      labels: cumulativeProfits.map(entry => new Date(entry.timestamp).toLocaleTimeString()),
      datasets: [
        {
          label: "Total Cumulative Profit",
          data: cumulativeProfits.map(entry => entry.profit),
          fill: false,
          borderColor: "#00c853", // Bright green
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
    <Paper elevation={3} className="graph-container" sx={{ backgroundColor: "#121212" }}>
      <Typography variant="h5" component="h2" className="graph-title">
        Profit Overview
      </Typography>

      <div className="graph-header">
        <Typography variant="h6" className="graph-label" style={{ color: "#ffffff", marginTop: "7px" }}>
          Last{" "}
        </Typography>
        <TextField
          type="number"
          variant="outlined"
          size="small"
          value={timeWindowSeconds}
          onChange={(e) => setTimeWindowSeconds(Math.max(2, parseInt(e.target.value) || 1))}
          inputProps={{
            style: { textAlign: "center", fontWeight: "bold", color: "#ffffff" },
          }}
          sx={{
            width: "100px",
            marginLeft: "15px",
            marginRight: "12px",
            marginBottom: "0px",
            backgroundColor: "#424242", // Darker background inside input box
            borderRadius: "0px", // Remove curvature curvature from input box as well
          }}
        />
        <Typography variant="h6" className="graph-label" style={{ color: "#ffffff", marginTop: "7px" }}>
          Seconds
        </Typography>
      </div>


      {/* Windowed profit chart */}
      <div className="chart-wrapper">
        <Line
          data={windowedChartData}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 0 },
            plugins: {
              legend: {
                display: false,
              },
            },
            scales: {
              x: {
                ticks: {
                  maxRotation: 45,
                  minRotation: 45,
                  font: { size: 12 },
                  color: "#ffffff",
                },
              },
              y: {
                ticks: {
                  font: { size: 12 },
                  color: "#ffffff",
                },
              },
            },
          }}
        />
      </div>

      <div className="graph-header">
        <Typography variant="h6" className="graph-label" style={{ color: "#ffffff", marginTop: "7px" }}>
           All Time
        </Typography>
      </div>

      {/* Overall cumulative profit chart */}
      <div className="chart-wrapper">
        <Line
          data={fullChartData}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 0 },
            plugins: {
              legend: {
                display: false,
              },
            },
            scales: {
              x: {
                ticks: {
                  maxRotation: 45,
                  minRotation: 45,
                  font: { size: 12 },
                  color: "#ffffff",
                },
              },
              y: {
                ticks: {
                  font: { size: 12 },
                  color: "#ffffff",
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
