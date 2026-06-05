from game_simulator import simulate_game
from nba_api.stats.endpoints import scheduleleaguev2

def simulate_season(data):
    schedule = get_schedule('2025-26')
    standings = {}

    for team_id in data: 
        standings[team_id] = {'wins': 0, 'losses': 0}

    for game in schedule:
        home_id = game['home_team_id']
        away_id = game['away_team_id']
        home_team = data[home_id]
        away_team = data[away_id]
        home_score, away_score = simulate_game(home_team, away_team, data)
        if home_score > away_score:
            standings[home_id]['wins'] += 1
            standings[away_id]['losses'] += 1
        else:
            standings[away_id]['wins'] += 1
            standings[home_id]['losses'] += 1

    return standings


def get_standings(results):
    pass

def simulate_playoffs(standings, data):
    pass

def get_schedule(season):
    schedule = scheduleleaguev2.ScheduleLeagueV2(season=season)
    df = schedule.get_data_frames()[0]
    
    df['gameId'] = df['gameId'].astype(str)
    regular = df[
        (df['homeTeam_teamId'] > 1610612000) & 
        (df['awayTeam_teamId'] > 1610612000) &
        (df['gameStatus'] == 3) &
        (df['gameId'].str.startswith('0022'))
    ]
    
    games = []
    for _, row in regular.iterrows():
        games.append({
            'home_team_id': row['homeTeam_teamId'],
            'away_team_id': row['awayTeam_teamId']
        })
    
    return games


# if __name__ == '__main__':
#     import sys
#     sys.path.append('../')
#     from data_fetcher import get_all_data
    
#     data = get_all_data('2025-26')
#     schedule = get_schedule('2025-26')
#     print(f"Total games: {len(schedule)}")
#     print(schedule[:3])


if __name__ == '__main__':
    import sys
    sys.path.append('../')
    from data_fetcher import get_all_data
    
    data = get_all_data('2025-26')
    standings = simulate_season(data)
    print(standings)