import pytest
import json
import asyncio
from collections import Counter
from unittest.mock import MagicMock, patch
from backend.scraper.src.odds_publisher import OddsPublisher
from backend.shared.redis import OddsValues, get_odds_match_bookmaker_key, get_odds_match_hash
from backend.scraper.src.config import scraper_config
from backend.shared.config import shared_config


@pytest.fixture
def mock_redis():
    """Mock Redis client to capture published messages."""
    mock = MagicMock()
    mock.publish = MagicMock()
    mock.hset = MagicMock()
    mock.hdel = MagicMock()
    return mock


@pytest.fixture
def odds_publisher(mock_redis):
    """Initialize OddsPublisher with a fixed seed for deterministic testing."""
    return OddsPublisher(redis_client=mock_redis, seed=42)  # Deterministic via seed


@pytest.mark.asyncio
async def test_publish_odds(mock_redis, odds_publisher):
    """Test `publish_odds` ensuring correct proportions of updates and closures."""

    ### Arrange ###

    scraper_config.ODDS_PUBLISH_INTERVAL = 0.0  # Faster updates

    published_messages = []
    required_updates = 1000  # Ensure enough events for statistical check

    def track_published_message(*args, **kwargs):
        try:
            message = json.loads(args[1])
            published_messages.append(message["event"])
        except json.JSONDecodeError:
            pytest.fail("Published message is not valid JSON")

    mock_redis.publish.side_effect = track_published_message

    async def controlled_publish():
        """Run `publish_odds` and wait until we collect enough updates."""
        task = asyncio.create_task(odds_publisher.publish_odds())

        while len(published_messages) < required_updates:
            await asyncio.sleep(0.01)

        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


    # Act
    await controlled_publish()

    #### Assert ###

    published_messages = published_messages[:required_updates]
    message_counts = Counter(published_messages)

    total_actions = sum(message_counts.values())
    update_ratio_observed = message_counts["odds_update"] / total_actions
    close_ratio_observed = message_counts["odds_close"] / total_actions

    total_publishing_probability = (
        scraper_config.ODDS_UPDATE_PROBABILITY + scraper_config.ODDS_CLOSE_PROBABILITY
    ) # As we don't publish keeps

    expected_update_ratio = (
        scraper_config.ODDS_UPDATE_PROBABILITY / total_publishing_probability
    )
    expected_close_ratio = (
        scraper_config.ODDS_CLOSE_PROBABILITY / total_publishing_probability
    )

    assert pytest.approx(update_ratio_observed, rel=0.1) == expected_update_ratio
    assert pytest.approx(close_ratio_observed, rel=0.1) == expected_close_ratio

    # Ensure Redis received correct calls
    assert mock_redis.publish.call_count > 0, "No messages were published to Redis"
    assert mock_redis.hset.call_count > 0, "No odds were stored in Redis"
    assert mock_redis.hdel.call_count > 0, "No odds were deleted in Redis"

    print(f"Updates: {message_counts['odds_update']} ({update_ratio_observed:.2%})")
    print(f"Closures: {message_counts['odds_close']} ({close_ratio_observed:.2%})")


@pytest.mark.parametrize(
    "random_value, expected_action",
    [
        (0.05, "update"),  # Below update threshold
        (0.25, "close"),   # Between update + close threshold
        (0.9, "keep")      # Above update + close threshold
    ]
)
def test_determine_action(random_value, expected_action, odds_publisher):
    """Ensure `determine_action` returns correct actions based on probability."""
    with patch("random.random", return_value=random_value):
        assert odds_publisher.determine_action() == expected_action


def test_generate_realistic_odds(odds_publisher):
    """Ensure `generate_realistic_odds` creates odds within expected ranges."""
    odds = odds_publisher.generate_realistic_odds()
    assert scraper_config.HOME_WIN_ODDS_MIN <= odds.home_win <= scraper_config.HOME_WIN_ODDS_MAX
    assert odds.away_win > 1.0  # No invalid odds


def test_close_odds(mock_redis, odds_publisher):
    """Ensure `close_odds` correctly updates `odds_state` and calls Redis."""
    match, bookmaker = "Match1", "Bet365"
    odds_publisher.odds_state[(bookmaker, match)] = OddsValues(home_win=2.0, away_win=3.0)

    odds_publisher.close_odds(match, bookmaker)

    assert odds_publisher.odds_state[(bookmaker, match)] is None
    mock_redis.publish.assert_called()
    mock_redis.hdel.assert_called()


def test_update_odds(mock_redis, odds_publisher):
    """Ensure `update_odds` correctly updates Redis and internal state."""
    match, bookmaker = "Match1", "Bet365"

    odds_publisher.update_odds(match, bookmaker)

    # Ensure internal state is updated
    assert (bookmaker, match) in odds_publisher.odds_state
    updated_odds = odds_publisher.odds_state[(bookmaker, match)]
    assert scraper_config.HOME_WIN_ODDS_MIN <= updated_odds.home_win <= scraper_config.HOME_WIN_ODDS_MAX
    assert updated_odds.away_win > 1.0  # Ensure odds are realistic

    called_args = mock_redis.hset.call_args
    assert called_args is not None, "Redis hset was not called."

    expected_match_hash = get_odds_match_hash(match)
    expected_bookmaker_key = get_odds_match_bookmaker_key(bookmaker)
    expected_serialized_odds = json.dumps(updated_odds.model_dump())

    # Ensure correct Redis call
    assert called_args[0][0] == expected_match_hash
    assert called_args[0][1] == expected_bookmaker_key
    assert json.loads(called_args[0][2]) == json.loads(expected_serialized_odds)


@pytest.mark.parametrize("home_odds, vig", [
    (2.0, 0.05),
    (1.8, 0.05),
    (3.0, 0.05),
])
def test_calculate_away_odds_with_vig(odds_publisher, home_odds, vig):
    """Ensure `calculate_away_odds` correctly applies vig."""
    scraper_config.VIG_PROBABILITY = vig
    calculated_away_odds = odds_publisher.calculate_away_odds(home_odds)

    home_prob = 1 / home_odds
    away_prob = 1 + vig - home_prob
    expected_away_odds = round(1 / away_prob, 2)

    assert pytest.approx(calculated_away_odds, rel=0.05) == expected_away_odds, \
        f"Expected {expected_away_odds} but got {calculated_away_odds}"
