import React, { useEffect, useState } from "react";
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

interface OddsData {
  match: string;
  bookmaker: string;
  odds: {
    home_win: number | null;
    draw: number | null;
    away_win: number | null;
  };
}

const SOCKET_URL = "ws://localhost:8001/ws"; // Replace with actual WebSocket URL

const App: React.FC = () => {
  const [odds, setOdds] = useState<OddsData[]>([]);

  useEffect(() => {
    const ws = new WebSocket(SOCKET_URL);

    ws.onmessage = (event) => {
      const data: OddsData = JSON.parse(event.data);

      setOdds((prevOdds) => {
        const existingIndex = prevOdds.findIndex(
          (o) => o.match === data.match && o.bookmaker === data.bookmaker
        );

        if (existingIndex !== -1) {
          // Update existing row
          const updatedOdds = [...prevOdds];
          updatedOdds[existingIndex] = data;
          return updatedOdds;
        } else {
          // Add new row
          return [...prevOdds, data];
        }
      });
    };

    ws.onopen = () => console.log("Connected to WebSocket");
    ws.onerror = (error) => console.error("WebSocket Error:", error);
    ws.onclose = () => console.log("WebSocket Disconnected");

    return () => {
      ws.close();
    };
  }, []);

  // Group by match
  const groupedOdds = odds.reduce((acc, odd) => {
    if (!acc[odd.match]) {
      acc[odd.match] = [];
    }
    acc[odd.match].push(odd);
    return acc;
  }, {} as Record<string, OddsData[]>);

  // Function to detect arbitrage opportunities
  const detectArbitrage = (matchOdds: OddsData[]): boolean => {
    let bestHomeWin = 0;
    let bestDraw = 0;
    let bestAwayWin = 0;

    matchOdds.forEach((odd) => {
      if (odd.odds.home_win) bestHomeWin = Math.max(bestHomeWin, odd.odds.home_win);
      if (odd.odds.draw) bestDraw = Math.max(bestDraw, odd.odds.draw);
      if (odd.odds.away_win) bestAwayWin = Math.max(bestAwayWin, odd.odds.away_win);
    });

    if (bestHomeWin > 0 && bestDraw > 0 && bestAwayWin > 0) {
      const arbitrageValue = (1 / bestHomeWin) + (1 / bestDraw) + (1 / bestAwayWin);
      return arbitrageValue < 1; // Arbitrage exists if sum < 1
    }

    return false;
  };

  return (
    <div style={{ padding: "20px", textAlign: "center" }}>
      <Typography variant="h4" gutterBottom>
        Live Odds Table
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                <strong>Match</strong>
              </TableCell>
              <TableCell>
                <strong>Bookmaker</strong>
              </TableCell>
              <TableCell>
                <strong>Home Win</strong>
              </TableCell>
              <TableCell>
                <strong>Draw</strong>
              </TableCell>
              <TableCell>
                <strong>Away Win</strong>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.entries(groupedOdds).map(([match, matchOdds], matchIndex) => {
              const hasArbitrage = detectArbitrage(matchOdds);

              return (
                <React.Fragment key={match}>
                  {/* Add spacing between matches */}
                  {matchIndex > 0 && (
                    <TableRow>
                      <TableCell colSpan={5} style={{ height: "20px" }} />
                    </TableRow>
                  )}

                  {matchOdds.map((odd, index) => {
                    // Check if the odds are closed (all values inside `odds` are null)
                    const isClosed =
                      odd.odds.home_win === null &&
                      odd.odds.draw === null &&
                      odd.odds.away_win === null;

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
                        <TableCell>{odd.odds.home_win ?? "-"}</TableCell>
                        <TableCell>{odd.odds.draw ?? "-"}</TableCell>
                        <TableCell>{odd.odds.away_win ?? "-"}</TableCell>
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

export default App;
