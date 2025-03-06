import React from "react";
import { Grid, Paper, Typography } from "@mui/material";
import OddsTable from "./OddsTable";
import ArbitrageTable from "./ArbitrageTable";
import CumulativeProfitChart from "./CumulativeProfitChart";
import "./styles/DashboardLayout.css"; // Import custom styles

const DashboardLayout: React.FC = () => {
  return (
    <div>
        {/* Title Bar */}
        <div className="title-bar">
            <Typography variant="h4" className="title-text">
            💲 Arbitrage Simulation 💲
            </Typography>
        </div>

      {/* Main Dashboard Content */}
    <Grid 
        container 
        spacing={1} 
        sx={{
            width: "100%",
            maxWidth: "1700px", 
            margin: "auto", 
            display: "flex", 
            flexDirection: { xs: "column", md: "row" } // ✅ Ensures correct layout
        }}
    >
        <Grid item xs={12} md={6} sx={{ padding: "10px"}}>
            <Paper elevation={3} sx={{ height: "100%" }}>
                <OddsTable />
            </Paper>
        </Grid>
        <Grid item xs={12} md={6} sx={{ padding: "10px"}}>
            <Paper elevation={3} sx={{ height: "100%" }}>
                <CumulativeProfitChart />
            </Paper>
        </Grid>
    </Grid>

    {/* Bottom Section: Arbitrage Table (Always Below, Full Width) */}
    <Grid container spacing={1} sx={{ width: "100%",     maxWidth: "1700px", margin: "auto" }}>
        <Grid item xs={12} sx={{ padding: "10px"}}>
            <Paper elevation={3} sx={{ height: "100%" }}>
                <ArbitrageTable />
            </Paper>
        </Grid>
    </Grid>
</div>


  );
};

export default DashboardLayout;
