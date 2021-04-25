
import pandas as pd
from nba_api.stats.static import teams
import json
import urllib3

game_id = '0022000735' #game_id for test
team_dict = teams.get_teams()
hawks_team_id = [team for team in team_dict if team['nickname'] == 'Hawks'][0]['id']        #get team id from team dictionary
spurs_team_id = [team for team in team_dict if team['nickname'] == 'Spurs'][0]['id']        #get team id from team dictionary

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
    
def play_by_play_url(game_id):
    return "https://stats.nba.com/stats/playbyplayv2/?gameId={0}&startPeriod=0&endPeriod=14".format(game_id)
    
def advanced_boxscore_url(game_id, start=None, end=None):
    if (start != None) and (end != None):
        return "https://stats.nba.com/stats/boxscoreadvancedv2/?gameId={0}&startPeriod=0&endPeriod=14&startRange={1}&endRange={2}&rangeType=2".format(game_id, start, end)
    else:
        return "https://stats.nba.com/stats/boxscoreadvancedv2?EndPeriod=1&EndRange=0&GameID={}&RangeType=0&StartPeriod=1&StartRange=0".format(game_id)
    
http = urllib3.PoolManager()
    
def extract_data(url):
    r = http.request('GET', url, headers=header_data)
    resp = json.loads(r.data)
    results = resp['resultSets'][0]
    headers = results['headers']
    rows = results['rowSet']
    frame = pd.DataFrame(rows)
    frame.columns = headers
    return frame
        
def calculate_time_at_period(period):
    if period > 5:
        return (720 * 4 + (period - 5) * (5 * 60)) * 10
    else:
        return (720 * (period - 1)) * 10
    
def split_subs(df, tag):
    subs = df[[tag, 'PERIOD', 'EVENTNUM']]
    subs['SUB'] = tag
    subs.columns = ['PLAYER_ID', 'PERIOD', 'EVENTNUM', 'SUB']
    return subs
    
frame = extract_data(play_by_play_url(game_id))
substitutionsOnly = frame[frame["EVENTMSGTYPE"] == 8][['PERIOD', 'EVENTNUM', 'PLAYER1_ID', 'PLAYER2_ID']]
substitutionsOnly.columns = ['PERIOD', 'EVENTNUM', 'OUT', 'IN']
subs_in = split_subs(substitutionsOnly, 'IN')
subs_out = split_subs(substitutionsOnly, 'OUT')
full_subs = pd.concat([subs_out, subs_in], axis=0).reset_index()[['PLAYER_ID', 'PERIOD', 'EVENTNUM', 'SUB']]
first_event_of_period = full_subs.loc[full_subs.groupby(by=['PERIOD', 'PLAYER_ID'])['EVENTNUM'].idxmin()]
players_subbed_in_at_each_period = first_event_of_period[first_event_of_period['SUB'] == 'IN'][['PLAYER_ID', 'PERIOD', 'SUB']]
periods = players_subbed_in_at_each_period['PERIOD'].drop_duplicates().values.tolist()
frames = []
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

#starting players for boxscore traditional
boxscore = extract_data(advanced_boxscore_url(game_id))
teams = boxscore['TEAM_ABBREVIATION'].unique()
home_players = list(boxscore[boxscore['TEAM_ABBREVIATION'] == teams[1]]['PLAYER_NAME'])
away_players = list(boxscore[boxscore['TEAM_ABBREVIATION'] == teams[0]]['PLAYER_NAME'])

home_desc = frame['HOMEDESCRIPTION'].tolist() #np array for columns of interest
away_desc = frame['VISITORDESCRIPTION'].tolist()
p1 = frame['PLAYER1_NAME'].tolist()
p2 = frame['PLAYER2_NAME'].tolist()
p3 = frame['PLAYER3_NAME'].tolist()
score = frame['SCORE'].tolist()

#current lineup tracker
def updateLineup(current_lineup, player, leave = False):
    if leave == False: current_lineup.append(player)
    else: current_lineup.remove(player)
    return current_lineup

#fantasy points tracker
def pointsTracker(current_lineup, player_track, player, pts, neg = False):
    record = player_track[player] 
    if neg == False: record[0] += pts
    else: record[0] -= pts 
    player_track.update({player:record})        
    for p in current_lineup: #update total points for each person in current_lineup
        record = player_track[p]
        if neg == False: record[1] += pts
        else: record[1] -= pts
        player_track.update({p:record})
    return player_track 

