import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from celery import Celery
from app.simulation.data_fetcher import load_data
from app.simulation.season_simulator import simulate_season, get_standings, simulate_playoffs
from app.database.database import save_simulation_result, create_table

app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@app.task
def run_simulation(season):
    data = load_data(season)
    standings = simulate_season(data)
    bracket = get_standings(standings)
    champion = simulate_playoffs(bracket, data)
    save_simulation_result(season, champion['team_name'])
    return champion['team_name']