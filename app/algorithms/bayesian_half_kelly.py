"""Bayesian half-Kelly trading strategy."""

from __future__ import annotations


class BayesianHalfKellyStrategy:
    """Algorithm 2: Beta(1,1) posterior mean + half Kelly sizing."""

    def __init__(self, money: float) -> None:
        """Initialize balances and observation counters."""
        self.kelly_multiplier = 0.5
        self.observations = {"heads": 0, "tails": 0}
        self.balances = {"money": money, "heads": 0.0, "tails": 0.0}
        self.valid_sides = {"heads", "tails"}

    def observation(self, side: str) -> None:
        """Register one observed outcome."""
        if side not in self.valid_sides:
            msg = "Invalid side. Must be 'heads' or 'tails'."
            raise ValueError(msg)
        self.observations[side] += 1

    def reset_observations(self) -> None:
        """Clear all observed outcomes."""
        self.observations = {"heads": 0, "tails": 0}

    def estimate_p(self, side: str) -> float:
        """Estimate probability of the provided side with a Beta(1,1) prior."""
        if side not in self.valid_sides:
            msg = "Invalid side. Must be 'heads' or 'tails'."
            raise ValueError(msg)

        heads = self.observations["heads"]
        tails = self.observations["tails"]

        if side == "heads":
            return self.estimate_p_head(heads, tails)
        return (tails + 1) / (heads + tails + 2)

    @staticmethod
    def estimate_p_head(heads: int, tails: int) -> float:
        """Estimate the probability of heads from raw observation counts."""
        return (heads + 1) / (heads + tails + 2)

    def stake_fraction(self, p: float, price: float) -> float:
        """Return the half-Kelly fraction based on subjective edge and market price."""
        if price <= 0.0 or price >= 1.0:
            return 0.0

        b = (1.0 - price) / price
        q = 1.0 - p
        f = (b * p - q) / b
        f *= self.kelly_multiplier
        return max(0.0, min(f, 1.0))
