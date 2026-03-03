"""Core simulation engine coordinating coin, market, and trading algorithms."""

from __future__ import annotations

import math
from typing import Any

from pydantic import BaseModel

from app.algorithms import FrequencyKellyTrader
from app.amm import ConstantProductYesNoAMM
from app.coin import CoinProcess

type Trader = FrequencyKellyTrader


class TradeRequest(BaseModel):
    """Request payload for a trade action."""

    algo: str
    side: str
    action: str


class Simulator:
    """Main simulation state and transition logic."""

    INITIAL_MARKET_MAKER_MONEY = 0.0
    INITIAL_MARKET_LIQUIDITY = 1e3
    INITIAL_TRADER_MONEY = 1e3
    EVENT_LOG_LIMIT = 300

    def __init__(self) -> None:
        """Initialize coin process, traders, market maker, and market state."""
        self.coin = CoinProcess()
        self.trader1 = FrequencyKellyTrader("algo1", self.INITIAL_TRADER_MONEY, kelly_fraction=1.0)
        self.trader2 = FrequencyKellyTrader("algo2", self.INITIAL_TRADER_MONEY, kelly_fraction=0.5)

        self.market_maker = {"money": self.INITIAL_MARKET_MAKER_MONEY}

        self.last_result = ""
        self.event_log: list[str] = []
        self.last_toss_outcome = ""

        self.market_maker["money"] -= self.INITIAL_MARKET_LIQUIDITY
        self.amm = ConstantProductYesNoAMM(self.INITIAL_MARKET_LIQUIDITY)

    def reset_coin(self) -> None:
        """Reset flow: clear market, reset observations, and initialize a new coin."""
        self._clear_market()
        self.trader1.reset_observations()
        self.trader2.reset_observations()
        self.coin.reset()
        self._log_event("Reset complete: market cleared and coin reinitialized.")

    def test_toss(self) -> dict[str, Any]:
        """Toss coin without resolving the market and return state."""
        outcome = self._draw_outcome()
        self._log_event(f"Test toss={outcome}.")
        return self.state()

    def event_toss(self) -> dict[str, Any]:
        """Toss coin, resolve market to outcome, clear market, and return state."""
        outcome = self._draw_outcome()
        self._log_event(f"Event toss={outcome}.")
        self.amm.resolve(outcome)
        self._clear_market()
        return self.state()

    def trade(self, algo: str, side: str, action: str) -> dict[str, Any]:  # noqa: ARG002
        """Buy token flow: trader pays money, market outputs tokens, trader receives tokens."""
        trader = self._get_trader(algo)

        stake = trader.calculate_buy_money_out(side, self.amm)  # ty:ignore[unresolved-attribute]
        trader.pay_for_tokens(stake)  # ty:ignore[unresolved-attribute]
        tokens_out = self.amm.buy(side, stake)
        trader.recieve_tokens(side, tokens_out)  # ty:ignore[unresolved-attribute]
        self._log_event(f"{trader.name} bought {tokens_out:.4f} {side} tokens for {stake:.2f}.")  # ty:ignore[unresolved-attribute]

        return self.state()

    def _clear_market(self) -> None:
        """Close current market positions and reopen with default liquidity."""
        for trader in (self.trader1, self.trader2):
            # Trader hands in their outcome tokens
            tokens = trader.resolve_tokens()
            payout = 0
            for side in ("heads", "tails"):
                if tokens[side] == 0:
                    continue
                # Market recieve outcome tokens and outputs money tokens
                token_payout = self.amm.payout(side, tokens[side])
                payout += token_payout
                self._log_event(f"{trader.name} handed in {tokens[side]:.1f} {side} tokens for {token_payout:.1f} money tokens.")
            # Traders recieve money tokens
            trader.recieve_money(payout)

        self.market_maker["money"] += self.amm.balances["money"]
        self._log_event(f"Market maker withdrew {self.amm.balances['money']:.2f} money tokens, and closed the market.")
        self.market_maker["money"] -= self.INITIAL_MARKET_LIQUIDITY
        self.amm = ConstantProductYesNoAMM(self.INITIAL_MARKET_LIQUIDITY)
        self._log_event(f"Market maker deposited {self.INITIAL_MARKET_LIQUIDITY:.2f} money tokens, and opened the market.")

    def _draw_outcome(self) -> str:
        outcome = self.coin.toss()
        self.trader1.observation(outcome)
        self.trader2.observation(outcome)
        self.last_toss_outcome = outcome
        return outcome

    def _log_event(self, message: str) -> None:
        self.last_result = message
        self.event_log.append(message)
        if len(self.event_log) > self.EVENT_LOG_LIMIT:
            self.event_log = self.event_log[-self.EVENT_LOG_LIMIT :]

    def _get_trader(self, algo: str) -> Trader | None:
        if algo == "algo1":
            return self.trader1
        if algo == "algo2":
            return self.trader2
        return None

    def state(self) -> dict[str, Any]:
        """Return a complete view of current simulation state."""
        market_prices = self.amm.prices()

        return {
            "coin": self._coin_state(),
            "market": {
                "prices": {
                    "heads": market_prices["heads"],
                    "tails": market_prices["tails"],
                    "heads_derivative": None,
                    "tails_derivative": None,
                },
                "balances": self.amm.balances,
            },
            "algorithm1": self._algo_state(self.trader1),
            "algorithm2": self._algo_state(self.trader2),
            "market_maker": {"balances": self.market_maker},
            "last_result": self.last_result,
            "event_log": self.event_log,
            "last_toss_outcome": self.last_toss_outcome,
        }

    def _coin_state(self) -> dict:
        heads = self.coin.occurrences["heads"]
        tails = self.coin.occurrences["tails"]
        total = heads + tails

        return {
            "actual_probability": {
                "heads": self.coin.probabilities["heads"],
                "tails": self.coin.probabilities["tails"],
                "sum": 1.0,
            },
            "occurrence_count": {
                "heads": heads,
                "tails": tails,
                "sum": total,
            },
            "implied_probability": {
                "heads": (heads / total) if total else 0.0,
                "tails": (tails / total) if total else 0.0,
                "sum": 1.0 if total else 0.0,
            },
        }

    def _algo_state(self, trader: Trader) -> dict[str, Any]:
        try:
            p_head = trader.estimate_p("heads")
        except (TypeError, ValueError):
            p_head = 0.5

        try:
            heads_buy_stake = trader.calculate_buy_money_out("heads", self.amm)
        except (TypeError, ValueError, ZeroDivisionError, OverflowError):
            heads_buy_stake = 0.0
        if not isinstance(heads_buy_stake, (int, float)) or not math.isfinite(heads_buy_stake) or heads_buy_stake <= 0.0:
            heads_buy_stake = 0.0

        try:
            tails_buy_stake = trader.calculate_buy_money_out("tails", self.amm)
        except (TypeError, ValueError, ZeroDivisionError, OverflowError):
            tails_buy_stake = 0.0
        if not isinstance(tails_buy_stake, (int, float)) or not math.isfinite(tails_buy_stake) or tails_buy_stake <= 0.0:
            tails_buy_stake = 0.0

        try:
            heads_buy_tokens = self.amm.calc_token_out("heads", heads_buy_stake) if heads_buy_stake > 0.0 else 0.0
        except (TypeError, ValueError, ZeroDivisionError, OverflowError):
            heads_buy_tokens = 0.0
        if not isinstance(heads_buy_tokens, (int, float)) or not math.isfinite(heads_buy_tokens) or heads_buy_tokens <= 0.0:
            heads_buy_tokens = 0.0

        try:
            tails_buy_tokens = self.amm.calc_token_out("tails", tails_buy_stake) if tails_buy_stake > 0.0 else 0.0
        except (TypeError, ValueError, ZeroDivisionError, OverflowError):
            tails_buy_tokens = 0.0
        if not isinstance(tails_buy_tokens, (int, float)) or not math.isfinite(tails_buy_tokens) or tails_buy_tokens <= 0.0:
            tails_buy_tokens = 0.0

        return {
            "estimate": {
                "heads": p_head,
                "tails": 1.0 - p_head,
            },
            "balances": trader.balances,
            "trades": {
                "heads": {
                    "buy": {
                        "stake": heads_buy_stake,
                        "tokens": heads_buy_tokens,
                    },
                },
                "tails": {
                    "buy": {
                        "stake": tails_buy_stake,
                        "tokens": tails_buy_tokens,
                    },
                },
            },
        }
