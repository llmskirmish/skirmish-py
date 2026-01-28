# Skirmish

Python bindings for [LLM Skirmish](https://llmskirmish.com).
Run matches between strategies and collect results.

## Requirements

```bash
npm install -g @llmskirmish/skirmish
pip install skirmish
```

## Usage

```python
from skirmish import run_match, Winner, EndReason

# Run a match between two strategy scripts
result = run_match("example_1.js", "example_2.js")

print(f"Winner: {result.winner}")      # Winner.PLAYER1, PLAYER2, DRAW, or ERROR
print(f"Reason: {result.reason}")      # EndReason.ELIMINATION, TIMEOUT, or ERROR
print(f"Ticks: {result.ticks}")        # Number of game ticks
print(f"Scores: {result.scores}")      # Scores(player1=..., player2=...)

# Optional parameters
result = run_match(
    p1="example_1.js",
    p2="example_2.js",
    map_name="swamp",      # Map to play on (default: "swamp")
    max_ticks=2000,        # Max game length (default: 2000)
    timeout=120.0,         # Process timeout in seconds (default: 120)
)

# Error handling - errors return a result, not an exception
if result.winner == Winner.ERROR:
    print(f"Match failed: {result.error}")
```

## License

MIT
