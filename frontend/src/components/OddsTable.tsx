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
import "./styles/Tables.css";
import { OddsData } from "../types";

const OddsTable: React.FC = () => {
  const context = useContext(WebSocketContext);

  if (!context) {
    return <Typography>Error: WebSocket context is unavailable.</Typography>;
  }

  const { odds } = context;

  // Group odds by match
  const groupedOdds = odds.reduce<Record<string, OddsData[]>>((acc, odd) => {
    if (!acc[odd.match]) {
      acc[odd.match] = [];
    }
    acc[odd.match].push(odd);
    return acc;
  }, {});

  return (
    <TableContainer component={Paper} className="table-container odds-table">
      <Typography variant="h5" component="h2" className="table-title">
        Live Odds
      </Typography>

      <Table stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell className="table-header">Match</TableCell>
            <TableCell className="table-header">Bookmaker</TableCell>
            <TableCell className="table-header">Home Win</TableCell>
            <TableCell className="table-header">Away Win</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {Object.entries(groupedOdds).map(([match, matchOdds], matchIndex) => (
            <React.Fragment key={match}>
              {matchIndex > 0 && (
                <TableRow>
                  <TableCell colSpan={4} className="table-spacing" /> {/* Spacing between each match */}
                </TableRow>
              )}
              {matchOdds.map((odd, index) => {
                return (
                  <TableRow 
                    key={index} 
                    className={`table-row ${odd.odds === null ? "cancelled" : odd.arb_status || "neutral"}`}
                  >
                    <TableCell className="table-cell">{index === 0 ? odd.match : ""}</TableCell>
                    <TableCell className="table-cell">{odd.bookmaker}</TableCell>
                    <TableCell className="table-cell right-align">{odd.odds?.home_win ?? "-"}</TableCell>
                    <TableCell className="table-cell right-align">{odd.odds?.away_win ?? "-"}</TableCell>
                  </TableRow>
                );
              })}
            </React.Fragment>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default OddsTable;
