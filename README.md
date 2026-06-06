# NBA Distributed Season Simulator

Simulates the entire NBA season 1000 times in parallel to compute championship probabilities.

---

## What it does

Pulls real 2025-26 NBA stats, simulates all 1230 regular season games and the full playoffs, and counts who wins the championship across 1000 runs.

```
San Antonio Spurs:      40.3%
Milwaukee Bucks:        13.0%
Cleveland Cavaliers:    13.0%
Oklahoma City Thunder:   8.5%
```

---

## How the math works

### Monte Carlo

Run the season 1000 times. Count who wins most often. That is Monte Carlo. The name comes from the casino because it uses randomness.

### Shooting

Each shot is a random number between 0 and 1. If Shai shoots 55%, any number below 0.55 is a make. 55% of all numbers between 0 and 1 fall below 0.55, so he makes it 55% of the time. The stats make the dice weighted.

Both of these work identically:

```python
random.random() < 0.55  # makes it
random.random() < 0.45  # misses it
```

### Turnovers

We calculate how many possessions a player touches the ball per game:

```
possessions with ball = 100 x (minutes per game / 48) x usage rate
```

Then divide his turnovers per game by that:

```
turnover probability = turnovers per game / possessions with ball
```

Example for Shai (2 turnovers, 34 minutes, 32% usage):

```
possessions = 100 x (34/48) x 0.32 = 22.7
turnover probability = 2 / 22.7 = 8.8%
```

The formula is not just minutes times usage. You need to find what fraction of the game the player is on court first, then scale by team possessions, then by usage.

### Three point attempt rate

Each player has a real three point attempt rate:

```
three point rate = three point attempts per game / field goal attempts per game
```

Shaq has a rate near 0%. Steph is near 50%. The simulation reflects actual player tendencies instead of assuming everyone shoots threes at the same rate.

### Foul rate

Each player has a real foul rate based on their free throw data:

```
foul rate = free throw attempts per game / (field goal attempts per game x 2)
```

We divide by 2 because one foul gives 2 free throws. Shai draws a lot of fouls. A bench player who never gets to the line draws almost none.

### Defense

Every team has a defensive rating, which is points allowed per 100 possessions. Lower is better. League average is 114.7.

```
defensive modifier = opponent defensive rating / league average
```

Against the Thunder (106.5 defensive rating):

```
modifier = 106.5 / 114.7 = 0.928
```

A player's shooting percentage gets multiplied by 0.928. Good defenses make scoring harder.

### Offense

```
offensive modifier = team offensive rating / league average
```

Players on good offensive teams get a boost. Players on bad offensive teams get penalized. This helps balanced teams like the Knicks who do not have one dominant star.

### Home court advantage

Home teams win roughly 60% of games in the NBA. We model this as a 1% boost to the home team's final score.

```python
home_score = int(home_score * 1.01)
```

### Why player ID not player name

Two NBA players can share the same name. Player ID is unique for every player so we use that as the dictionary key.

---

## Data structure

```python
{
    1610612760: {
        'team_name': 'Oklahoma City Thunder',
        'off_rating': 117.6,
        'def_rating': 106.5,
        'pace': 100.37,
        'roster': [
            {
                'player_id': 1628983,
                'name': 'Shai Gilgeous-Alexander',
                'fg_pct': 0.519,
                'fg3_pct': 0.375,
                'ft_pct': 0.898,
                'usg_pct': 0.318,
                'min_pg': 34.2,
                'pts_pg': 31.1,
                'tov_pg': 2.4,
                'fga_pg': 17.8,
                'fg3a_pg': 5.3,
                'fta_pg': 8.1
            },
        ]
    },
}
```

---

## Why we use the real NBA schedule

We pull the actual 2025-26 schedule from the NBA API instead of generating a fake one. This means home and away assignments are accurate and back to backs are real. Generating a fake schedule would require implementing all NBA scheduling rules from scratch.

Regular season game IDs start with 0022. Playoff game IDs start with 0042. We filter to 0022 to get exactly 1230 regular season games.

---

## Playoff format

16 teams, 8 per conference, seeded by regular season wins. Each round is best of 7.

```
Round 1:  1v8, 2v7, 3v6, 4v5  (8 series)
Round 2:  winners play winners (4 series)
Round 3:  conference finals    (2 series)
Round 4:  NBA Finals           (1 series)
```

East and West conferences are hardcoded because they never change.

---

## Known limitations in V1

**No injury modeling.** Every player plays every game at their season average. The 2025-26 Bucks finished 11th in the East because Damian Lillard got injured early. The simulator does not know this and rates them too highly.

**No pass simulation.** Every possession ends with the selected player. In reality players pass and create shots for teammates. V2 could model this by chaining possession selections.

**No 5 man rotation modeling.** We select players from the full roster weighted by usage rate instead of simulating actual lineups. Players with low usage get selected less often, which approximates real rotations but is not exact. V2 could model actual lineups.

**Star player bias.** The simulator rewards individual stats heavily. Teams with one elite player like Wemby tend to be overrated. V2 with multi-season averaging would temper this.

---

## Architecture

```
nba_api (fetched once)
        |
        v
Redis cache (season data stored as JSON)
        |
        v
Celery (1000 simulation jobs dispatched)
        |
        v
10 parallel workers (each runs one full season)
        |
        v
PostgreSQL (each worker saves the champion)
        |
        v
FastAPI (serves championship probabilities)
        |
        v
HTML frontend (displays results)
```

---

## Benchmark

| Method | Time |
|---|---|
| Sequential (1 process) | 1559 seconds (26 minutes) |
| Distributed (10 workers) | 419 seconds (7 minutes) |
| Speedup | 3.7x |

Theoretical max with 10 workers is 10x. Real world is lower because of Redis overhead, job dispatch time, and Postgres write contention across concurrent workers.

---

## Tech stack

| Layer | Tool |
|---|---|
| Data source | nba_api |
| Cache | Redis |
| Task queue | Celery |
| Message broker | Redis |
| Database | PostgreSQL |
| API | FastAPI |
| Frontend | HTML |

---

## V1 vs V2

V1 uses current season stats and simulates the 2025-26 season.

V2 will add a stat projection layer. The user picks a future season. The system pulls 2-3 seasons of historical stats per player, uses an ML model with age curves to project future performance, and feeds those projections into the same V1 simulator. The simulation engine stays the same. Only the data layer changes.

---

## How to run

**Install dependencies:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install nba_api celery redis psycopg2-binary fastapi uvicorn pandas
```

**Set up the database:**

```bash
psql postgres -c "CREATE DATABASE nba_sim;"
python3 -c "from app.database.database import create_table; create_table()"
```

**Cache season data (run once):**

```bash
python3 -c "from app.simulation.data_fetcher import cache_data; cache_data('2025-26')"
```

**Start Redis:**

```bash
brew services start redis
```

**Start Celery workers:**

```bash
celery -A app.workers.tasks worker --loglevel=info
```

**Run 1000 simulations:**

```bash
python3 -c "
from celery import group
from app.workers.tasks import run_simulation
job_group = group(run_simulation.s('2025-26') for i in range(1000))
job_group.apply_async().get()
"
```

**Start the API:**

```bash
uvicorn app.api.api:app --reload
```

**View results:**

Open `http://localhost:8000/probabilities?season=2025-26` in a browser.