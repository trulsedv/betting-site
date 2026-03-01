from __future__ import annotations

import random


class CoinProcess:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        p_heads = random.uniform(0.2, 0.8)
        self.probabilities = {"heads": p_heads, "tails": 1.0 - p_heads}
        self.occurrences = {"heads": 0, "tails": 0}

    def toss(self) -> str:
        rndm = random.random()

        outcome = "heads" if rndm < self.probabilities["heads"] else "tails"
        self.occurrences[outcome] += 1
        return outcome
