"""Frequency-based Kelly trading strategy."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.amm import ConstantProductYesNoAMM


class FrequencyKellyStrategy:
    """Algorithm 1: observed-frequency estimate + full Kelly sizing."""

    def __init__(self, money: float) -> None:
        """Initialize balances and observation counters."""
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
        """Estimate side probability from relative outcome frequency."""
        if side not in self.valid_sides:
            msg = "Invalid side. Must be 'heads' or 'tails'."
            raise ValueError(msg)

        heads = self.observations["heads"]
        tails = self.observations["tails"]

        total = heads + tails
        if total == 0:
            p = 0.5
            return p

        if side == "heads":
            p = heads / total
        if side == "tails":
            p = tails / total

        return p

    def calculate_buy_money_out(self, side: str, market: ConstantProductYesNoAMM) -> float:
        """Calculate buy stake from edge, bankroll, and market inventories."""
        if side not in self.valid_sides:
            msg = "Invalid side. Must be 'heads' or 'tails'."
            raise ValueError(msg)

        m = self.balances["money"]
        p = self.estimate_p(side)
        hm = market.balances["heads"]
        tm = market.balances["tails"]

        if side == "heads":
            money_out = (p * hm - (1 - p) * tm) / (hm / m + (1 - p))
        if side == "tails":
            money_out = (p * tm - (1 - p) * hm) / (tm / m + (1 - p))

        return money_out
