def calculate_guaranteed_payout(S_H: float, S_A: float, O_H: float, O_A: float) -> float:
    "Calculates the guarantees payout if betting for home with stake S_H and odds O_H, and away with stake S_A and odds O_A."
    return min(S_H * O_H, S_A * O_A)