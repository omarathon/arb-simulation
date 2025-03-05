import pytest
from backend.arb_engine.src.arb_engine import ArbOpportunity

def test_arb_opportunity_calculations():
    arb = ArbOpportunity("Match1", "BookmakerA", "BookmakerB", odds_home_win=2.0, odds_away_win=2.5)

    assert arb.get_probability_home_win() == pytest.approx(0.5, rel=1e-3), "Home win probability should be 1/odds."
    assert arb.get_probability_away_win() == pytest.approx(0.4, rel=1e-3), "Away win probability should be 1/odds."
    assert arb.get_combined_market_margin() == pytest.approx(0.9, rel=1e-3), "Market margin should be sum of probabilities."

@pytest.mark.parametrize(
    "odds_home, odds_away, expected, message",
    [
        (2.0, 2.5, True, "Arbitrage should exist if market margin < 1."),
        (2.0, 1.9, False, "Arbitrage should not exist if market margin >= 1."),
    ]
)
def test_arb_opportunity_arbitrage_exists(odds_home, odds_away, expected, message):
    arb = ArbOpportunity("Match1", "BookmakerA", "BookmakerB", odds_home_win=odds_home, odds_away_win=odds_away)
    assert arb.is_net_gain() == expected, message