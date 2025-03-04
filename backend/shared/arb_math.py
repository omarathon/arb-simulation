from typing import Optional

def calculate_guaranteed_payout(S_H: float, S_A: float, O_H: Optional[float], O_A: Optional[float]) -> float:
    """
    Calculates the guaranteed payout, considering possible cancellations.
    If one side is cancelled, it assumes the worst-case scenario (zero payout).
    """
    payout_home = (S_H * O_H) if O_H is not None else 0
    payout_away = (S_A * O_A) if O_A is not None else 0
    return min(payout_home, payout_away)

def calculate_guaranteed_profit(S_H: float, S_A: float, O_H: Optional[float], O_A: Optional[float]) -> float:
    """
    Calculates the guaranteed profit, handling cancellations correctly.
    If a side is cancelled, its stake is considered zero as the bet will not take place.
    """
    guaranteed_payout = calculate_guaranteed_payout(S_H, S_A, O_H, O_A)
    total_stake = (S_H if O_H is not None else 0) + (S_A if O_A is not None else 0)
    return guaranteed_payout - total_stake
