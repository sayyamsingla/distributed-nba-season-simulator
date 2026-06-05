import random


def simulate_possession(player, team, opponent):
    possessions_with_ball = 100 * (player['min_pg'] / 48) * player['usg_pct']
    tov_prob = player['tov_pg'] / possessions_with_ball 

def simulate_game(home_team, away_team, data):
    pass

def simulate_playoffs(bracket, data):
    pass

def get_league_avg_def_rating(data):
    total = sum(team['def_rating'] for team in data.values())
    return total / len(data)


if __name__ == '__main__':
    import sys
    sys.path.append('../')
    from data_fetcher import get_all_data
    
    data = get_all_data('2025-26')
    avg = get_league_avg_def_rating(data)
    print("League avg def rating:", avg)