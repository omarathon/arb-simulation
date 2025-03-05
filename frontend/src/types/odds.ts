import { ArbStatus } from "./arb";

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
    timestamp: number;
}

export const isValidOddArbStatus = (status: ArbStatus): status is Exclude<OddArbStatus, null> => {
    return status === "detected" || status === "completed";
};