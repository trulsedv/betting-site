from __future__ import annotations

import math


class ConstantProductYesNoAMM:
    """Simple yes/no AMM with constant product inventory math.

    Balances:
    - `heads`: yes-token inventory in market
    - `tails`: no-token inventory in market
    - `money`: money-token inventory in market

    Price convention used by this app:
    - price(heads) = tails / (heads + tails)
    - price(tails) = heads / (heads + tails)

    With this convention, buying heads decreases `heads` reserve and increases
    `tails` reserve, which raises `price(heads)` as expected.
    """

    def __init__(self, money_tokens: float) -> None:
        self.resolution = None
        self.seed(money_tokens)

    def seed(self, money_tokens: float) -> None:
        seed = max(0.0, money_tokens)
        self.balances = {"heads": seed, "tails": seed, "money": seed}

    def prices(self) -> dict[str, float]:
        y = self.balances["heads"]
        n = self.balances["tails"]
        total = y + n
        if total <= 0.0:
            return {"heads": 0.5, "tails": 0.5}  # should return NaN or similar since this mean the market has not been "seeded"
        return {
            "heads": n / total,
            "tails": y / total,
        }

    def preview_buy(self, side: str, money_in: float) -> float:
        if money_in <= 0.0:
            raise ValueError("Invalid money_in. Must be positive.")
        if side not in ["heads", "tails"]:
            raise ValueError("Invalid side. Must be 'heads' or 'tails'.")

        y = self.balances["heads"]
        n = self.balances["tails"]

        if side == "heads":
            tokens_out = y + money_in - (y * n / (n + money_in))
        if side == "tails":
            tokens_out = n + money_in - (y * n / (y + money_in))
        return tokens_out

    def preview_sell(self, side: str, tokens_in: float) -> float:
        if tokens_in <= 0.0:
            raise ValueError("Invalid tokens_in. Must be positive.")
        if side not in ["heads", "tails"]:
            raise ValueError("Invalid side. Must be 'heads' or 'tails'.")

        y = self.balances["heads"]
        n = self.balances["tails"]

        if side == "heads":
            money_out = ((y + n + tokens_in) - math.sqrt((y + n + tokens_in) ** 2 - (4.0 * tokens_in * n))) / 2.0
        if side == "tails":
            money_out = ((y + n + tokens_in) - math.sqrt((y + n + tokens_in) ** 2 - (4.0 * tokens_in * y))) / 2.0
        return money_out

    def buy(self, side: str, money_in: float) -> float:
        tokens_out = self.preview_buy(side, money_in)

        self.balances["money"] += money_in
        self.balances["heads"] += money_in
        self.balances["tails"] += money_in
        self.balances[side] -= tokens_out
        return tokens_out

    def sell(self, side: str, tokens_in: float) -> float:
        money_out = self.preview_sell(side, tokens_in)

        self.balances["money"] -= money_out
        self.balances["heads"] -= money_out
        self.balances["tails"] -= money_out
        self.balances[side] += tokens_in
        return money_out

    def resolve(self, outcome: str) -> None:
        self.resolution = outcome
    
    def payout(self, side: str, tokens: float) -> float:
        if self.resolution is None or self.resolution != side:
            return 0.0
        return tokens