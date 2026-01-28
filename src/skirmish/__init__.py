"""
LLM Skirmish - Python bindings for LLM Skirmish.

Run matches between javascript strategies and collect results.
"""

import json
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

__version__ = "0.0.1"
__all__ = ["EndReason", "MatchResult", "Scores", "Winner", "run_match"]

@dataclass(frozen=True, slots=True)
class Scores:
    """Final scores for both players."""
    player1: int
    player2: int


class Winner(str, Enum):
    """Match outcome - who won."""
    PLAYER1 = "player1"
    PLAYER2 = "player2"
    DRAW = "draw" # very rare, requires both EndReason.TIMEOUT and MatchResult.scores to be equal
    ERROR = "error"


class EndReason(str, Enum):
    """Why the match ended."""
    ELIMINATION = "elimination"  # All enemy spawn was destroyed
    TIMEOUT = "timeout"          # Max ticks reached, winner by score
    ERROR = "error"              # Match failed to run (see error field)


@dataclass(frozen=True, slots=True)
class MatchResult:
    """Immutable result of a completed match."""
    winner: Winner
    reason: EndReason
    ticks: int
    scores: Scores
    error: str | None = None


def _parse_jsonl(output: str) -> Iterator[dict]:
    """Parse JSONL output, silently skipping malformed lines."""
    for line in output.strip().split("\n"):
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def _extract_result(output: str) -> tuple[Winner, EndReason, int, Scores]:
    """Extract (winner, reason, ticks, scores) from CLI JSONL output."""
    winner = Winner.DRAW
    reason = EndReason.TIMEOUT
    ticks = 0
    scores = Scores(0, 0)

    for data in _parse_jsonl(output):
        msg_type = data.get("type")
        if msg_type == "tick":
            ticks = data.get("tick", ticks)
        elif msg_type == "result":
            victory = data.get("victory", {})
            raw_winner = victory.get("winner")
            winner = Winner.PLAYER1 if raw_winner == "player1" else Winner.PLAYER2 if raw_winner == "player2" else Winner.DRAW
            reason = EndReason(victory.get("reason", "timeout"))
            raw_scores = victory.get("scores", {})
            scores = Scores(raw_scores.get("player1", 0), raw_scores.get("player2", 0))

    return winner, reason, ticks, scores


def _make_error(error_msg: str) -> MatchResult:
    """Create an error result."""
    return MatchResult(Winner.ERROR, EndReason.ERROR, 0, Scores(0, 0), error_msg)


def run_match(p1: str | Path, p2: str | Path, map_name: str = "swamp", max_ticks: int = 2000, timeout: float = 120.0) -> MatchResult:
    """Run a match between two JS bot strategies (p1/p2 are file paths)."""
    cmd = [
        "skirmish", "run",
        "--p1", str(p1), "--p2", str(p2),
        "--map", map_name, "--max-ticks", str(max_ticks), "--stdout",
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return _make_error("skirmish CLI not found. Install: npm i -g @llmskirmish/skirmish")
    except subprocess.TimeoutExpired:
        return _make_error(f"Match timed out after {timeout}s")

    if proc.returncode != 0:
        return _make_error(proc.stderr.strip() or f"Exit code {proc.returncode}")

    winner, reason, ticks, scores = _extract_result(proc.stdout)
    return MatchResult(winner, reason, ticks, scores)
