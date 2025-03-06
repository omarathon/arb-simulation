import React, { useContext } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
} from "@mui/material";
import { WebSocketContext } from "../contexts/WebSocketContext";
import { ArbMessage } from "../types";
import "./styles/Tables.css";

const niceStatuses: Record<ArbMessage["status"], string> = {
  detected: "Detected",
  completed: "Completed",
  adjusted: "Adjusted",
  cancelled: "Cancelled",
};

const NUM_ARBS = 10; // How many arbs to show

const ArbitrageTable: React.FC = () => {
  const context = useContext(WebSocketContext);

  if (!context) {
    return <Typography>Error: WebSocket context is unavailable.</Typography>;
  }

  const { arbitrages } = context;
  const arbList: ArbMessage[] = Object.values(arbitrages)
    .sort((a, b) => b.timestamp - a.timestamp)
    .slice(0, NUM_ARBS);

  return (
    <TableContainer component={Paper} className="table-container arbitrage-table">
      <Typography variant="h5" component="h2" className="table-title">
        Live Arbitrages
      </Typography>

      <Table stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell className="table-header">Status</TableCell>
            <TableCell className="table-header">Match</TableCell>
            <TableCell className="table-header">Home Bookmaker</TableCell>
            <TableCell className="table-header">Away Bookmaker</TableCell>
            <TableCell className="table-header">Home Odds</TableCell>
            <TableCell className="table-header">Away Odds</TableCell>
            <TableCell className="table-header">Home Stake</TableCell>
            <TableCell className="table-header">Away Stake</TableCell>
            <TableCell className="table-header">Profit</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {arbList.map((arb) => (
            <TableRow key={arb.id} className={`table-row ${arb.status}`}>
              <TableCell className="table-cell">{niceStatuses[arb.status]}</TableCell>
              <TableCell className="table-cell">{arb.match}</TableCell>
              <TableCell className="table-cell">{arb.home_win_bookmaker}</TableCell>
              <TableCell className="table-cell">{arb.away_win_bookmaker}</TableCell>
              <TableCell className="table-cell">{arb.home_win_odds ?? "-"}</TableCell>
              <TableCell className="table-cell">{arb.away_win_odds ?? "-"}</TableCell>
              <TableCell className="table-cell right-align">£{arb.home_win_stake.toFixed(2)}</TableCell>
              <TableCell className="table-cell right-align">£{arb.away_win_stake.toFixed(2)}</TableCell>
              <TableCell className="table-cell right-align">£{arb.guaranteed_profit.toFixed(2)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default ArbitrageTable;
