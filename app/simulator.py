"""Core simulation engine coordinating coin, market, and trading algorithms."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.algorithms import BayesianHalfKellyStrategy, FrequencyKellyStrategy
from app.amm import ConstantProductYesNoAMM
from app.coin import CoinProcess

type Trader = FrequencyKellyStrategy | BayesianHalfKellyStrategy


class TradeRequest(BaseModel):
    """Request payload for a trade action."""

    algo: str
    side: str
    action: str


class Simulator:
    """Main simulation state and transition logic."""

    INITIAL_MARKET_MAKER_MONEY = 1e6
    INITIAL_MARKET_LIQUIDITY = 1e5
    INITIAL_TRADER_MONEY = 1e3
    EVENT_LOG_LIMIT = 300

    def __init__(self) -> None:
        """Initialize coin process, traders, market maker, and market state."""
        self.coin = CoinProcess()
        self.trader1 = FrequencyKellyStrategy(self.INITIAL_TRADER_MONEY)
        self.trader2 = BayesianHalfKellyStrategy(self.INITIAL_TRADER_MONEY)

        self.market_maker = {"money": self.INITIAL_MARKET_MAKER_MONEY}

        self.initialize_market()

        self.last_result = ""
        self.event_log: list[str] = []
        self.last_toss_outcome = ""

    def reset_coin(self) -> None:
        """Reset the coin process and reinitialize market liquidity."""
        self.coin.reset()
        self.trader1.reset_observations()
        self.trader2.reset_observations()

        # There should be a payout phase here for unresolved token positions.
        self.initialize_market()

    def initialize_market(self) -> None:
        """Create a new seeded market and debit market-maker cash."""
        self.market_maker["money"] -= self.INITIAL_MARKET_LIQUIDITY
        self.amm = ConstantProductYesNoAMM(self.INITIAL_MARKET_LIQUIDITY)

    def _set_result(self, message: str) -> None:
        self.last_result = message
        self.event_log.append(message)
        if len(self.event_log) > self.EVENT_LOG_LIMIT:
            self.event_log = self.event_log[-self.EVENT_LOG_LIMIT :]

    def _sync_algo_states(self) -> None:
        for trader in (self.trader1, self.trader2):
            trader.observations["heads"] = self.coin.occurrences["heads"]
            trader.observations["tails"] = self.coin.occurrences["tails"]

    def _get_trader(self, algo: str) -> Trader | None:
        if algo == "algo1":
            return self.trader1
        if algo == "algo2":
            return self.trader2
        return None

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

    def state(self) -> dict[str, Any]:
        """Return a complete view of current simulation state."""
        market_prices = self._market_prices()

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
            "algorithm1": self._algo_state("algo1"),
            "algorithm2": self._algo_state("algo2"),
            "market_maker": {"balances": self.market_maker},
            "last_result": self.last_result,
            "event_log": self.event_log,
            "last_toss_outcome": self.last_toss_outcome,
        }

    def _draw_outcome(self) -> str:
        outcome = self.coin.toss()
        self.last_toss_outcome = outcome
        return outcome

    def test_toss(self) -> dict[str, Any]:
        """Toss coin without resolving the market and return state."""
        outcome = self._draw_outcome()
        self._set_result(f"Test toss={outcome}. No market settlement.")
        return self.state()

    def event_toss(self) -> dict[str, Any]:
        """Toss coin, resolve market payouts, reseed market, and return state."""
        outcome = self._draw_outcome()
        self.amm.resolve(outcome)

        payout = 0.0
        for trader in (self.trader1, self.trader2):
            payout_heads = self.amm.payout("heads", trader.balances["heads"])
            payout_tails = self.amm.payout("tails", trader.balances["tails"])
            algo_payout = payout_heads + payout_tails

            trader.balances["money"] += algo_payout
            payout += algo_payout
            trader.balances["heads"] = 0.0
            trader.balances["tails"] = 0.0

        self.amm.balances["money"] -= payout

        remaining_money = self.amm.balances["money"]
        self.market_maker["money"] += remaining_money
        self.initialize_market()

        self._set_result(
            f"Event toss={outcome}. Paid out {payout:.2f}. "
            f"Returned {remaining_money:.2f} to market maker and re-seeded market.",
        )
        return self.state()

    def trade(self, algo: str, side: str, action: str) -> dict[str, Any]:
        """Validate and execute a buy or sell action, then return state."""
        trader = self._get_trader(algo)
        if trader is None:
            self._set_result(f"Invalid algo: {algo}")
        elif side not in {"heads", "tails"}:
            self._set_result(f"Invalid side: {side}")
        elif action not in {"buy", "sell"}:
            self._set_result(f"Invalid action: {action}")
        elif action == "buy":
            stake = self._calc_buy_stake(algo, side)
            if stake <= 0.0:
                self._set_result(f"{algo} buy {side}: no edge, no trade.")
            else:
                self._execute_buy(algo, side, stake)
        else:
            tokens_to_sell = self._calc_sell_tokens(algo, side)
            if tokens_to_sell <= 0.0:
                self._set_result(f"{algo} sell {side}: no tokens to sell.")
            else:
                self._execute_sell(algo, side, tokens_to_sell)
        return self.state()

    def _algo_state(self, algo: str) -> dict:
        trader = self._get_trader(algo)
        if trader is None:
            return {
                "estimate": {"heads": 0.5, "tails": 0.5},
                "balances": {"heads": 0.0, "tails": 0.0, "money": 0.0},
                "trades": {
                    "heads": {"buy": {"stake": 0.0, "tokens": 0.0}, "sell": {"money": 0.0, "tokens": 0.0}},
                    "tails": {"buy": {"stake": 0.0, "tokens": 0.0}, "sell": {"money": 0.0, "tokens": 0.0}},
                },
            }

        return {
            "estimate": {
                "heads": self._estimate_p_head(algo),
                "tails": 1.0 - self._estimate_p_head(algo),
            },
            "balances": trader.balances,
            "trades": {
                "heads": {
                    "buy": {
                        "stake": self._calc_buy_stake(algo, "heads"),
                        "tokens": self._calc_buy_tokens("heads", self._calc_buy_stake(algo, "heads")),
                    },
                    "sell": {
                        "money": self._calc_sell_money("heads", self._calc_sell_tokens(algo, "heads")),
                        "tokens": self._calc_sell_tokens(algo, "heads"),
                    },
                },
                "tails": {
                    "buy": {
                        "stake": self._calc_buy_stake(algo, "tails"),
                        "tokens": self._calc_buy_tokens("tails", self._calc_buy_stake(algo, "tails")),
                    },
                    "sell": {
                        "money": self._calc_sell_money("tails", self._calc_sell_tokens(algo, "tails")),
                        "tokens": self._calc_sell_tokens(algo, "tails"),
                    },
                },
            },
        }

    def _market_prices(self) -> dict[str, float]:
        return self.amm.prices()

    def _calc_buy_tokens(self, side: str, stake: float) -> float:
        if stake <= 0.0:
            return 0.0
        try:
            return self.amm.preview_buy(side, stake)
        except ValueError:
            return 0.0

    def _calc_sell_money(self, side: str, tokens: float) -> float:
        if tokens <= 0.0:
            return 0.0
        try:
            return self.amm.preview_sell(side, tokens)
        except ValueError:
            return 0.0

    def _calc_buy_stake(self, algo: str, side: str) -> float:
        self._sync_algo_states()
        trader = self._get_trader(algo)
        if trader is None:
            return 0.0

        if algo == "algo1":
            try:
                stake = self.trader1.calculate_buy_money_out(side, self.amm)
            except (ValueError, ZeroDivisionError):
                return 0.0

            bankroll = trader.balances["money"]
            return max(0.0, min(stake, bankroll, 200.0))

        if algo != "algo2":
            return 0.0

        prices = self._market_prices()
        p_head = self._estimate_p_head(algo)
        p = p_head if side == "heads" else (1.0 - p_head)
        price = prices[side]
        f = self.trader2.stake_fraction(p=p, price=price)

        bankroll = trader.balances["money"]
        return max(0.0, min(bankroll * f, 200.0))

    def _calc_sell_tokens(self, algo: str, side: str) -> float:
        trader = self._get_trader(algo)
        if trader is None:
            return 0.0

        held = trader.balances[side]
        if held <= 0.0:
            return 0.0

        prices = self._market_prices()
        p_head = self._estimate_p_head(algo)
        p = p_head if side == "heads" else (1.0 - p_head)
        market_p = prices[side]
        return held if p < market_p else 0.0

    def _execute_buy(self, algo: str, side: str, stake: float) -> None:
        trader = self._get_trader(algo)
        if trader is None:
            self._set_result(f"Invalid algo: {algo}")
            return

        if stake <= 0.0:
            self._set_result(f"{algo} buy {side}: invalid stake.")
            return

        try:
            tokens_out = self.amm.buy(side, stake)
        except ValueError:
            self._set_result(f"{algo} buy {side}: trade failed.")
            return

        if tokens_out <= 0.0:
            self._set_result(f"{algo} buy {side}: trade failed.")
            return

        trader.balances["money"] -= stake
        trader.balances[side] += tokens_out

        self._set_result(f"{algo} bought {tokens_out:.4f} {side} tokens for {stake:.2f}.")

    def _execute_sell(self, algo: str, side: str, tokens_to_sell: float) -> None:
        trader = self._get_trader(algo)
        if trader is None:
            self._set_result(f"Invalid algo: {algo}")
            return

        tokens_to_sell = min(tokens_to_sell, trader.balances[side])
        if tokens_to_sell <= 0.0:
            self._set_result(f"{algo} sell {side}: invalid token amount.")
            return

        liquidity_cap = min(
            self.amm.balances.get("money", 0.0),
            self.amm.balances.get("heads", 0.0),
            self.amm.balances.get("tails", 0.0),
        )
        preview_money = self._calc_sell_money(side, tokens_to_sell)
        if preview_money <= 0.0 or preview_money > liquidity_cap:
            self._set_result(f"{algo} sell {side}: insufficient market liquidity.")
            return

        try:
            money_out = self.amm.sell(side, tokens_to_sell)
        except ValueError:
            self._set_result(f"{algo} sell {side}: trade failed.")
            return

        if money_out <= 0.0:
            self._set_result(f"{algo} sell {side}: trade failed.")
            return

        trader.balances[side] -= tokens_to_sell
        trader.balances["money"] += money_out

        self._set_result(f"{algo} sold {tokens_to_sell:.4f} {side} tokens for {money_out:.2f}.")

    def _estimate_p_head(self, algo: str) -> float:
        self._sync_algo_states()

        if algo == "algo1":
            try:
                return self.trader1.estimate_p("heads")
            except ValueError:
                return 0.5

        if algo != "algo2":
            return 0.5

        try:
            return self.trader2.estimate_p("heads")
        except ValueError:
            return 0.5
