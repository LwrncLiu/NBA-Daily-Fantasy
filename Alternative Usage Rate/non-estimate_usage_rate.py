import pandas as pd
import json
import urllib3

#arbitrarily using Hawks at Spurs (April 1st, 2021) game. Went to Double Overtime o.O
game_id = '0022000735'

#header for API call
header_data = {
        'Host': 'stats.nba.com',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        'Referer': 'stats.nba.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    }

#endpoint calls for playbyplay and boxscoreadvancedv2
def play_by_play_url(game_id):
    return "https://stats.nba.com/stats/playbyplayv2/?gameId={0}&startPeriod=0&endPeriod=14".format(game_id)    
def advanced_boxscore_url(game_id, start=None, end=None):
    if (start != None) and (end != None):
        return "https://stats.nba.com/stats/boxscoreadvancedv2/?gameId={0}&startPeriod=0&endPeriod=14&startRange={1}&endRange={2}&rangeType=2".format(game_id, start, end)
    else:
        return "https://stats.nba.com/stats/boxscoreadvancedv2?EndPeriod=1&EndRange=0&GameID={}&RangeType=0&StartPeriod=1&StartRange=0".format(game_id)

#generate http client
http = urllib3.PoolManager()
#function for downlading and extracting data from endpoint
def extract_data(url):
    r = http.request('GET', url, headers=header_data)
    resp = json.loads(r.data)
    results = resp['resultSets'][0]
    headers = results['headers']
    rows = results['rowSet']
    frame = pd.DataFrame(rows)
    frame.columns = headers
    return frame

#function for calculating start time and end time of each period
def calculate_time_at_period(period):
    if period > 5:
        return (720 * 4 + (period - 5) * (5 * 60)) * 10
    else:
        return (720 * (period - 1)) * 10

#function to process players who are coming in and out during the quarter
def split_subs(df, tag):
    subs = df[[tag, 'PERIOD', 'EVENTNUM']]
    subs['SUB'] = tag
    subs.columns = ['PLAYER_ID', 'PERIOD', 'EVENTNUM', 'SUB']
    return subs

#extract play by play data
frame = extract_data(play_by_play_url(game_id))

#filter the play by play to only include substitution
substitutionsOnly = frame[frame["EVENTMSGTYPE"] == 8][['PERIOD', 'EVENTNUM', 'PLAYER1_ID', 'PLAYER2_ID']]
substitutionsOnly.columns = ['PERIOD', 'EVENTNUM', 'OUT', 'IN']
subs_in = split_subs(substitutionsOnly, 'IN')
subs_out = split_subs(substitutionsOnly, 'OUT')
full_subs = pd.concat([subs_out, subs_in], axis=0).reset_index()[['PLAYER_ID', 'PERIOD', 'EVENTNUM', 'SUB']]
first_event_of_period = full_subs.loc[full_subs.groupby(by=['PERIOD', 'PLAYER_ID'])['EVENTNUM'].idxmin()]
players_subbed_in_at_each_period = first_event_of_period[first_event_of_period['SUB'] == 'IN'][['PLAYER_ID', 'PERIOD', 'SUB']]
periods = players_subbed_in_at_each_period['PERIOD'].drop_duplicates().values.tolist()
frames = []

#calculate the start and end time of each quarter so that there is no collision at the start/end barrier between periods.
for period in periods:
    low = calculate_time_at_period(period) + 5
    high = calculate_time_at_period(period + 1) - 5
    boxscore = advanced_boxscore_url(game_id, low, high)
    boxscore_players = extract_data(boxscore)[['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ABBREVIATION']]
    boxscore_players['PERIOD'] = period
    players_subbed_in_at_period = players_subbed_in_at_each_period[players_subbed_in_at_each_period['PERIOD'] == period]
    joined_players = pd.merge(boxscore_players, players_subbed_in_at_period, on=['PLAYER_ID', 'PERIOD'], how='left')
    joined_players = joined_players[pd.isnull(joined_players['SUB'])][['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ABBREVIATION', 'PERIOD']]
    frames.append(joined_players)

per_quarter_starters = pd.concat(frames)

#separate players that belong to the home and away teams
boxscore = extract_data(advanced_boxscore_url(game_id))
teams = boxscore['TEAM_ABBREVIATION'].unique()
home_players = list(boxscore[boxscore['TEAM_ABBREVIATION'] == teams[1]]['PLAYER_NAME'])
away_players = list(boxscore[boxscore['TEAM_ABBREVIATION'] == teams[0]]['PLAYER_NAME'])

#convert columns of interests to list
home_desc = frame['HOMEDESCRIPTION'].tolist()
away_desc = frame['VISITORDESCRIPTION'].tolist() 
p1 = frame['PLAYER1_NAME'].tolist()
p2 = frame['PLAYER2_NAME'].tolist()
event_type = frame['EVENTMSGTYPE'].tolist()

#current lineup tracker
def updateLineup(current_lineup, player, leave = False):
    if leave == False: current_lineup.append(player)
    else: current_lineup.remove(player)
    return current_lineup

#fantasy points tracker
def statsTracker(current_lineup, player_track, player, stat):
    p_record = player_track[player] 
    p_record[stat] += 1
    player_track.update({player:p_record})
    tm_stat = 'tm'+stat        
    for p in current_lineup: #update total points for each person in current_lineup
        t_record = player_track[p]
        t_record[tm_stat] += 1
        player_track.update({p:t_record})
    return player_track 

#usage rate calculation
def calculateUsageRate(track):
    for player in track:
        p_dict = track[player]
        num = p_dict['fga'] + 0.44*p_dict['fta'] + p_dict['tov']
        den = p_dict['tmfga'] + 0.44*p_dict['tmfta'] + p_dict['tmtov']
        if den == 0:
            p_dict['usg'] = 0.0
        else: 
            p_dict['usg'] = str(round(100*(num/den),1))+'%'
        track.update({player:p_dict})
    return track

#initialize dictionaries for tracking individual stats and team stats while playing 
h_values = [{'fga':0,'fta':0,'tov':0,'tmfga':0,'tmfta':0,'tmtov':0} for i in range(len(home_players))]
home_track = dict(zip(home_players, h_values))
a_values = [{'fga':0,'fta':0,'tov':0,'tmfga':0,'tmfta':0,'tmtov':0} for i in range(len(away_players))] 
away_track = dict(zip(away_players, a_values))

quarters = per_quarter_starters['PERIOD'].unique()
for q in quarters: #looping through each quarter
    #update the quarter starting lineups for home and away teams
    home_lineup = list(per_quarter_starters[(per_quarter_starters['PERIOD'] == q) & (per_quarter_starters['TEAM_ABBREVIATION'] == teams[1])]['PLAYER_NAME'])
    away_lineup = list(per_quarter_starters[(per_quarter_starters['PERIOD'] == q) & (per_quarter_starters['TEAM_ABBREVIATION'] == teams[0])]['PLAYER_NAME'])
    quarter_plays = frame[frame.PERIOD == q]
    for i in quarter_plays.index: #looping through the plays in each quarter
        if (home_desc[i] == None) and (away_desc[i] == None): pass #nothing happened
        else: #something happened
            home_event = home_desc[i] if home_desc[i] != None else "" 
            away_event = away_desc[i] if away_desc[i] != None else ""
            if event_type[i] == 8: #substitution
                if home_event != "": #home team substitution    
                    home_lineup = updateLineup(updateLineup(home_lineup, p2[i]), p1[i], leave = True)
                if away_event != "": #away team substitution
                    away_lineup = updateLineup(updateLineup(away_lineup, p2[i]), p1[i], leave = True)
                    
            if (home_event != "") and (p1[i] in home_players): #tracking home team stats
                if (event_type[i] == 1) or (event_type[i] == 2): #FGA
                    home_track = statsTracker(home_lineup, home_track, p1[i], stat = 'fga') 
                elif event_type[i] == 3: #FTA
                    home_track = statsTracker(home_lineup, home_track, p1[i], stat = 'fta')
                elif event_type[i] == 5: #TOV
                    home_track = statsTracker(home_lineup, home_track, p1[i], stat = 'tov')
            if (away_event != "") and (p1[i] in away_players): #tracking away team stats
                if (event_type[i] == 1) or (event_type[i] == 2): #FGA
                    away_track = statsTracker(away_lineup, away_track, p1[i], stat = 'fga')
                elif event_type[i] == 3: #FTA
                    away_track = statsTracker(away_lineup, away_track, p1[i], stat = 'fta')
                elif event_type[i] == 5: #TOV
                    away_track = statsTracker(away_lineup, away_track, p1[i], stat = 'tov')

#calculate the usage rate for home and away teams
home_track = calculateUsageRate(home_track)
away_track = calculateUsageRate(away_track)
