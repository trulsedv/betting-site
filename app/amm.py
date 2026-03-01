"""Constant-product yes/no AMM primitives."""

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
        """Initialize the market and seed symmetric liquidity."""
        self.resolution = None
        self.seed(money_tokens)
        self.valid_sides = {"heads", "tails"}

    def seed(self, money_tokens: float) -> None:
        """Seed equal heads, tails, and money balances."""
        seed = max(0.0, money_tokens)
        self.balances = {"heads": seed, "tails": seed, "money": seed}

    def prices(self) -> dict[str, float]:
        """Return implied prices for heads and tails."""
        y = self.balances["heads"]
        n = self.balances["tails"]
        total = y + n
        if total <= 0.0:
            return {"heads": 0.5, "tails": 0.5}
        return {
            "heads": n / total,
            "tails": y / total,
        }

    def preview_buy(self, side: str, money_in: float) -> float:
        """Preview token output for a buy without mutating balances."""
        if money_in <= 0.0:
            msg = "Invalid money_in. Must be positive."
            raise ValueError(msg)
        if side not in self.valid_sides:
            msg = "Invalid side. Must be 'heads' or 'tails'."
            raise ValueError(msg)

        y = self.balances["heads"]
        n = self.balances["tails"]

        if side == "heads":
            tokens_out = y + money_in - (y * n / (n + money_in))
        if side == "tails":
            tokens_out = n + money_in - (y * n / (y + money_in))
        return tokens_out

    def preview_sell(self, side: str, tokens_in: float) -> float:
        """Preview money output for a sell without mutating balances."""
        if tokens_in <= 0.0:
            msg = "Invalid tokens_in. Must be positive."
            raise ValueError(msg)
        if side not in self.valid_sides:
            msg = "Invalid side. Must be 'heads' or 'tails'."
            raise ValueError(msg)

        y = self.balances["heads"]
        n = self.balances["tails"]

        if side == "heads":
            money_out = ((y + n + tokens_in) - math.sqrt((y + n + tokens_in) ** 2 - (4.0 * tokens_in * n))) / 2.0
        if side == "tails":
            money_out = ((y + n + tokens_in) - math.sqrt((y + n + tokens_in) ** 2 - (4.0 * tokens_in * y))) / 2.0
        return money_out

    def buy(self, side: str, money_in: float) -> float:
        """Execute a buy and mutate market balances."""
        tokens_out = self.preview_buy(side, money_in)

        self.balances["money"] += money_in
        self.balances["heads"] += money_in
        self.balances["tails"] += money_in
        self.balances[side] -= tokens_out
        return tokens_out

    def sell(self, side: str, tokens_in: float) -> float:
        """Execute a sell and mutate market balances."""
        money_out = self.preview_sell(side, tokens_in)

        self.balances["money"] -= money_out
        self.balances["heads"] -= money_out
        self.balances["tails"] -= money_out
        self.balances[side] += tokens_in
        return money_out

    def resolve(self, outcome: str) -> None:
        """Set the final market outcome used for payouts."""
        self.resolution = outcome

    def payout(self, side: str, tokens: float) -> float:
        """Return payout for winning side tokens after resolution."""
        if self.resolution is None or self.resolution != side:
            return 0.0
        return tokens
