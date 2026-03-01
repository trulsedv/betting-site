from __future__ import annotations


class BayesianHalfKellyStrategy:
    """Algorithm 2: Beta(1,1) posterior mean + half Kelly sizing."""

    def __init__(self, money: float) -> None:
        self.kelly_multiplier = 0.5
        self.observations = {"heads": 0, "tails": 0}
        self.balances = {"money": money, "heads": 0.0, "tails": 0.0}

    def observation(self, side: str) -> None:
        if side not in ["heads", "tails"]:
            raise ValueError("Invalid side. Must be 'heads' or 'tails'.")
        self.observations[side] += 1

    def reset_observations(self) -> None:
        self.observations = {"heads": 0, "tails": 0}

    def estimate_p(self, side: str) -> float:
        if side not in ["heads", "tails"]:
            raise ValueError("Invalid side. Must be 'heads' or 'tails'.")

        heads = self.observations["heads"]
        tails = self.observations["tails"]

        if side == "heads":
            return (heads + 1) / (heads + tails + 2)
        return (tails + 1) / (heads + tails + 2)

    def estimate_p_head(self, heads: int, tails: int) -> float:
        return (heads + 1) / (heads + tails + 2)

    def stake_fraction(self, p: float, price: float) -> float:
        if price <= 0.0 or price >= 1.0:
            return 0.0

        b = (1.0 - price) / price
        q = 1.0 - p
        f = (b * p - q) / b
        f *= self.kelly_multiplier
        return max(0.0, min(f, 1.0))
