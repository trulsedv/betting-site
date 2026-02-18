# betting-site

Local FastAPI website simulating a betting competition between two algorithms on skewed coin flips.

## Run

```bash
cd /home/truls/.openclaw/workspace/betting-site
uv sync
uv run uvicorn app.main:app --reload
```

Open: http://127.0.0.1:8000

## Controls

- **Continue sequence**: advances one step:
  1. initial coin flip (no bet)
  2. first algorithm bets
  3. second algorithm bets
  4. coin flip + payout settlement
  5. next round alternates first bettor
- **New coin**: resamples hidden coin probability and resets estimates/history.
- **Dry flip**: coin flip without bets; algorithms still update observations.

## Algorithms

- **Algo 1**: observed-frequency estimate + Kelly criterion.
- **Algo 2**: Bayesian estimate (Beta-Bernoulli posterior mean) + half-Kelly.

Odds are implied from a simple two-reserve constant-product style AMM state.
