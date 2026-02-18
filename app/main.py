from __future__ import annotations

import random
from dataclasses import asdict, dataclass

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


@dataclass
class Bet:
    algo: str
    side: str
    stake: float
    odds_b: float


class Simulator:
    def __init__(self) -> None:
        self.reset_coin()

    def reset_coin(self) -> None:
        self.true_p_heads = random.uniform(0.2, 0.8)
        self.heads = 0
        self.tails = 0
        self.flip_index = 0
        self.round_index = 0
        self.starting_algo = 1
        self.pending_bets: list[Bet] = []
        self.phase = "initial_flip"
        self.bankroll = {"algo1": 1000.0, "algo2": 1000.0}
        self.last_result = ""
        self.amm_head = 100.0
        self.amm_tail = 100.0

    def state(self) -> dict:
        return {
            "true_p_heads": self.true_p_heads,
            "heads": self.heads,
            "tails": self.tails,
            "flip_index": self.flip_index,
            "round_index": self.round_index,
            "phase": self.phase,
            "bankroll": self.bankroll,
            "amm": {"head": self.amm_head, "tail": self.amm_tail},
            "pending_bets": [asdict(b) for b in self.pending_bets],
            "last_result": self.last_result,
        }

    def step(self) -> dict:
        if self.phase == "initial_flip":
            self._coin_flip(settle=False)
            self.phase = "bet_1"
            self.last_result = "Initial flip done (no bets)."
            return self.state()

        if self.phase.startswith("bet_"):
            order = self._bet_order_for_round()
            idx = int(self.phase.split("_")[1]) - 1
            algo = order[idx]
            self._place_bet(algo)
            self.phase = "bet_2" if idx == 0 else "flip_settle"
            return self.state()

        if self.phase == "flip_settle":
            outcome = self._coin_flip(settle=True)
            self.round_index += 1
            self.starting_algo = 2 if self.starting_algo == 1 else 1
            self.phase = "bet_1"
            self.last_result = f"Flip={outcome}. Settled {len(self.pending_bets)} bets."
            self.pending_bets = []
            return self.state()

        return self.state()

    def dry_flips(self, n: int = 1) -> dict:
        for _ in range(max(1, n)):
            self._coin_flip(settle=False)
        self.last_result = f"Dry flips executed: {max(1, n)}"
        return self.state()

    def _bet_order_for_round(self) -> list[str]:
        return ["algo1", "algo2"] if self.starting_algo == 1 else ["algo2", "algo1"]

    def _coin_flip(self, settle: bool) -> str:
        outcome = "heads" if random.random() < self.true_p_heads else "tails"
        self.flip_index += 1
        if outcome == "heads":
            self.heads += 1
        else:
            self.tails += 1

        if settle:
            for bet in self.pending_bets:
                self.bankroll[bet.algo] += bet.stake * bet.odds_b if bet.side == outcome else -bet.stake

        return outcome

    def _place_bet(self, algo: str) -> None:
        p_head = self._estimate_p_head(algo)
        implied_p_head = self.amm_head / (self.amm_head + self.amm_tail)

        if p_head >= implied_p_head:
            side = "heads"
            p = p_head
            b = self.amm_tail / self.amm_head
            stake = self._stake(algo, p, b)
            self.amm_head += stake
        else:
            side = "tails"
            p = 1.0 - p_head
            b = self.amm_head / self.amm_tail
            stake = self._stake(algo, p, b)
            self.amm_tail += stake

        self.pending_bets.append(Bet(algo=algo, side=side, stake=stake, odds_b=b))
        self.last_result = f"{algo} bet {stake:.2f} on {side} (b={b:.3f})"

    def _estimate_p_head(self, algo: str) -> float:
        h, t = self.heads, self.tails
        if algo == "algo1":
            return 0.5 if h + t == 0 else h / (h + t)
        return (h + 1) / (h + t + 2)

    def _stake(self, algo: str, p: float, b: float) -> float:
        q = 1.0 - p
        f = (b * p - q) / b
        if algo == "algo2":
            f *= 0.5
        f = max(0.0, min(f, 1.0))
        return max(0.0, min(self.bankroll[algo] * f, 200.0))


app = FastAPI(title="Betting Site")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
sim = Simulator()


@app.get("/")
async def root():
    return FileResponse("app/static/index.html")


@app.get("/api/state")
async def get_state():
    return sim.state()


@app.post("/api/step")
async def step():
    return sim.step()


@app.post("/api/new-coin")
async def new_coin():
    sim.reset_coin()
    return sim.state()


@app.post("/api/dry-flips")
async def dry_flips(n: int = 1):
    return sim.dry_flips(n=n)
