/*
    Web socket
*/

export type MessageType = "odds_update" | "arb_detection" | "arb_execution";

export interface WebSocketMessage {
  message_type: MessageType;
  contents: any;
}

/*
    Odds
*/

export type OddArbStatus = "detected" | "completed" | null; // Detected => arb detected with this precise odd. Completed => arb completed with this exact odd.
export interface OddsData {
    event: "odds_update" | "odds_close";
    match: string;
    bookmaker: string;
    odds: {
        home_win: number;
        away_win: number;
    } | null;
    arb_status: OddArbStatus;
}

/*
    Arb
*/

export type ArbStatus = "detected" | "completed" | "cancelled" | "adjusted";
export interface ArbMessage {
    id: string;
    match: string;
    home_win_bookmaker: string;
    away_win_bookmaker: string;
    home_win_odds?: number;
    away_win_odds?: number;
    home_win_stake: number;
    away_win_stake: number;
    guaranteed_profit: number;
    status: ArbStatus;
    timestamp: number;
}

export const isValidOddArbStatus = (status: ArbStatus): status is Exclude<OddArbStatus, null> => {
    return status === "detected" || status === "completed";
};
  