import asyncio
import json
import redis
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.database.database import (
    clear_simulations,
    get_championship_probabilities,
    save_simulation_result,
)
from app.simulation.data_fetcher import load_data
from app.simulation.season_simulator import (
    get_schedule,
    get_standings,
    simulate_playoffs,
    simulate_season,
)

app = FastAPI()

STATIC_DIR = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/probabilities")
def get_probabilities(season: str = "2025-26"):
    results = get_championship_probabilities(season)
    total = sum(count for _, count in results)
    if total == 0:
        return {"probabilities": {}, "simulations": 0, "season": season}
    probabilities = {
        champion: round(count / total * 100, 1)
        for champion, count in results
    }
    return {"probabilities": probabilities, "simulations": total, "season": season}


def _load_schedule_cached(season: str) -> list:
    r = redis.Redis(host="localhost", port=6379, db=0)
    cached = r.get(f"nba_schedule_{season}")
    if cached:
        return json.loads(cached)
    schedule = get_schedule(season)
    safe = [
        {"home_team_id": int(g["home_team_id"]), "away_team_id": int(g["away_team_id"])}
        for g in schedule
    ]
    r.set(f"nba_schedule_{season}", json.dumps(safe))
    return safe


def _run_batch(data: dict, schedule: list, season: str, batch_size: int) -> None:
    for _ in range(batch_size):
        standings = simulate_season(data, schedule)
        bracket = get_standings(standings)
        champion = simulate_playoffs(bracket, data)
        save_simulation_result(season, champion["team_name"])


@app.get("/simulate/stream")
async def simulate_stream(n: int = 100, season: str = "2025-26"):
    async def event_stream():
        try:
            yield f"data: {json.dumps({'status': 'loading'})}\n\n"

            data = await asyncio.to_thread(load_data, season)
            schedule = await asyncio.to_thread(_load_schedule_cached, season)

            yield f"data: {json.dumps({'status': 'clearing'})}\n\n"
            await asyncio.to_thread(clear_simulations, season)

            batch_size = max(1, n // 50)
            completed = 0

            while completed < n:
                this_batch = min(batch_size, n - completed)
                await asyncio.to_thread(_run_batch, data, schedule, season, this_batch)
                completed += this_batch
                progress = round(completed / n * 100, 1)
                payload = json.dumps({
                    "status": "running",
                    "progress": progress,
                    "completed": completed,
                    "total": n,
                })
                yield f"data: {payload}\n\n"

            results = get_championship_probabilities(season)
            total = sum(c for _, c in results)
            probs = {
                champ: round(cnt / total * 100, 1) for champ, cnt in results
            }
            yield f"data: {json.dumps({'status': 'done', 'probabilities': probs, 'simulations': total, 'season': season})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
