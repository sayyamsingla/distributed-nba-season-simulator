from nba_api.stats.endpoints import leaguedashplayerstats, leaguedashteamstats, commonteamroster
from nba_api.stats.static import teams
import pandas as pd

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
            'usg_pct': 0
        }

    for _, row in advanced_df.iterrows():
        player_id = row['PLAYER_ID']
        if player_id in player_stats:
            player_stats[player_id]['usg_pct'] = row['USG_PCT']

    # for key in player_stats.keys(): 
    #     print(f"Key: {key}, Player stats: {player_stats[key]} \n")

    return player_stats


def get_team_advanced_stats(season):
    pass

def get_team_roster(team_id):
    pass

def get_all_data(season):
    pass

if __name__ == '__main__':
    result = get_player_stats('2025-26')
    # print(result)