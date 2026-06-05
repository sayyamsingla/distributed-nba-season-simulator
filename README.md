# NBA Distributed Season Simulator

A tool that simulates the entire NBA season 1000 times to predict who wins the championship.

## How the math works

### Shooting
Each shot is decided by a random number between 0 and 1. If Shai shoots 55% from the field, any random number below 0.55 means he makes it. 55% of all numbers between 0 and 1 fall below 0.55 so he makes it 55% of the time naturally. The real stats make the randomness realistic.

### Turnovers
A player's turnover probability per possession is calculated like this.

First we find how many possessions he touches the ball per game:

    possessions = 100 x (minutes per game / 48) x usage rate

Then we divide his turnovers per game by that number:

    turnover probability = turnovers per game / possessions with ball

For example Shai averages 2 turnovers, plays 34 minutes, and has a 32% usage rate:

    possessions = 100 x (34/48) x 0.32 = 22.7
    turnover probability = 2 / 22.7 = 8.8% per possession

### Defense
Every team has a defensive rating which is points allowed per 100 possessions. Lower is better. The league average is 114.7.

We use this to adjust shooting percentages based on the opponent:

    defensive modifier = opponent def rating / league average

For example playing against the Thunder who have a 106.5 defensive rating:

    modifier = 106.5 / 114.7 = 0.928

So a player's shooting percentage gets multiplied by 0.928, making it harder to score against a good defense.

### Why player ID and not player name
Two players in the NBA can share the same name. Player ID is unique for every player so we use that as the key instead.

### Data structure

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
                    'tov_pg': 2.4
                }
            ]
        }
    }

## Tech Stack

- Python
- Celery
- Redis
- PostgreSQL
- FastAPI
- React
