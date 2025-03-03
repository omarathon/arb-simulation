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
  event: string;
  match: string;
  bookmaker: string;
  odds: {
    home_win: number;
    away_win: number;
  } | null;
}

const SOCKET_URL = "ws://localhost:8002/ws"; // Replace with actual WebSocket URL

const App: React.FC = () => {
  const [odds, setOdds] = useState<OddsData[]>([]);

  useEffect(() => {
    const ws = new WebSocket(SOCKET_URL);

    ws.onmessage = (event) => {
      let data: OddsData;
      try {
        data = JSON.parse(event.data);
      }
      catch (error) {
        console.error("Error parsing JSON:", error);
        return;
      }

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

  const detectArbitrage = (matchOdds: OddsData[]): boolean => {
    let minArbValue = Infinity;
  
    for (let i = 0; i < matchOdds.length; i++) {
      for (let j = 0; j < matchOdds.length; j++) {
        if (i === j) continue; // Avoid same bookmaker
  
        const homeWin = matchOdds[i].odds?.home_win;
        const awayWin = matchOdds[j].odds?.away_win;
  
        if (homeWin && awayWin) {
          const arbitrageValue = (1 / homeWin) + (1 / awayWin);
          minArbValue = Math.min(minArbValue, arbitrageValue);
        }
      }
    }
  
    return minArbValue < 1;
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
                    const isClosed = odd.event == "odds_close"

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

export default App;
