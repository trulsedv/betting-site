from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.simulator import Simulator, TradeRequest


app = FastAPI(title="Betting Site")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
sim = Simulator()


@app.get("/")
async def root():
    return FileResponse("app/static/index.html")


@app.get("/api/state")
async def get_state():
    return sim.state()


@app.post("/api/reset")
async def reset():
    sim.reset_coin()
    return sim.state()


@app.post("/api/toss")
async def toss_coin():
    return sim.event_toss()


@app.post("/api/test-toss")
async def test_toss():
    return sim.test_toss()


@app.post("/api/event-toss")
async def event_toss():
    return sim.event_toss()


@app.post("/api/trade")
async def trade(req: TradeRequest):
    return sim.trade(req.algo, req.side, req.action)


@app.post("/api/new-coin")
async def new_coin_compat():
    sim.reset_coin()
    return sim.state()


@app.post("/api/flip-coin")
async def flip_coin_compat():
    return sim.event_toss()