h_values = [[0.0,0.0] for i in range(len(home_players))] #create list of lists for dictionary values for both home and away teams
home_track = dict(zip(home_players, h_values)) #initialize dictionary with player and values
a_values = [[0.0,0.0] for i in range(len(away_players))] 
away_track = dict(zip(away_players, a_values))
current_score = None

quarters = per_quarter_starters['PERIOD'].unique()
for q in quarters: #looping through each quarter
    home_lineup = list(per_quarter_starters[(per_quarter_starters['PERIOD'] == q) & (per_quarter_starters['TEAM_ABBREVIATION'] == teams[1])]['PLAYER_NAME']) #update the quarter starting lineup for the home team
    away_lineup = list(per_quarter_starters[(per_quarter_starters['PERIOD'] == q) & (per_quarter_starters['TEAM_ABBREVIATION'] == teams[0])]['PLAYER_NAME']) #update the quarter starting lineup for the away team
    quarter_plays = frame[frame.PERIOD == q]
    for i in quarter_plays.index:
        if (home_desc[i] == None) and (away_desc[i] == None): pass #nothing happened
        else: #something happened
            home_event = home_desc[i] if home_desc[i] != None else "" #looking for sub: keyword for substitution
            away_event = away_desc[i] if away_desc[i] != None else ""
            if ('SUB: ' in home_event): #home team substitution
                home_lineup = updateLineup(updateLineup(home_lineup, p2[i]), p1[i], leave = True)
            if ('SUB: ' in away_event): #away team substition
                away_lineup = updateLineup(updateLineup(away_lineup, p2[i]), p1[i], leave = True)
                    
            if (current_score != score[i]) and (score[i] != None): #if there is a score change, look for who scored... and who assisted
                if home_desc[i] != None:
                    if '3PT' in home_desc[i]:
                        home_track = pointsTracker(home_lineup, home_track, p1[i], pts = 3.5)
                    elif 'Free Throw' in home_desc[i]:
                        home_track = pointsTracker(home_lineup, home_track, p1[i], pts = 1)
                    else: 
                        home_track = pointsTracker(home_lineup, home_track, p1[i], pts = 2)
                    if 'AST' in home_desc[i]: #check if there's an assist
                        home_track = pointsTracker(home_lineup, home_track, p2[i], pts = 1.5)
                elif away_desc[i] != None:
                    if '3PT' in away_desc[i]:
                        away_track = pointsTracker(away_lineup, away_track, p1[i], pts = 3.5)
                    elif 'Free Throw' in away_desc[i]:
                        away_track = pointsTracker(away_lineup, away_track, p1[i], pts = 1)
                    else: 
                        away_track = pointsTracker(away_lineup, away_track, p1[i], pts = 2)
                    if 'AST' in away_desc[i]: #check if there's an assist
                        away_track = pointsTracker(away_lineup, away_track, p2[i], pts = 1.5)
                        
            if home_desc[i] != None: #tracking rebounds, steals, blocks, and turnovers for away team
                if 'REBOUND' in home_desc[i]:
                    home_track = pointsTracker(home_lineup, home_track, p1[i], pts = 1.25)
                elif 'STEAL' in home_desc[i]:
                    home_track = pointsTracker(home_lineup, home_track, p2[i], pts = 2)
                elif 'BLOCK' in home_desc[i]:
                    home_track = pointsTracker(home_lineup, home_track, p3[i], pts = 2)
                elif 'Turnover' in home_desc[i]:
                    home_track = pointsTracker(home_lineup, home_track, p1[i], pts = 0.5, neg = True)
            if away_desc[i] != None: #tracking rebounds, steals, blocks, and turnovers for away team
                if 'REBOUND' in away_desc[i]:
                    away_track = pointsTracker(away_lineup, away_track, p1[i], pts = 1.25)
                elif 'STEAL' in away_desc[i]:
                    away_track= pointsTracker(away_lineup, away_track, p2[i], pts = 2)
                elif 'BLOCK' in away_desc[i]:
                    away_track = pointsTracker(away_lineup, away_track, p3[i], pts = 2)
                elif 'Turnover' in away_desc[i]:
                    away_track = pointsTracker(away_lineup, away_track, p1[i], pts = 0.5, neg = True)
            current_score = score[i] if score[i] != None else current_score #update current score


def calculateFantasyRate(track):
    for player in track:
        record = track[player]
        if record[1] == 0.0: 
            record.append(0.0)
            track.update({player: record})
        else:
            record.append(record[0]/record[1])
            track.update({player: record})
    return track

home_track = calculateFantasyRate(home_track)