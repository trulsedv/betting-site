"""Coin process used by the simulator."""

from __future__ import annotations

from random import SystemRandom


class CoinProcess:
    """Stateful Bernoulli process with hidden probability of heads."""

    def __init__(self) -> None:
        """Initialize and sample a fresh hidden probability."""
        self.reset()
        self.rng = SystemRandom()

    def reset(self) -> None:
        """Resample hidden probabilities and clear occurrence counters."""
        p_heads = self.rng.uniform(0.2, 0.8)
        self.probabilities = {"heads": p_heads, "tails": 1.0 - p_heads}
        self.occurrences = {"heads": 0, "tails": 0}

    def toss(self) -> str:
        """Draw one outcome according to the hidden probability."""
        rndm = self.rng.random()

        outcome = "heads" if rndm < self.probabilities["heads"] else "tails"
        self.occurrences[outcome] += 1
        return outcome
