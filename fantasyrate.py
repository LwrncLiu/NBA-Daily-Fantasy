# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 17:20:54 2021

@author: lwrnc
"""


import pandas as pd
import json
import urllib3

game_id = '0022000735'

def fantasyUsageRate(game_id):
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
        subs = df[[tag, 'PERIOD', 'EVENTNUM', 'INDEX']]
        subs['SUB'] = tag
        subs.columns = ['PLAYER_ID', 'PERIOD', 'EVENTNUM', 'INDEX', 'SUB']
        return subs
        
    frame = extract_data(play_by_play_url(game_id))
    frame['INDEX'] = frame.index
    substitutionsOnly = frame[frame["EVENTMSGTYPE"] == 8][['PERIOD', 'EVENTNUM', 'PLAYER1_ID', 'PLAYER2_ID','INDEX']]
    substitutionsOnly.columns = ['PERIOD', 'EVENTNUM', 'OUT', 'IN','INDEX']
    subs_in = split_subs(substitutionsOnly, 'IN')
    subs_out = split_subs(substitutionsOnly, 'OUT')
    full_subs = pd.concat([subs_out, subs_in], axis=0).reset_index()[['PLAYER_ID', 'PERIOD', 'EVENTNUM', 'INDEX','SUB']]
    first_event_of_period = full_subs.loc[full_subs.groupby(by=['PERIOD', 'PLAYER_ID'])['INDEX'].idxmin()]
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
    
    #players for boxscore traditional
    boxscore = extract_data(advanced_boxscore_url(game_id))
    teams = boxscore['TEAM_ABBREVIATION'].unique()
    home_players = list(boxscore[boxscore['TEAM_ABBREVIATION'] == teams[1]]['PLAYER_NAME'])
    away_players = list(boxscore[boxscore['TEAM_ABBREVIATION'] == teams[0]]['PLAYER_NAME'])
    
    home_desc = frame['HOMEDESCRIPTION'].tolist() #np array for columns of interest
    away_desc = frame['VISITORDESCRIPTION'].tolist()
    p1 = frame['PLAYER1_NAME'].tolist()
    p2 = frame['PLAYER2_NAME'].tolist()
    p3 = frame['PLAYER3_NAME'].tolist()
    event_type = frame['EVENTMSGTYPE'].tolist()
    
    #current lineup tracker
    def updateLineup(current_lineup, player, leave = False):
        if leave == False: current_lineup.append(player)
        else: current_lineup.remove(player)
        return current_lineup
    
    #fantasy points tracker
    def statsTracker(current_lineup, player_track, player, stat, ct = 1):
        p_record = player_track[player] 
        p_record[stat] += ct
        player_track.update({player:p_record})
        tm_stat = 'tm'+stat        
        for p in current_lineup: #update total points for each person in current_lineup
            t_record = player_track[p]
            t_record[tm_stat] += ct
            player_track.update({p:t_record})
        return player_track 
    
    h_values = [{'2pt':0,'3pt':0,'ft':0,'ast':0,'reb':0,'stl':0,'blk':0,'tov':0,
                 'tm2pt':0,'tm3pt':0,'tmft':0,'tmast':0,'tmreb':0,'tmstl':0,'tmblk':0,'tmtov':0} for i in range(len(home_players))] #create list of lists for dictionary values for both home and away teams
    home_track = dict(zip(home_players, h_values)) #initialize dictionary with player and values
    a_values = [{'2pt':0,'3pt':0,'ft':0,'ast':0,'reb':0,'stl':0,'blk':0,'tov':0,
                 'tm2pt':0,'tm3pt':0,'tmft':0,'tmast':0,'tmreb':0,'tmstl':0,'tmblk':0,'tmtov':0} for i in range(len(away_players))] 
    away_track = dict(zip(away_players, a_values))
    
    quarters = per_quarter_starters['PERIOD'].unique()
    for q in quarters: #looping through each quarter
        home_lineup = list(per_quarter_starters[(per_quarter_starters['PERIOD'] == q) & (per_quarter_starters['TEAM_ABBREVIATION'] == teams[1])]['PLAYER_NAME']) #update the quarter starting lineup for the home team
        away_lineup = list(per_quarter_starters[(per_quarter_starters['PERIOD'] == q) & (per_quarter_starters['TEAM_ABBREVIATION'] == teams[0])]['PLAYER_NAME']) #update the quarter starting lineup for the away team
        quarter_plays = frame[frame.PERIOD == q]
        for i in quarter_plays.index:
            if (home_desc[i] == None) and (away_desc[i] == None): pass #nothing happened
            else: #something happened
                home_event = home_desc[i] if home_desc[i] != None else "" 
                away_event = away_desc[i] if away_desc[i] != None else ""
                if event_type[i] == 8: #substitution
                    if home_event != "": #home team substitution   
                        home_lineup = updateLineup(updateLineup(home_lineup, p2[i]), p1[i], leave = True)
                    elif away_event != "": #away team substitution
                        away_lineup = updateLineup(updateLineup(away_lineup, p2[i]), p1[i], leave = True)
                        
                if home_event != "": #tracking home team stats
                    if (event_type[i] == 1):
                        if ('3PT' not in home_event): #2 pointer made, add 2 points to pts for p1
                            home_track = statsTracker(home_lineup, home_track, p1[i], stat = '2pt') 
                        if ('3PT' in home_event): #3 pointer made, add 3 points to pts for p1
                            home_track = statsTracker(home_lineup, home_track, p1[i], stat = '3pt') 
                        if ('AST' in home_event): #assist, add 1 count to ast for p2
                            home_track = statsTracker(home_lineup, home_track, p2[i], stat = 'ast')
                    if (event_type[i] == 3) and ('MISS' not in home_event): #free throw made, add 1 point to pts for p1
                        home_track = statsTracker(home_lineup, home_track, p1[i], stat = 'ft')
                    if (event_type[i] == 4) and (p1[i] != None): #rebound, add 1 count to reb for p1, this does not account for "team rebounds"
                        home_track = statsTracker(home_lineup, home_track, p1[i], stat = 'reb')
                    if event_type[i] == 5:
                        if 'STEAL' in home_event: #steal, add 1 count to stl for p2
                            home_track = statsTracker(home_lineup, home_track, p2[i], stat = 'stl')
                        if 'Turnover' in home_event: #turnover, add 1 count to tov for p1
                            if p1[i] != None: #if not a team turnover
                                home_track = statsTracker(home_lineup, home_track, p1[i], stat = 'tov')
                    if (event_type[i] == 2) and ('BLOCK' in home_event): #block, add 1 count to blk for p3
                        home_track = statsTracker(home_lineup, home_track, p3[i], stat = 'blk')
                if away_event != "": #tracking away team stats
                    if (event_type[i] == 1):
                        if ('3PT' not in away_event): #2 pointer made, add 2 points to pts for p1
                            away_track = statsTracker(away_lineup, away_track, p1[i], stat = '2pt') 
                        if ('3PT' in away_event): #3 pointer made, add 3 points to pts for p1
                            away_track = statsTracker(away_lineup, away_track, p1[i], stat = '3pt') 
                        if ('AST' in away_event): #assist, add 1 count to ast for p2
                            away_track = statsTracker(away_lineup, away_track, p2[i], stat = 'ast')
                    if (event_type[i] == 3) and ('MISS' not in away_event): #free throw made, add 1 point to pts for p1
                       away_track = statsTracker(away_lineup, away_track, p1[i], stat = 'ft')
                    if (event_type[i] == 4) and (p1[i] != None): #rebound, add 1 count to reb for p1, this does not account for "team rebounds"
                        away_track = statsTracker(away_lineup, away_track, p1[i], stat = 'reb')
                    if event_type[i] == 5:
                        if 'STEAL' in away_event: #steal, add 1 count to stl for p2
                            away_track = statsTracker(away_lineup, away_track, p2[i], stat = 'stl')
                        if 'Turnover' in away_event: #turnover, add 1 count to tov for p1
                            if p1[i] != None: #if not a team turnover
                                away_track = statsTracker(away_lineup, away_track, p1[i], stat = 'tov')
                    if (event_type[i] == 2) and ('BLOCK' in away_event): #block, add 1 count to blk for p2
                        away_track = statsTracker(away_lineup, away_track, p3[i], stat = 'blk')
    
    #usage rate calculation
    def calculateUsageRate(track):
        for player in track:
            p_dict = track[player]
            num = 2*p_dict['2pt'] + 3*p_dict['3pt'] + p_dict['ft'] + 1.5*p_dict['ast'] + 1.2*p_dict['reb'] + 3*p_dict['stl'] + 3*p_dict['blk'] #- p_dict['tov']
            den = 2*p_dict['tm2pt'] + 3*p_dict['tm3pt'] + p_dict['tmft'] + 1.5*p_dict['tmast'] + 1.2*p_dict['tmreb'] + 3*p_dict['tmstl'] + 3*p_dict['tmblk'] - p_dict['tmtov']
            p_dict['p_fp'] = round(num,1)
            p_dict['tm_fp'] = round(den,1)
            if den == 0:
                p_dict['usg'] = 0.0
            else: 
                p_dict['usg'] = round(100*(num/den),1)
            track.update({player:p_dict})
        return track
    
    home_track = calculateUsageRate(home_track)
    away_track = calculateUsageRate(away_track)
    return home_track, away_track

home,away = fantasyUsageRate('0022000798')
