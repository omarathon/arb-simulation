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