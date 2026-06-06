from nba_api.stats.endpoints import leaguedashplayerstats, leaguedashteamstats, commonteamroster
import time
import redis
import json

def get_player_stats(season):
    stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season)
    df = stats.get_data_frames()[0]

    advanced = leaguedashplayerstats.LeagueDashPlayerStats(season=season, measure_type_detailed_defense='Advanced')
    advanced_df = advanced.get_data_frames()[0]

    player_stats = {}
    for _, row in df.iterrows():
        player_id = row['PLAYER_ID']
        gp = row['GP']
        player_stats[player_id] = {
            'name': row['PLAYER_NAME'],
            'team_id': row["TEAM_ID"],
            'fg_pct': row['FG_PCT'],
            'fg3_pct': row['FG3_PCT'],
            'ft_pct': row['FT_PCT'],
            'tov_pg': round(row['TOV'] / gp) if gp > 0 else 0,
            'min_pg': round(row['MIN'] / gp) if gp > 0 else 0,
            'pts_pg': round(row['PTS'] / gp) if gp > 0 else 0,
            'fga_pg': round(row['FGA'] / gp, 2) if gp > 0 else 0,
            'fg3a_pg': round(row['FG3A'] / gp, 2) if gp > 0 else 0,
            'fta_pg': round(row['FTA'] / gp, 2) if gp > 0 else 0,
            'usg_pct': 0
        }

    for _, row in advanced_df.iterrows():
        player_id = row['PLAYER_ID']
        if player_id in player_stats:
            player_stats[player_id]['usg_pct'] = row['USG_PCT']

    return player_stats


def get_team_advanced_stats(season):
    stats = leaguedashteamstats.LeagueDashTeamStats(season=season, measure_type_detailed_defense='Advanced')
    df = stats.get_data_frames()[0]
    
    team_stats = {}
    for _, row in df.iterrows():
        team_id = row['TEAM_ID']
        team_stats[team_id] = {
            'team_name': row['TEAM_NAME'],
            'off_rating': row['OFF_RATING'],
            'def_rating': row['DEF_RATING'],
            'pace': row['PACE']
        }

    return team_stats

def get_team_roster(team_id):
   roster = commonteamroster.CommonTeamRoster(team_id=team_id)
   time.sleep(0.7)
   df = roster.get_data_frames()[0]
   player_ids = []

   for _, player in df.iterrows():
       player_ids.append(player['PLAYER_ID'])

   return player_ids


def get_all_data(season):
    data = {}
    player_stats = get_player_stats(season=season)
    teams_stats = get_team_advanced_stats(season=season)

    for team_id in teams_stats: 
        roster = get_team_roster(team_id)
        data[team_id] = teams_stats[team_id]
        data[team_id]['roster'] = [] 
        for player_id in roster:
            if player_id in player_stats:
                player = player_stats[player_id]
                player['player_id'] = player_id
                data[team_id]['roster'].append(player)
    return data


def cache_data(season):
    # fetch data from NBA API
    data = get_all_data(season)
    
    # connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    # save to Redis as JSON string
    r.set(f'nba_data_{season}', json.dumps(data))
    print(f"Data cached in Redis for season {season}")
    return data

def load_data(season):
    # connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    # load from Redis
    data = r.get(f'nba_data_{season}')
    
    if data is None:
        print("No cached data found, fetching from API...")
        return cache_data(season)
    
    return {int(k): v for k, v in json.loads(data).items()}

if __name__ == '__main__':
#     result = get_player_stats('2025-26')
#     result = get_team_advanced_stats('2025-26')
#     get_team_roster(1610612760)
    get_all_data('2025-26')
