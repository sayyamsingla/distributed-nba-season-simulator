from celery import Celery
import sys
sys.path.append('../')
from simulation.data_fetcher import get_all_data
from simulation.season_simulator import simulate_season, get_standings, simulate_playoffs


# create the Celery app
# broker = Redis (where jobs wait)
# backend = Redis (where results are stored temporarily)

app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@app.task
def run_simulation(season):
    data = get_all_data(season)
    standings = simulate_season(data)
    bracket = get_standings(standings)
    champion = simulate_playoffs(bracket, data)
    return champion['team_name']