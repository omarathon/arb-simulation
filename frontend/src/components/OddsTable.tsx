import React, { useContext } from "react";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography } from "@mui/material";
import { WebSocketContext } from "../contexts/WebSocketContext";

interface OddsData {
  event: string;
  match: string;
  bookmaker: string;
  odds: {
    home_win: number;
    away_win: number;
  } | null;
  arb_status?: "detected" | "completed" | null;
}

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
  oddsCell: {
    textAlign: "right",
    fontSize: "0.95rem",
  },
};

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
    <TableContainer component={Paper} sx={{height:"100%", width:"100%"}}>
      <Typography variant="h5" sx={{ paddingTop: "20px", textAlign: "center" }}>
        Live Odds Table
      </Typography>
      <Table stickyHeader sx={{padding: "20px"}}>
        <TableHead>
          <TableRow>
            <TableCell sx={tableStyles.tableHeader}>Match</TableCell>
            <TableCell sx={tableStyles.tableHeader}>Bookmaker</TableCell>
            <TableCell sx={tableStyles.tableHeader}>Home Win</TableCell>
            <TableCell sx={tableStyles.tableHeader}>Away Win</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {Object.entries(groupedOdds).map(([match, matchOdds], matchIndex) => (
            <React.Fragment key={match}>
              {matchIndex > 0 && (
                <TableRow>
                  <TableCell colSpan={4} sx={{ height: "20px" }} />
                </TableRow>
              )}
              {matchOdds.map((odd, index) => {
                const isClosed = odd.event === "odds_close";

                return (
                  <TableRow
                    key={index}
                    sx={{
                      backgroundColor: isClosed
                        ? "#ffcccc" // Red if closed
                        : odd.arb_status === "completed"
                        ? "#ccffcc" // Green if executed
                        : odd.arb_status === "detected"
                        ? "#ffffcc" // Yellow if detected
                        : "#ffffff", // White otherwise
                    }}
                  >
                    <TableCell sx={tableStyles.tableCell}>{index === 0 ? odd.match : ""}</TableCell>
                    <TableCell sx={tableStyles.tableCell}>{odd.bookmaker}</TableCell>
                    <TableCell sx={tableStyles.oddsCell}>{odd.odds?.home_win ?? "-"}</TableCell>
                    <TableCell sx={tableStyles.oddsCell}>{odd.odds?.away_win ?? "-"}</TableCell>
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
