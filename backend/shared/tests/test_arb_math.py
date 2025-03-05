import pytest
from backend.shared.arb_math import calculate_guaranteed_payout, calculate_guaranteed_profit

@pytest.mark.parametrize(
    "stake_home, stake_away, odds_home, odds_away, expected_payout, message",
    [
        (100, 100, 2.0, 2.0, 200, "Equal stakes and odds"),
        (50, 150, 3.0, 1.5, 150, "Different stakes and odds"),
        (100, 100, None, 2.0, 0, "Home odds missing, payout should be 0"),
        (100, 100, 2.0, None, 0, "Away odds missing, payout should be 0"),
        (100, 100, None, None, 0, "Both odds missing, payout should be 0"),
    ]
)
def test_calculate_guaranteed_payout(stake_home, stake_away, odds_home, odds_away, expected_payout, message):
    assert calculate_guaranteed_payout(stake_home, stake_away, odds_home, odds_away) == expected_payout, message

@pytest.mark.parametrize(
    "stake_home, stake_away, odds_home, odds_away, expected_profit, message",
    [
        (100, 100, 2.0, 2.0, 0, "No profit when odds are perfectly balanced"),
        (100, 150, 3.0, 1.8, 20, "Arbitrage should yield a profit"),
        (100, 100, None, 2.0, -100, "Missing home odds should result in a loss",),
        (100, 100, None, None, 0, "Missing both odds should result in neutral",),
    ]
)
def test_calculate_guaranteed_profit(stake_home, stake_away, odds_home, odds_away, expected_profit, message):
    assert calculate_guaranteed_profit(stake_home, stake_away, odds_home, odds_away) == expected_profit, message
