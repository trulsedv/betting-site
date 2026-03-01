from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.amm import ConstantProductYesNoAMM


class FrequencyKellyStrategy:
    """Algorithm 1: observed-frequency estimate + full Kelly sizing."""

    def __init__(self, money: float) -> None:
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
        if side not in ["heads", "tails"]:
            raise ValueError("Invalid side. Must be 'heads' or 'tails'.")

        m = self.balances["money"]
        p = self.estimate_p(side)
        hm = market.balances["heads"]
        tm = market.balances["tails"]

        if side == "heads":
            money_out = (p * hm - (1 - p) * tm) / (hm / m + (1 - p))
        if side == "tails":
            money_out = (p * tm - (1 - p) * hm) / (tm / m + (1 - p))

        return money_out
