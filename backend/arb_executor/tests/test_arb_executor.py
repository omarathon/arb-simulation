import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
from backend.arb_executor.src.arb_executor import ArbExecutor
from backend.shared.redis import ArbMessage, get_odds_match_bookmaker_key
from backend.shared.config import shared_config
from backend.shared.arb_math import calculate_guaranteed_profit
from backend.arb_executor.src.config import arb_executor_config


@pytest.fixture
def mock_redis():
    mock = MagicMock()
    mock.hget.side_effect = lambda key, field: json.dumps({
        "home_win": 2.1, "away_win": 2.2
    }) if field in [get_odds_match_bookmaker_key("Bet365"), get_odds_match_bookmaker_key("Smarkets")] else None
    mock.publish = MagicMock()
    return mock

@pytest.fixture
def arb_executor(mock_redis):
    """Initialize ArbExecutor with a mocked Redis client."""
    return ArbExecutor(redis_client=mock_redis)


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_execute_arb_successful(mock_sleep, arb_executor, mock_redis):
    """Test executing an arbitrage successfully when odds remain unchanged."""
    
    # Arrange
    arb_message = ArbMessage(
        id="test-arb-1",
        match="Match1",
        home_win_bookmaker="Bet365",
        away_win_bookmaker="Smarkets",
        home_win_odds=2.1,
        away_win_odds=2.2,
        home_win_stake=50.0,
        away_win_stake=50.0,
        guaranteed_profit=calculate_guaranteed_profit(50.0, 50.0, 2.1, 2.2),
        status="detected",
        timestamp=1234567890
    )

    # Act
    await arb_executor.execute_arb(arb_message)

    ### Assert ###

    mock_sleep.assert_called_once_with(arb_executor_config.DELAY_SECONDS_TO_EXECUTE_ARB) # Ensure the simulated delay
    mock_redis.publish.assert_called_once()
    published_channel, published_message = mock_redis.publish.call_args[0]

    assert published_channel == shared_config.REDIS_ARB_EXECUTIONS_CHANNEL

    published_arb = json.loads(published_message)
    assert published_arb["status"] == "completed"
    assert published_arb["home_win_odds"] == 2.1
    assert published_arb["away_win_odds"] == 2.2
    assert published_arb["guaranteed_profit"] == calculate_guaranteed_profit(50.0, 50.0, 2.1, 2.2)


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_execute_arb_adjusted_odds(mock_sleep, arb_executor, mock_redis):
    """Test executing an arbitrage when the odds change before execution."""

    # Arrange
    arb_message = ArbMessage(
        id="test-arb-2",
        match="Match2",
        home_win_bookmaker="Bet365",
        away_win_bookmaker="Smarkets",
        home_win_odds=2.1,
        away_win_odds=2.2,
        home_win_stake=50.0,
        away_win_stake=50.0,
        guaranteed_profit=calculate_guaranteed_profit(50.0, 50.0, 2.1, 2.2),
        status="detected",
        timestamp=1234567890
    )

    # Simulate fetching adjusted odds
    mock_redis.hget.side_effect = lambda key, field: json.dumps({
        "home_win": 1.5, "away_win": 1.9
    }) if field in [get_odds_match_bookmaker_key("Bet365"), get_odds_match_bookmaker_key("Smarkets")] else None

    # Act
    await arb_executor.execute_arb(arb_message)

    ### Assert ###

    mock_sleep.assert_called_once_with(arb_executor_config.DELAY_SECONDS_TO_EXECUTE_ARB)
    mock_redis.publish.assert_called_once()
    published_channel, published_message = mock_redis.publish.call_args[0]

    assert published_channel == shared_config.REDIS_ARB_EXECUTIONS_CHANNEL

    published_arb = json.loads(published_message)
    assert published_arb["status"] == "adjusted"
    assert published_arb["home_win_odds"] == 1.5
    assert published_arb["away_win_odds"] == 1.9
    assert published_arb["guaranteed_profit"] != calculate_guaranteed_profit(50.0, 50.0, 2.1, 2.2)
    assert published_arb["guaranteed_profit"] == calculate_guaranteed_profit(50.0, 50.0, 1.5, 1.9)


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_execute_arb_cancelled_due_to_single_missing_odds(mock_sleep, arb_executor, mock_redis):
    """Test arbitrage execution is cancelled if odds disappear on a single side (market closed)."""

    # Arrange
    arb_message = ArbMessage(
        id="test-arb-3",
        match="Match3",
        home_win_bookmaker="Bet365",
        away_win_bookmaker="Smarkets",
        home_win_odds=2.1,
        away_win_odds=2.2,
        home_win_stake=49.0,
        away_win_stake=50.0,
        guaranteed_profit=calculate_guaranteed_profit(49.0, 50.0, 2.1, 2.2),
        status="detected",
        timestamp=1234567890
    )

    # Simulate one side missing (home_win_odds is missing, away_win_odds remains)
    mock_redis.hget.side_effect = lambda key, field: (
        None if field == get_odds_match_bookmaker_key("Bet365") else json.dumps({"home_win": 2.1, "away_win": 2.2})
    )

    # Act
    await arb_executor.execute_arb(arb_message)

    ### Assert ###

    mock_sleep.assert_called_once_with(arb_executor_config.DELAY_SECONDS_TO_EXECUTE_ARB)
    mock_redis.publish.assert_called_once()
    published_channel, published_message = mock_redis.publish.call_args[0]

    assert published_channel == shared_config.REDIS_ARB_EXECUTIONS_CHANNEL

    published_arb = json.loads(published_message)

    # Verify cancellation due to one side missing
    assert published_arb["status"] == "cancelled"
    assert published_arb["home_win_odds"] is None  # Home odds are missing
    assert published_arb["away_win_odds"] == 2.2  # Away odds still present
    # Since one side is missing, we executed the other side but it's not guaranteed to payout, so we lose money in the worst case
    assert published_arb["guaranteed_profit"] == -50


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_execute_arb_cancelled_due_to_double_missing_odds(mock_sleep, arb_executor, mock_redis):
    """Test arbitrage execution is cancelled if odds disappear on both sides (market closed)."""

    # Arrange
    arb_message = ArbMessage(
        id="test-arb-3",
        match="Match3",
        home_win_bookmaker="Bet365",
        away_win_bookmaker="Smarkets",
        home_win_odds=2.1,
        away_win_odds=2.2,
        home_win_stake=50.0,
        away_win_stake=50.0,
        guaranteed_profit=calculate_guaranteed_profit(50.0, 50.0, 2.1, 2.2),
        status="detected",
        timestamp=1234567890
    )

    # Simulate odds being removed (market closed)
    mock_redis.hget.side_effect = lambda key, field: None  # Simulate missing odds

    # Act
    await arb_executor.execute_arb(arb_message)

    ### Assert ###

    mock_sleep.assert_called_once_with(arb_executor_config.DELAY_SECONDS_TO_EXECUTE_ARB)
    mock_redis.publish.assert_called_once()
    published_channel, published_message = mock_redis.publish.call_args[0]

    assert published_channel == shared_config.REDIS_ARB_EXECUTIONS_CHANNEL

    published_arb = json.loads(published_message)
    assert published_arb["status"] == "cancelled"
    assert published_arb["home_win_odds"] is None and published_arb["away_win_odds"] is None
    assert published_arb["guaranteed_profit"] != calculate_guaranteed_profit(50.0, 50.0, 2.1, 2.2)
    assert published_arb["guaranteed_profit"] == 0
