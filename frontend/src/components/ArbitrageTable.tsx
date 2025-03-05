import React, { useContext } from "react";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography } from "@mui/material";
import { WebSocketContext } from "../contexts/WebSocketContext";
import { ArbMessage } from "../types";

// Status formatting helpers
const niceStatuses: Record<ArbMessage["status"], string> = {
  detected: "Detected",
  completed: "Completed",
  adjusted: "Adjusted",
  cancelled: "Cancelled",
};

const statusColors: Record<ArbMessage["status"], string> = {
  detected: "#fff6b3", // Yellow
  completed: "#c8f7c5", // Green
  adjusted: "#ffcc80", // Orange
  cancelled: "#f7b2b2", // Red
};

// Common table styling for consistency
const tableStyles = {
  tableHeader: {
    fontWeight: "bold",
    textAlign: "center",
    backgroundColor: "#007f7f", // Smarkets-themed color
    color: "white",
  },
  tableCell: {
    textAlign: "center",
    fontSize: "0.95rem",
  },
  rightAlignCell: {
    textAlign: "right",
    fontSize: "0.95rem",
  },
};

const ArbitrageTable: React.FC = () => {
  const context = useContext(WebSocketContext);

  if (!context) {
    return <Typography>Error: WebSocket context is unavailable.</Typography>;
  }

  const { arbitrages } = context;
  const arbList: ArbMessage[] = Object.values(arbitrages)
    .sort((a, b) => b.timestamp - a.timestamp)
    .slice(0, 10); // Show last 10 arbitrages

  return (
    <TableContainer component={Paper} sx={{height:"100%", width:"100%"}}>
      <Typography variant="h5" sx={{ paddingTop: "20px", textAlign: "center"}}>
        Arbitrage Opportunities (Last 10)
      </Typography>
      <Table stickyHeader sx={{ padding: "20px" }}>
        <TableHead>
          <TableRow>
            <TableCell sx={tableStyles.tableHeader}>Status</TableCell>
            <TableCell sx={tableStyles.tableHeader}>Match</TableCell>
            <TableCell sx={tableStyles.tableHeader}>Home Bookmaker</TableCell>
            <TableCell sx={tableStyles.tableHeader}>Away Bookmaker</TableCell>
            <TableCell sx={tableStyles.tableHeader}>Home Odds</TableCell>
            <TableCell sx={tableStyles.tableHeader}>Away Odds</TableCell>
            <TableCell sx={tableStyles.tableHeader}>Home Stake</TableCell>
            <TableCell sx={tableStyles.tableHeader}>Away Stake</TableCell>
            <TableCell sx={tableStyles.tableHeader}>Profit</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {arbList.map((arb) => (
            <TableRow key={arb.id} sx={{ backgroundColor: statusColors[arb.status] }}>
              <TableCell sx={tableStyles.tableCell}>{niceStatuses[arb.status]}</TableCell>
              <TableCell sx={tableStyles.tableCell}>{arb.match}</TableCell>
              <TableCell sx={tableStyles.tableCell}>{arb.home_win_bookmaker}</TableCell>
              <TableCell sx={tableStyles.tableCell}>{arb.away_win_bookmaker}</TableCell>
              <TableCell sx={tableStyles.tableCell}>{arb.home_win_odds ?? "-"}</TableCell>
              <TableCell sx={tableStyles.tableCell}>{arb.away_win_odds ?? "-"}</TableCell>
              <TableCell sx={tableStyles.rightAlignCell}>${arb.home_win_stake.toFixed(2)}</TableCell>
              <TableCell sx={tableStyles.rightAlignCell}>${arb.away_win_stake.toFixed(2)}</TableCell>
              <TableCell sx={tableStyles.rightAlignCell}>${arb.guaranteed_profit.toFixed(2)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default ArbitrageTable;
