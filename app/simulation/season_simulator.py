from nba_api.stats.endpoints import scheduleleaguev2
from app.simulation.game_simulator import simulate_game

EAST_TEAMS = [
    1610612737,  # Atlanta Hawks
    1610612738,  # Boston Celtics
    1610612751,  # Brooklyn Nets
    1610612766,  # Charlotte Hornets
    1610612741,  # Chicago Bulls
    1610612739,  # Cleveland Cavaliers
    1610612765,  # Detroit Pistons
    1610612754,  # Indiana Pacers
    1610612748,  # Miami Heat
    1610612749,  # Milwaukee Bucks
    1610612752,  # New York Knicks
    1610612753,  # Orlando Magic
    1610612755,  # Philadelphia 76ers
    1610612761,  # Toronto Raptors
    1610612764,  # Washington Wizards
]

WEST_TEAMS = [
    1610612742,  # Dallas Mavericks
    1610612743,  # Denver Nuggets
    1610612744,  # Golden State Warriors
    1610612745,  # Houston Rockets
    1610612746,  # LA Clippers
    1610612747,  # LA Lakers
    1610612763,  # Memphis Grizzlies
    1610612750,  # Minnesota Timberwolves
    1610612740,  # New Orleans Pelicans
    1610612760,  # OKC Thunder
    1610612756,  # Phoenix Suns
    1610612757,  # Portland Trail Blazers
    1610612758,  # Sacramento Kings
    1610612759,  # San Antonio Spurs
    1610612762,  # Utah Jazz
]

def simulate_season(data, schedule=None):
    if schedule is None:
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


def get_standings(standings):
    east_standings = {}
    for team_id in EAST_TEAMS:
        if team_id in standings:
            east_standings[team_id] = standings[team_id]

    west_standings = {}
    for team_id in WEST_TEAMS:
        if team_id in standings:
            west_standings[team_id] = standings[team_id]

    sorted_east = sorted(east_standings, key=lambda x: east_standings[x]['wins'], reverse=True)
    sorted_west = sorted(west_standings, key=lambda x: west_standings[x]['wins'], reverse=True)

    return {
        'east': sorted_east,
        'west': sorted_west
    }


def simulate_series(team1, team2, data):
    team1_wins = 0
    team2_wins = 0
    
    while team1_wins < 4 and team2_wins < 4:
        # simulate one game
        # home court goes to higher seed (team1)
        home_score, away_score = simulate_game(team1, team2, data)
        if home_score > away_score:
            team1_wins += 1
        else:
            team2_wins += 1
    
    if team1_wins == 4:
        return team1
    else:
        return team2

def simulate_playoffs(bracket, data):
    # first round - 8 series
    east_first_round_winners = []
    west_first_round_winners = []
    
    # east first round: 1v8, 2v7, 3v6, 4v5
    matchups = [(0, 7), (1, 6), (2, 5), (3, 4)]
    for high_seed, low_seed in matchups:
        team1 = data[bracket['east'][high_seed]]
        team2 = data[bracket['east'][low_seed]]
        winner = simulate_series(team1, team2, data)
        east_first_round_winners.append(winner)
    
    # west first round: 1v8, 2v7, 3v6, 4v5
    for high_seed, low_seed in matchups:
        team1 = data[bracket['west'][high_seed]]
        team2 = data[bracket['west'][low_seed]]
        winner = simulate_series(team1, team2, data)
        west_first_round_winners.append(winner)
    
    # second round
    east_second_round_winners = []
    west_second_round_winners = []
    
    # east second round: 1v4 winner vs 2v3 winner, etc
    second_round_matchups = [(0, 3), (1, 2)]
    for high_seed, low_seed in second_round_matchups:
        winner = simulate_series(east_first_round_winners[high_seed], east_first_round_winners[low_seed], data)
        east_second_round_winners.append(winner)
    
    for high_seed, low_seed in second_round_matchups:
        winner = simulate_series(west_first_round_winners[high_seed], west_first_round_winners[low_seed], data)
        west_second_round_winners.append(winner)
    
    # conference finals
    east_champion = simulate_series(east_second_round_winners[0], east_second_round_winners[1], data)
    west_champion = simulate_series(west_second_round_winners[0], west_second_round_winners[1], data)
    
    # nba finals
    champion = simulate_series(east_champion, west_champion, data)
    
    return champion
    

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



def print_standings(standings, data):
    east_standings = {}
    for team_id in EAST_TEAMS:
        if team_id in standings:
            east_standings[team_id] = standings[team_id]

    west_standings = {}
    for team_id in WEST_TEAMS:
        if team_id in standings:
            west_standings[team_id] = standings[team_id]

    sorted_east = sorted(east_standings, key=lambda x: east_standings[x]['wins'], reverse=True)
    sorted_west = sorted(west_standings, key=lambda x: west_standings[x]['wins'], reverse=True)

    print("\n--- EASTERN CONFERENCE ---")
    for i, team_id in enumerate(sorted_east, 1):
        wins = standings[team_id]['wins']
        losses = standings[team_id]['losses']
        name = data[team_id]['team_name']
        print(f"{i}.) {name}: {wins}W - {losses}L")

    print("\n--- WESTERN CONFERENCE ---")
    for i, team_id in enumerate(sorted_west, 1):
        wins = standings[team_id]['wins']
        losses = standings[team_id]['losses']
        name = data[team_id]['team_name']
        print(f"{i}.) {name}: {wins}W - {losses}L")

if __name__ == '__main__':
    from app.simulation.data_fetcher import get_all_data

    data = get_all_data('2025-26')
    standings = simulate_season(data)
    bracket = get_standings(standings)
    champion = simulate_playoffs(bracket, data)
    print_standings(standings, data)
    print(f"Champion: {champion['team_name']}")