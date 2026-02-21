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
        self.next_bettor = "algo1"
        self.pending_bets: list[Bet] = []
        self.phase = "betting"
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
            "next_bettor": self.next_bettor,
            "bankroll": self.bankroll,
            "amm": {"head": self.amm_head, "tail": self.amm_tail},
            "pending_bets": [asdict(b) for b in self.pending_bets],
            "last_result": self.last_result,
        }

    def next_bet(self) -> dict:
        algo = self.next_bettor
        self._place_bet(algo)
        self.next_bettor = "algo2" if algo == "algo1" else "algo1"
        return self.state()

    def flip_coin(self) -> dict:
        outcome = self._coin_flip(settle=True)
        settled = len(self.pending_bets)
        self.pending_bets = []
        self.round_index += 1
        self.phase = "betting"
        self.last_result = f"Flip={outcome}. Settled {settled} bets."
        return self.state()

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


@app.post("/api/next-bet")
async def next_bet():
    return sim.next_bet()


@app.post("/api/new-coin")
async def new_coin():
    sim.reset_coin()
    return sim.state()


@app.post("/api/flip-coin")
async def flip_coin():
    return sim.flip_coin()
