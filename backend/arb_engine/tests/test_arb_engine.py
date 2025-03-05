import pytest
import json
from unittest.mock import MagicMock
from backend.arb_engine.src.arb_engine import ArbEngine
from backend.shared.redis import OddsUpdateMessage, OddsValues, get_odds_match_bookmaker_key
from backend.shared.arb_math import calculate_guaranteed_profit
from backend.arb_engine.src.config import arb_engine_config
from backend.shared.config import shared_config
from backend.shared.utils import current_milli_time

@pytest.fixture
def mock_redis():
    return MagicMock()

@pytest.fixture
def arb_engine(mock_redis):
    return ArbEngine(redis_client=mock_redis)


@pytest.mark.asyncio
async def test_detect_arb_and_publish_bets(arb_engine, mock_redis):
    """Test full arbitrage detection and ensure the correct arb is published to Redis."""

    # Arrange
    mock_redis.hgetall.side_effect = lambda key: {
        "odds:Match1": {
            get_odds_match_bookmaker_key("Bet365"): json.dumps({"home_win": 2.0, "away_win": 2.5}),
            get_odds_match_bookmaker_key("Smarkets"): json.dumps({"home_win": 1.9, "away_win": 2.1})
        }
    }.get(key, {})
    mock_redis.publish = MagicMock()

    # Act
    # Run arbitrage detection
    await arb_engine.detect_arb_and_publish_bets(odds_update = OddsUpdateMessage(
        event="odds_update",
        match="Match1",
        bookmaker="Bet365",
        odds=OddsValues(home_win=2.0, away_win=2.5),
        timestamp=current_milli_time()
    ))

    ### Assert ###

    # Ensure Redis was queried correctly
    mock_redis.hgetall.assert_called_once_with("odds:Match1")

    mock_redis.publish.assert_called_once()  # Ensure something was published
    published_channel, published_message = mock_redis.publish.call_args[0]  # Extract call args

    # Verify it was published to the correct channel
    assert published_channel == shared_config.REDIS_ARB_DETECTIONS_CHANNEL

    # Validate the published arbitrage opportunity
    published_arb = json.loads(published_message)
    assert published_arb["match"] == "Match1"
    assert published_arb["home_win_bookmaker"] == "Bet365"
    assert published_arb["away_win_bookmaker"] == "Smarkets"
    assert published_arb["home_win_odds"] == 2.0
    assert published_arb["away_win_odds"] == 2.1
    assert published_arb["status"] == "detected"

    # Validate stake calculations
    total_stake = arb_engine_config.TOTAL_STAKE_PER_ARB
    expected_stake_home = (total_stake * (1 / 2.0)) / ((1 / 2.0) + (1 / 2.1))
    expected_stake_away = (total_stake * (1 / 2.1)) / ((1 / 2.0) + (1 / 2.1))
    expected_profit = calculate_guaranteed_profit(
        expected_stake_home, expected_stake_away, 2.0, 2.1
    )
    assert published_arb["home_win_stake"] == pytest.approx(expected_stake_home, rel=1e-3)
    assert published_arb["away_win_stake"] == pytest.approx(expected_stake_away, rel=1e-3)
    assert published_arb["guaranteed_profit"] == pytest.approx(expected_profit, rel=1e-3)


@pytest.mark.asyncio
async def test_no_arb_detected(arb_engine, mock_redis):
    """Test that no arbitrage is detected when combined market margin is >= 1.0."""

    # Arrange
    mock_redis.hgetall.side_effect = lambda key: {
        "odds:Match1": {
            get_odds_match_bookmaker_key("Bet365"): json.dumps({"home_win": 1.8, "away_win": 2.3}),
            get_odds_match_bookmaker_key("Smarkets"): json.dumps({"home_win": 1.9, "away_win": 2.2})
        }
    }.get(key, {})
    mock_redis.publish = MagicMock()

    # Act
    await arb_engine.detect_arb_and_publish_bets(odds_update = OddsUpdateMessage(
        event="odds_update",
        match="Match1",
        bookmaker="Bet365",
        odds=OddsValues(home_win=1.8, away_win=2.1),  # No arbitrage should exist
        timestamp=current_milli_time()
    ))

    # Assert
    mock_redis.hgetall.assert_called_once_with("odds:Match1")
    mock_redis.publish.assert_not_called()

