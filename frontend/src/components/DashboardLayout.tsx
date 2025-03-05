import React from "react";
import { Grid, Paper } from "@mui/material";
import OddsTable from "./OddsTable";
import ArbitrageTable from "./ArbitrageTable";
import CumulativeProfitChart from "./CumulativeProfitChart";

const DashboardLayout: React.FC = () => {
  return (
    <div>
    {/* Top Section: Odds Table & Profit Chart (Side-by-Side on Large Screens, Stacked on Small Screens) */}
    <Grid 
        container 
        spacing={1} 
        sx={{ 
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
    <Grid container spacing={1} sx={{ maxWidth: "1700px", margin: "auto" }}>
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
