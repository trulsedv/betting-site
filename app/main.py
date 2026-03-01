"""FastAPI entrypoint for the betting simulator."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.simulator import Simulator, TradeRequest

app = FastAPI(title="Betting Site")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
sim = Simulator()


@app.get("/")
async def root() -> FileResponse:
    """Serve the single-page frontend."""
    return FileResponse("app/static/index.html")


@app.get("/api/state")
async def get_state() -> dict[str, Any]:
    """Return full current simulator state."""
    return sim.state()


@app.post("/api/reset")
async def reset() -> dict[str, Any]:
    """Reset coin process and market, then return state."""
    sim.reset_coin()
    return sim.state()


@app.post("/api/toss")
async def toss_coin() -> dict[str, Any]:
    """Run a resolving toss and return resulting state."""
    return sim.event_toss()


@app.post("/api/test-toss")
async def test_toss() -> dict[str, Any]:
    """Run a non-settling toss and return resulting state."""
    return sim.test_toss()


@app.post("/api/event-toss")
async def event_toss() -> dict[str, Any]:
    """Run a settling toss and return resulting state."""
    return sim.event_toss()


@app.post("/api/trade")
async def trade(req: TradeRequest) -> dict[str, Any]:
    """Execute one algorithm trade and return resulting state."""
    return sim.trade(req.algo, req.side, req.action)


@app.post("/api/new-coin")
async def new_coin_compat() -> dict[str, Any]:
    """Compatibility endpoint for resetting the coin process."""
    sim.reset_coin()
    return sim.state()


@app.post("/api/flip-coin")
async def flip_coin_compat() -> dict[str, Any]:
    """Compatibility endpoint for a settling coin toss."""
    return sim.event_toss()
