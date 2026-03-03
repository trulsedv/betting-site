"""Frequency-based Kelly trading strategy."""

from __future__ import annotations

import pathlib
import pickle  # noqa: S403
from typing import TYPE_CHECKING

import sympy as sp

if TYPE_CHECKING:
    from app.amm import ConstantProductYesNoAMM


class FrequencyKellyTrader:
    """Algorithm 1: observed-frequency estimate + full Kelly sizing."""

    def __init__(self, name: str, money: float, kelly_fraction: float) -> None:
        """Initialize balances and observation counters."""
        self.name = name
        self.observations = {"heads": 0, "tails": 0}
        self.balances = {"money": money, "money_placed": 0.0, "heads": 0.0, "tails": 0.0}
        self.kelly_fraction = kelly_fraction

        with pathlib.Path("app/algorithms/m_opt_solution.pkl").open("rb") as f:
            solution_data = pickle.load(f)  # noqa: S301
        self.optimal_money_out = sp.lambdify(solution_data["parameters"], solution_data["symbolic_solution"], "numpy")

    def observation(self, side: str) -> None:
        """Register one observed outcome."""
        self.observations[side] += 1

    def estimate_p(self, side: str) -> float:
        """Estimate side probability from relative outcome frequency."""
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
        p = self.estimate_p(side)
        if p in {0.0, 1.0}:
            return 0.0
        m = self.balances["money"]
        m0 = self.balances["money_placed"]
        mb0 = m + m0
        hm = market.balances["heads"]
        tm = market.balances["tails"]
        hb = self.balances["heads"]
        tb = self.balances["tails"]
        if side == "heads":
            money_out = self.optimal_money_out(m0, mb0, hb, hm, tm, tb, p)
        if side == "tails":
            money_out = self.optimal_money_out(m0, mb0, tb, tm, hm, hb, p)
        money_out *= self.kelly_fraction
        return min(max(money_out, 0.0), m)

    def pay_for_tokens(self, money_out: float) -> None:
        """Withdraw money tokens, and update money placed on tokens."""
        self.balances["money"] -= money_out
        self.balances["money_placed"] += money_out

    def recieve_tokens(self, side: str, tokens: float) -> None:
        """Receive tokens for a specific side."""
        self.balances[side] += tokens

    def resolve_tokens(self) -> dict[str, float]:
        """Hand out tokens for resolution."""
        tokens = {
            "heads": self.balances["heads"],
            "tails": self.balances["tails"],
        }
        self.balances["heads"] = 0.0
        self.balances["tails"] = 0.0
        self.balances["money_placed"] = 0.0
        return tokens

    def recieve_money(self, money: float) -> None:
        """Receive money tokens."""
        self.balances["money"] += money

    def reset_observations(self) -> None:
        """Clear all observed outcomes."""
        self.observations = {"heads": 0, "tails": 0}
