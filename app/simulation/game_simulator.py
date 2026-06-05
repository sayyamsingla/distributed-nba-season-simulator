import random
from data_fetcher import get_all_data

# V1 assumptions - can be tuned in V2
FOUL_SHOT_PENALTY_THREE = 0.05   # shooting % drops to 5% of normal on fouled three
FOUL_SHOT_PENALT_REGULAR = 0.25  # shooting % drops to 25% of normal on fouled two

def simulate_possession(player, team, opponent, league_avg_def):
    # calculate how many possessions this player touches the ball per game
    possessions_with_ball = 100 * (player['min_pg'] / 48) * player['usg_pct']
    
    # turnover probability = turnovers per game / possessions with ball
    tov_prob = player['tov_pg'] / possessions_with_ball
    
    # check for turnover first - if turnover, possession is over with 0 points
    if random.random() < tov_prob: 
        return 0
    
    # defensive modifier - good defenses reduce shooting percentage
    # lower def_rating = better defense = modifier below 1 = harder to score
    defensive_modifier = opponent['def_rating'] / league_avg_def
    adjusted_fg_pct = player['fg_pct'] * defensive_modifier
    adjusted_fg3_pct = player['fg3_pct'] * defensive_modifier
    
    # shooting percentage when fouled drops significantly
    fouled_fg3_pct = adjusted_fg3_pct * FOUL_SHOT_PENALTY_THREE
    fouled_fg_pct = adjusted_fg_pct * FOUL_SHOT_PENALT_REGULAR
    
    # foul rate per shot attempt = free throw attempts / (field goal attempts * 2)
    # multiply fga by 2 because one foul gives 2 free throws
    foul_rate = player['fta_pg'] / (player['fga_pg'] * 2) if player['fga_pg'] > 0 else 0 

    # decide if this is a three point attempt based on player's real attempt rate
    # e.g. Shaq almost never shoots threes, Steph attempts threes ~50% of the time
    three_point_rate = player['fg3a_pg'] / player['fga_pg'] if player['fga_pg'] > 0 else 0 
    is_three = random.random() < three_point_rate

    if is_three:     
        if random.random() < foul_rate:
            # fouled on a three - shooting % drops to 5% of normal
            if random.random() < fouled_fg3_pct: 
               # made the shot while fouled - four point play
               if random.random() < player['ft_pct']:
                return 4  # made three + made free throw
               else: 
                return 3  # made three + missed free throw
            else: 
                # missed the shot while fouled - shoot 3 free throws
                total_count = 0
                for i in range(3):
                    if random.random() < player['ft_pct']:
                        total_count += 1
                return total_count
        else: 
            # no foul - regular three point attempt
            if random.random() < adjusted_fg3_pct: 
               return 3
            else: 
               return 0 
    else: 
        if random.random() < foul_rate: 
            # fouled on a two - shooting % drops to 25% of normal
            if random.random() < fouled_fg_pct:
                # made the shot while fouled - shoot 1 free throw
                if random.random() < player['ft_pct']:
                    return 3  # made two + made free throw
                else: 
                    return 2  # made two + missed free throw
            else: 
                # missed the shot while fouled - shoot 2 free throws
                total_count = 0
                for i in range(2):
                    if random.random() < player['ft_pct']:
                        total_count += 1
                return total_count
        else:
            # no foul - regular two point attempt
            if random.random() < adjusted_fg_pct: 
               return 2
            else: 
               return 0
    
    

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
    league_avg_def = get_league_avg_def_rating(data)
    
    # get OKC and their opponent BOS
    okc = data[1610612760]
    bos = data[1610612738]
    
    # get Shai
    shai = next(p for p in okc['roster'] if p['name'] == 'Shai Gilgeous-Alexander')
    
    # # simulate 10 possessions
    # for i in range(100):
    #     points = simulate_possession(shai, okc, bos, league_avg_def)
    #     print(f"Possession {i+1}: {points} points")
    total = sum(simulate_possession(shai, okc, bos, league_avg_def) for _ in range(100))
    print(f"Total points in 100 possessions: {total}")
    print(f"Points per possession: {total / 100}")

# if __name__ == '__main__':
#     import sys
#     sys.path.append('../')
#     from data_fetcher import get_all_data
    
#     data = get_all_data('2025-26')
#     avg = get_league_avg_def_rating(data)
#     print("League avg def rating:", avg)





    # assumption
# FOUL_SHOT_PENALTY_THREE = 0.05
# FOUL_SHOT_PENALT_REGULAR = 0.25

# def simulate_possession(player, team, opponent, league_avg_def):
#     possessions_with_ball = 100 * (player['min_pg'] / 48) * player['usg_pct']
#     tov_prob = player['tov_pg'] / possessions_with_ball
#     if random.random() < tov_prob: 
#         return 0
#     defensive_modifier = opponent['def_rating']/ league_avg_def
#     adjusted_fg_pct = player['fg_pct'] * defensive_modifier
#     adjusted_fg3_pct = player['fg3_pct'] * defensive_modifier
#     fouled_fg3_pct = adjusted_fg3_pct * FOUL_SHOT_PENALTY_THREE
#     fouled_fg_pct = adjusted_fg_pct * FOUL_SHOT_PENALT_REGULAR
#     foul_rate = player['fta_pg'] / (player['fga_pg'] * 2) if player['fga_pg'] > 0 else 0 


#     three_point_rate = player['fg3a_pg'] / player['fga_pg'] if player['fga_pg'] > 0 else 0 
#     is_three = random.random() < three_point_rate

    
#     if is_three:     
#         if random.random() < foul_rate:
#             if random.random() < fouled_fg3_pct: 
#                if random.random() < player['ft_pct']:
#                 return 4
#                else: 
#                 return 3
#             else: 
#                 total_count = 0
#                 for i in range(3):
#                     if random.random() < player['ft_pct']:
#                         total_count += 1
#                 return total_count
#         else: 
#             if random.random() < adjusted_fg3_pct: 
#                return 3
#             else: 
#                return 0 
#     else: 
#         if random.random() < foul_rate: 
#             if random.random() < fouled_fg_pct:
#                 if random.random() < player['ft_pct']:
#                     return 3
#                 else: 
#                     return 2
#             else: 
#                 total_count = 0
#                 for i in range(2):
#                     if random.random() < player['ft_pct']:
#                         total_count += 1
#                 return total_count
#         else:
#             if random.random() < adjusted_fg_pct: 
#                return 2
#             else: 
#                return 0 

# import random
# from data_fetcher import get_all_data