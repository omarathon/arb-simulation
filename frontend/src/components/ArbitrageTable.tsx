import React, { useContext } from "react";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography } from "@mui/material";
import { WebSocketContext } from "../contexts/WebSocketContext";

interface ArbMessage {
  id: string;
  match: string;
  home_win_bookmaker: string;
  away_win_bookmaker: string;
  home_win_odds?: number;
  away_win_odds?: number;
  home_win_stake: number;
  away_win_stake: number;
  guaranteed_payout: number;
  profit: number; // ✅ NEW
  status: "detected" | "completed" | "cancelled" | "adjusted";
  timestamp: number;
}

const statusColors: Record<ArbMessage["status"], string> = {
  detected: "#fff6b3", // Yellow
  completed: "#c8f7c5", // Green
  adjusted: "#ffcc80", // Orange
  cancelled: "#f7b2b2", // Red
};

const ArbitrageTable: React.FC = () => {
  const context = useContext(WebSocketContext);

  if (!context) {
    return <Typography>Error: WebSocket context is unavailable.</Typography>;
  }

  const { arbitrages } = context;
  const arbList = Object.values(arbitrages)
    .sort((a, b) => b.timestamp - a.timestamp)
    .slice(0, 10); // Limit to last 10 arbitrages

  return (
    <div style={{ padding: "20px", textAlign: "center" }}>
      <Typography variant="h5" gutterBottom>
        Arbitrage Opportunities (Last 10)
      </Typography>
      <TableContainer component={Paper} style={{ maxHeight: "auto", overflowY: "auto" }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell><strong>Match</strong></TableCell>
              <TableCell><strong>Home Bookmaker</strong></TableCell>
              <TableCell><strong>Away Bookmaker</strong></TableCell>
              <TableCell><strong>Home Odds</strong></TableCell>
              <TableCell><strong>Away Odds</strong></TableCell>
              <TableCell><strong>Home Stake</strong></TableCell>
              <TableCell><strong>Away Stake</strong></TableCell>
              <TableCell><strong>Payout</strong></TableCell>
              <TableCell><strong>Profit</strong></TableCell> {/* ✅ NEW COLUMN */}
              <TableCell><strong>Status</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {arbList.map((arb) => (
              <TableRow key={arb.id} style={{ backgroundColor: statusColors[arb.status] }}>
                <TableCell>{arb.match}</TableCell>
                <TableCell>{arb.home_win_bookmaker}</TableCell>
                <TableCell>{arb.away_win_bookmaker}</TableCell>
                <TableCell>{arb.home_win_odds ?? "-"}</TableCell>
                <TableCell>{arb.away_win_odds ?? "-"}</TableCell>
                <TableCell>${arb.home_win_stake.toFixed(2)}</TableCell>
                <TableCell>${arb.away_win_stake.toFixed(2)}</TableCell>
                <TableCell>${arb.guaranteed_payout.toFixed(2)}</TableCell>
                <TableCell>${arb.profit.toFixed(2)}</TableCell> {/* ✅ SHOW PROFIT */}
                <TableCell>{arb.status.toUpperCase()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
};

export default ArbitrageTable;
