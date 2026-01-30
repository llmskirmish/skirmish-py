"""Tests for run_match using example strategies."""

from importlib.resources import files

import pytest

from skirmish import EndReason, MatchResult, Scores, Winner, run_match

STRATEGIES = files("skirmish.strategies")
EXAMPLE_1 = STRATEGIES / "example_1.js"
EXAMPLE_2 = STRATEGIES / "example_2.js"


@pytest.fixture(scope="module")
def cli_available() -> bool:
    """Check if skirmish CLI is installed."""
    import shutil
    return shutil.which("skirmish") is not None


@pytest.fixture
def require_cli(cli_available: bool) -> None:
    """Skip test if CLI not available."""
    if not cli_available:
        pytest.skip("skirmish CLI not installed")


class TestRunMatch:
    """Tests for run_match function."""

    def test_returns_match_result(self, require_cli: None) -> None:
        """run_match returns a MatchResult."""
        result = run_match(EXAMPLE_1, EXAMPLE_2, max_ticks=100)
        assert isinstance(result, MatchResult)

    def test_result_has_winner(self, require_cli: None) -> None:
        """Result has a valid winner."""
        result = run_match(EXAMPLE_1, EXAMPLE_2, max_ticks=100)
        assert result.winner in (Winner.PLAYER1, Winner.PLAYER2, Winner.DRAW)

    def test_result_has_reason(self, require_cli: None) -> None:
        """Result has a valid end reason."""
        result = run_match(EXAMPLE_1, EXAMPLE_2, max_ticks=100)
        assert result.reason in (EndReason.ELIMINATION, EndReason.TIMEOUT)

    def test_result_has_scores(self, require_cli: None) -> None:
        """Result has scores for both players."""
        result = run_match(EXAMPLE_1, EXAMPLE_2, max_ticks=100)
        assert isinstance(result.scores, Scores)
        assert isinstance(result.scores.player1, int)
        assert isinstance(result.scores.player2, int)

    def test_result_has_ticks(self, require_cli: None) -> None:
        """Result has tick count."""
        result = run_match(EXAMPLE_1, EXAMPLE_2, max_ticks=100)
        assert isinstance(result.ticks, int)
        assert 0 <= result.ticks <= 100

    def test_max_ticks_respected(self, require_cli: None) -> None:
        """Match ends at or before max_ticks."""
        result = run_match(EXAMPLE_1, EXAMPLE_2, max_ticks=50)
        assert result.ticks <= 50

    def test_same_strategy_vs_itself(self, require_cli: None) -> None:
        """Same strategy can play against itself."""
        result = run_match(EXAMPLE_1, EXAMPLE_1, max_ticks=100)
        assert isinstance(result, MatchResult)
        assert result.reason != EndReason.ERROR