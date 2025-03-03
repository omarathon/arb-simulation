import React, { useContext } from "react";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography } from "@mui/material";
import { WebSocketContext } from "../contexts/WebSocketContext";
import { detectArbitrage } from "./ArbitrageDetector";

interface OddsData {
  event: string;
  match: string;
  bookmaker: string;
  odds: {
    home_win: number;
    away_win: number;
  } | null;
}

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
    <div style={{ padding: "20px", textAlign: "center" }}>
      <Typography variant="h4" gutterBottom>
        Live Odds Table
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Match</strong></TableCell>
              <TableCell><strong>Bookmaker</strong></TableCell>
              <TableCell><strong>Home Win</strong></TableCell>
              <TableCell><strong>Away Win</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.entries(groupedOdds).map(([match, matchOdds]: [string, OddsData[]], matchIndex) => {
              const hasArbitrage = detectArbitrage(matchOdds as OddsData[]);

              return (
                <React.Fragment key={match}>
                  {matchIndex > 0 && (
                    <TableRow>
                      <TableCell colSpan={5} style={{ height: "20px" }} />
                    </TableRow>
                  )}

                  {matchOdds.map((odd: OddsData, index: number) => {
                    const isClosed = odd.event === "odds_close";

                    return (
                      <TableRow
                        key={index}
                        style={{
                          backgroundColor: isClosed
                            ? "#ffcccc" // Light red if closed
                            : hasArbitrage
                            ? "#ffffcc" // Light yellow if arbitrage detected
                            : "#ccffcc", // Light green if open
                        }}
                      >
                        <TableCell>{index === 0 ? odd.match : ""}</TableCell>
                        <TableCell>{odd.bookmaker}</TableCell>
                        <TableCell>{odd.odds?.home_win ?? "-"}</TableCell>
                        <TableCell>{odd.odds?.away_win ?? "-"}</TableCell>
                      </TableRow>
                    );
                  })}
                </React.Fragment>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
};

export default OddsTable;
