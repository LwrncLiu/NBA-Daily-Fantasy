# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 14:44:17 2020

@author: lwrnc
"""
import numpy as np
import pandas as pd
from itertools import combinations
import matplotlib.pyplot as plt
import seaborn as sns
import math
import matplotlib.style as style 
from operator import add
import statistics
from nba_api.stats.static import teams
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.library.parameters import SeasonAll
from nba_api.stats.endpoints import leaguegamelog
from ipywidgets import IntProgress, HBox, Label
from IPython.display import display, clear_output
import time
import random
import requests
from datetime import datetime
from datetime import date
from collections import Counter
from fpdf import FPDF
import scipy.stats as sc


pd.options.mode.chained_assignment = None

#this function contains the acronyms of the nba teams for some naming conventions
def teamAcronym(team):
    acronym = {'Hawks':'ATL', 'Nets':'BKN', 'Celtics':'BOS', 'Hornets':'CHA', 'Bulls':'CHI',
               'Cavaliers':'CLE', 'Mavericks':'DAL', 'Nuggets':'DEN', 'Pistons':'DET', 'Warriors':'GSW',
               'Rockets':'HOU', 'Pacers':'IND', 'Clippers':'LAC', 'Lakers':'LAL', 'Grizzlies':'MEM',
               'Heat':'MIA', 'Bucks':'MIL', 'Timberwolves':'MIN', 'Pelicans':'NOP', 'Knicks':'NYK',
               'Thunder':'OKC', 'Magic':'ORL', '76ers':'PHI', 'Suns':'PHX', 'Trail Blazers':'POR',
               'Kings':'SAC', 'Spurs':'SAS', 'Raptors':'TOR', 'Jazz':'UTA', 'Wizards':'WAS'}
    return acronym[team]

#This function contains the dictionary of all the nba teams.
def colorScheme(team):
    colors = {'Lakers1':'#552583','Lakers2':'#FDB927','Clippers1':'#C8102E','Clippers2':'#1D428A','Hawks1':'#E03A3E','Hawks2':'#C1D32F','Celtics1':'#007A33','Celtics2':'#BA9653', 
          'Nets1':'#000000','Nets2':'#FFFFFF','Hornets1':'#1D1160','Hornets2':'#00788C','Bulls1':'#CE1141','Bulls2':'#000000','Cavaliers1':'#860038','Cavaliers2':'#FDBB30',
          'Mavericks1':'#00538C','Mavericks2':'#002B5E','Nuggets1':'#0E2240','Nuggets2':'#FEC524','Pistons1':'#C8102E','Pistons2':'#BEC0C2','Warriors1':'#1D428A','Warriors2':'#FFC72C',
          'Rockets1':'#CE1141','Rockets2':'#000000','Pacers1':'#002D62','Pacers2':'#FDBB30','Grizzlies1':'#5D76A9','Grizzlies2':'#12173F','Heat1':'#98002E','Heat2':'#F9A01B',
          'Bucks1':'#00471B','Bucks2':'#EEE1C6','Timberwolves1':'#0C2340','Timberwolves2':'#78BE20','Pelicans1':'#0C2340','Pelicans2':'#C8102E','Knicks1':'#006BB6','Knicks2':'#F58426',
          'Thunder1':'#007AC1','Thunder2':'#EF3B24','Magic1':'#0077C0','Magic2':'#C4CED4','76ers1':'#006BB6','76ers2':'#ED174C','Suns1':'#1D1160','Suns2':'#E56020',
          'Trail Blazers1':'#E03A3E','Trail Blazers2':'#000000','Kings1':'#5A2D81','Kings2':'#63727A','Spurs1':'#C4CED4','Spurs2':'#000000','Raptors1':'#CE1141','Raptors2':'#000000',
          'Jazz1':'#002B5C','Jazz2':'#00471B','Wizards1':'#002B5C','Wizards2':'#E31837'}
    key1 = team+'1'
    key2 = team+'2'
    return colors[key1], colors[key2]

def detailedColorScheme(team):
    colors = {'Lakers1a':'#2e1447','Lakers1b':'#481f6f','Lakers1c':'#622b97','Lakers1d':'#7c36bf','Lakers2':'#FDB927','Clippers1a':'#810a1e','Clippers1b':'#b00e29','Clippers1c':'#e01233','Clippers1d':'#ef3654','Clippers2':'#1D428A',
              'Hawks1a':'#b21c20','Hawks1b':'#dd2428','Hawks1c':'#e35054','Hawks1d':'#ea7c7f','Hawks2':'#C1D32F','Celtics1a':'#002e13','Celtics1b':'#006128','Celtics1c':'#00943e','Celtics1d':'#00c753','Celtics2':'#BA9653', 
              'Nets1a':'#000000','Nets1b':'#242323','Nets1c':'#3A3939','Nets1d':'#616161','Nets2':'#FFFFFF','Hornets1a':'#09051f','Hornets1b':'#160d4a','Hornets1c':'#241576','Hornets1d':'#311da1','Hornets2':'#00788C',
              'Bulls1a':'#870b2b','Bulls1b':'#b60f3a','Bulls1c':'#e61348','Bulls1d':'#ef3d6a','Bulls2':'#000000','Cavaliers1a':'#3a0018','Cavaliers1b':'#6d002d','Cavaliers1c':'#a00043','Cavaliers1d':'#d30058','Cavaliers2':'#FDBB30',
              'Mavericks1a':'#002640','Mavericks1b':'#004473','Mavericks1c':'#0062a6','Mavericks1d':'#0080d9','Mavericks2':'#002B5E','Nuggets1a':'#000101','Nuggets1b':'#09172b','Nuggets1c':'#132d55','Nuggets1d':'#1c437f','Nuggets2':'#FEC524',
              'Pistons1a':'#810a1e','Pistons1b':'#b00e29','Pistons1c':'#e01233','Pistons1d':'#ef3654','Pistons2':'#BEC0C2','Warriors1a':'#10244b','Warriors1b':'#193875','Warriors1c':'#214c9f','Warriors1d':'#2a60c9','Warriors2':'#FFC72C','Rockets1a':'#870b2b','Rockets1b':'#b60f3a','Rockets1c':'#e61348','Rockets1d':'#ef3d6a','Rockets2':'#000000',
              'Pacers1a':'#000a16','Pacers1b':'#002149','Pacers1c':'#00397c','Pacers1d':'#0050af','Pacers2':'#FDBB30','Grizzlies1a':'#405379','Grizzlies1b':'#526a9a','Grizzlies1c':'#6e84b2','Grizzlies1d':'#8fa0c4','Grizzlies2':'#12173F',
              'Heat1a':'#4c0017','Heat1b':'#7f0026','Heat1c':'#b20036','Heat1d':'#e50045','Heat2':'#F9A01B','Bucks1a':'#000000','Bucks1b':'#002e11','Bucks1c':'#006125','Bucks1d':'#009438','Bucks2':'#EEE1C6',
              'Timberwolves1a':'#000000','Timberwolves1b':'#08172b','Timberwolves1c':'#102f55','Timberwolves1d':'#184680','Timberwolves2':'#78BE20','Pelicans1a':'#000000','Pelicans1b':'#08172b','Pelicans1c':'#102f55','Pelicans1d':'#184680','Pelicans2':'#C8102E',
              'Knicks1a':'#003e6a','Knicks1b':'#005c9d','Knicks1c':'#007ad0','Knicks1d':'#0397ff','Knicks2':'#F58426','Thunder1a':'#004a75','Thunder1b':'#006aa8','Thunder1c':'#008adb','Thunder1d':'#0fa7ff','Thunder2':'#EF3B24',
              'Magic1a':'#004874','Magic1b':'#0067a7','Magic1c':'#0087da','Magic1d':'#0ea3ff','Magic2':'#C4CED4','76ers1a':'#003e6a','76ers1b':'#005c9d','76ers1c':'#007ad0','76ers1d':'#0397ff','76ers2':'#ED174C',
              'Suns1a':'#09051f','Suns1b':'#160d4a','Suns1c':'#241576','Suns1d':'#311da1','Suns2':'#E56020','Trail Blazers1a':'#b21c20','Trail Blazers1b':'#dd2428','Trail Blazers1c':'#e35054','Trail Blazers1d':'#ea7c7f','Trail Blazers2':'#000000',
              'Kings1a':'#321948','Kings1b':'#4d266e','Kings1c':'#673494','Kings1d':'#8241ba','Kings2':'#63727A','Spurs1a':'#000000','Spurs1b':'#242323','Spurs1c':'#3A3939','Spurs1d':'#616161','Spurs2':'#C4CED4',
              'Raptors1a':'#870b2b','Raptors1b':'#b60f3a','Raptors1c':'#e61348','Raptors1d':'#ef3d6a','Raptors2':'#000000','Jazz1a':'#000710','Jazz1b':'#001f43','Jazz1c':'#003776','Jazz1d':'#004fa9','Jazz2':'#F9A01B',
              'Wizards1a':'#000710','Wizards1b':'#001f43','Wizards1c':'#003776','Wizards1d':'#004fa9','Wizards2':'#E31837'}
    key1a = team+'1a'
    key1b = team+'1b'
    key1c = team+'1c'
    key1d = team+'1d'
    key2 = team+'2'
    return colors[key1a], colors[key1b], colors[key1c], colors[key1d], colors[key2]

#pulls the data of the team from a "relational database"
def getTeamData(team):
    #get current roster of the team
    url = 'Teams/'+team+'.csv'
    df = pd.read_csv(url)
    df.head()
    players = np.array(df['Player'])
    #from boxscore, get the statistics of each player
    boxscore = pd.read_csv('Teams/Box Scores.csv', index_col = 0)
    team_boxscore = pd.DataFrame(columns = ['Starter','Date','Versus','MP','FG','FGA','FG%','3P','3PA','3P%','FT','FTA','FT%','ORB','DRB','TRB','AST','STL','BLK','TOV','PF','PTS','+/-'])
    for i in players:
        player_boxscore = boxscore.loc[boxscore.index == i]
        team_boxscore = pd.concat([team_boxscore, player_boxscore])
    return team_boxscore

def getHistoricTeamData(team):
    box_score = pd.read_csv('Teams/Box Scores.csv', index_col = 0)
    team_boxscore = box_score[box_score['Team'] == team]
    return team_boxscore


#this function gets the minutes played of a player from the string format stored in the dataframe
def getMinutesPlayed(df):
    mp = []
    for i in range(len(df)):
        time = df['MP'][i]
        if len(time) > 4:
            minutes = float(time[:2])
            seconds = float(time[3:5])
        else:
            minutes = float(time[0])
            seconds = float(time[-2:])
        sec_cov = float(round(seconds/60, 2))
        tot = minutes + sec_cov
        mp.append(tot)
    df['MP1'] = mp
    return df

#this function calculates the usage rate give a dataframe of basic box scores
def usageRate(df):
    box_score = pd.read_csv('Teams/Box Scores.csv', index_col = 0)
    players = df.index.unique()
    count = 1
    for i in players:
        games = df[df.index == i]  
        usg_rate = []
        for j in range(len(games['Date'])):
            game = box_score[(box_score['Date'] == games['Date'][j])&(box_score['Versus'] == games['Versus'][j])&(box_score['Team'] == games['Team'][j])]
            player_perf = box_score[(box_score['Date'] == games['Date'][j])&(box_score['Versus'] == games['Versus'][j])&(box_score['Team'] == games['Team'][j])&(box_score.index == i)]
            player_perf = getMinutesPlayed(player_perf)
            p_fga = player_perf['FGA']
            p_fta = player_perf['FTA']
            p_tov = player_perf['TOV']
            p_mp = player_perf['MP1']

            tm_fga = sum(game['FGA'])
            tm_fta = sum(game['FTA'])
            tm_tov = sum(game['TOV'])
            num = (p_fga + 0.44*p_fta + p_tov)*48
            den = p_mp*(tm_fga + 0.44*tm_fta + tm_tov)
            p_usg = float(round(100*num/den,1))
            usg_rate.append(p_usg)
        games['USG%'] = usg_rate
        if count == 1:
            df1 = games
            count += 1 
        else:
            df1 = pd.concat([df1, games])
    return df1

#this function calculates the assist rate of a player given a dataframe of basic box scores
def assistRate(df):
    box_score = pd.read_csv('Teams/Box Scores.csv', index_col = 0)
    players = df.index.unique()
    count = 1
    for i in players:
        games = df[df.index == i]
        ast_rate = []
        for j in range(len(games['Date'])):
            game = box_score[(box_score['Date'] == games['Date'][j])&(box_score['Versus'] == games['Versus'][j])&(box_score['Team'] == games['Team'][j])]
            player_perf = box_score[(box_score['Date'] == games['Date'][j])&(box_score['Versus'] == games['Versus'][j])&(box_score['Team'] == games['Team'][j])&(box_score.index == i)]
            player_perf = getMinutesPlayed(player_perf)
            tm_fg = sum(game['FG'])
            p_ast = player_perf['AST']
            p_mp = player_perf['MP1']
            p_fg = player_perf['FG']
            den = (p_mp/48)*tm_fg - p_fg
            rate = float(round(100*(p_ast/den),1))
            ast_rate.append(rate)
        games['AST%'] = ast_rate
        if count == 1:
            df1 = games
            count += 1
        else:
            df1 = pd.concat([df1, games])
    return df1

#this function calculates the total rebound rate of a player given a dataframe of basic box scores and the team of interest
def reboundRate(df):
    box_score = pd.read_csv('Teams/Box Scores.csv', index_col = 0)
    players = df.index.unique()
    count = 1
    for i in players:
        games = df[df.index == i]
        trb_rate = []
        for j in range(len(games['Date'])):
            game = box_score[(box_score['Date'] == games['Date'][j])&(box_score['Versus'] == games['Versus'][j])&(box_score['Team'] == games['Team'][j])]
            opp_game = box_score[(box_score['Date'] == games['Date'][j])&(box_score['Versus'] == games['Team'][j])&(box_score['Team'] == games['Versus'][j])]
            player_perf = box_score[(box_score['Date'] == games['Date'][j])&(box_score['Versus'] == games['Versus'][j])&(box_score['Team'] == games['Team'][j])&(box_score.index == i)]
            player_perf = getMinutesPlayed(player_perf)
            p_trb = player_perf['TRB']
            p_mp = player_perf['MP1']
            tm_trb = sum(game['TRB'])
            opp_trb = sum(opp_game['TRB'])
            num = p_trb*48
            den = p_mp*(tm_trb + opp_trb)
            trb_r = float(round(100*(num/den),1))
            trb_rate.append(trb_r)
        games['TRB%'] = trb_rate
        if count == 1:
            df1 = games
            count += 1
        else:
            df1 = pd.concat([df1, games])
    return df1

#function to calculate DFS points given a dataset of performances
def fantasyPoints(df):
    
    #calculating fantasy points
    pts_list = list(df['PTS'])
    trb_list = list(df['REB'])
    ast_list = list(df['AST'])
    stl_list = list(df['STL'])
    blk_list = list(df['BLK'])
    f3m_list = list(df['FG3M'])
    try:
        tov_list = list(df['TOV'])
    except:
        tov_list = list(df['TO'])
    
    fp_list = []
    
    for i in range(len(df.index)):
        count = 0
        #stats
        points = pts_list[i]
        ct_trb = trb_list[i]
        ct_ast = ast_list[i]
        ct_stl = stl_list[i]
        ct_blk = blk_list[i]
        #point calculation
        three_pointers = f3m_list[i]*0.5
        rebounds = (ct_trb)*1.25 
        assists = (ct_ast)*1.5
        steals= (ct_stl)*2
        blocks = (ct_blk)*2
        turnovers = tov_list[i]*0.5
        mainstats = [points, ct_trb, ct_ast, ct_stl, ct_blk]
        count = points + three_pointers + rebounds + assists + steals + blocks
        count -= turnovers
        #double-double
        #print(mainstats)
        if sum(1 for j in mainstats if j >= 10) >= 2:
            count += 1.5
        #triple-double
        if sum(1 for j in mainstats if j >= 10) >= 3:
            count += 3
        fp_list.append(count)
    df['FP'] = fp_list
    return df

def fantasyPointsFD(df):
    
    #calculating fantasy points
    f3m_list = list(df['FG3M'])
    fgm_list = list(df['FGM'])
    ftm_list = list(df['FTM'])
    trb_list = list(df['REB'])
    ast_list = list(df['AST'])
    blk_list = list(df['BLK'])
    stl_list = list(df['STL'])
    try:
        tov_list = list(df['TOV'])
    except:
        tov_list = list(df['TO'])
    fp_list = []
    
    for i in range(len(df.index)):
        count = 0
        #count of each stat
        f3m = f3m_list[i]
        f2m = fgm_list[i] - f3m_list[i]
        ftm = ftm_list[i]
        ct_trb = trb_list[i]
        ct_ast = ast_list[i]
        ct_blk = blk_list[i]
        ct_stl = stl_list[i]
        ct_tov = tov_list[i]
        
        #point calculation of each stats
        three_pointers = f3m * 3
        two_pointers = f2m * 2
        free_throw = ftm * 1
        rebounds = ct_trb*1.2 
        assists = ct_ast*1.5
        steals= ct_stl*3
        blocks = ct_blk*3
        turnovers = ct_tov*1
        count = three_pointers + two_pointers + free_throw + rebounds + assists + steals + blocks - turnovers

        fp_list.append(count)
    df['FP'] = fp_list
    return df

#using nba api
def teamData(team_name):
    team_dict = teams.get_teams()
    team_id = [team for team in team_dict if team['nickname'] == team_name][0]['id']
    team_roster = commonteamroster.CommonTeamRoster(team_id = team_id).get_data_frames()[0]
    team_roster_id = list(team_roster['PLAYER_ID'])
    max_count = len(team_roster_id)
    f = IntProgress(min = 0, max = max_count, bar_style = 'success')
    bar = (HBox([Label('Loading Player Data:'), f]))
    display(bar)
    team_career = pd.DataFrame()
    for i in team_roster_id:
        player_career = playergamelog.PlayerGameLog(player_id = i, season = SeasonAll.all).get_data_frames()[0]
        team_career = team_career.append(player_career)
        time.sleep(0.5) #pause to avoid timeout error?
        f.value += 1
    clear_output()
    max_count_c = len(team_career['Player_ID'])
    c = IntProgress(min = 0, max = max_count_c, bar_style = 'success')
    bar1 = (HBox([Label('Calculating Player Data:'), c]))
    display(bar1)
    player_names = []
    for p in team_career['Player_ID']:
        player = team_roster[team_roster['PLAYER_ID'] == p]['PLAYER'].to_string().split('    ',1)[1]
        player_names.append(player)
        c.value += 1
    team_career['Player'] = player_names
    team_career = team_career.set_index('Player')
    team_season = team_career[team_career['SEASON_ID'] == '22020']
    clear_output()
    return team_season, team_career


#function breaks down fantasy points by category for visualizations
def categoryFantasyPoints(df):
    #creating DFS column
    if 'FP' in df.columns:
        pass
    else:
        df = fantasyPoints(df)
    
    pts_fp = []
    reb_fp = []
    ast_fp = []
    otr_fp = []
    
    pts_list = list(df['PTS'])
    fg3m_list = list(df['FG3M'])
    trb_list = list(df['REB'])
    ast_list = list(df['AST'])
    fp_list = list(df['FP'])

    #calculating fantasy points
    for i in range(len(df.index)):
        pts_count = 0
        #point calculation
        points = pts_list[i]*1
        three_pointers = fg3m_list[i]*0.5
        pts_count = points + three_pointers
        pts_fp.append(pts_count)
        
        rebounds = trb_list[i]*1.25
        reb_fp.append(rebounds)
        
        assists = ast_list[i]*1.5
        ast_fp.append(assists)
        
        main = pts_count + rebounds + assists
        
        other = fp_list[i] - main
        otr_fp.append(other)
        
    df['PTS FP'] = pts_fp
    df['REB FP'] = reb_fp
    df['AST FP'] = ast_fp
    df['OTR FP'] = otr_fp
    return df

def categoryFantasyPointsFD(df):
    #creating DFS column
    if 'FP' in df.columns:
        pass
    else:
        df = fantasyPointsFD(df)

    df['PTS FP'] = ""
    df['REB FP'] = ""
    df['AST FP'] = ""
    df['OTR FP'] = ""
    
    f3m_list = list(df['FG3M'])
    fgm_list = list(df['FGM'])
    ftm_list = list(df['FTM'])
    trb_list = list(df['REB'])
    ast_list = list(df['AST'])
    fp_list = list(df['FP'])
    
    pts_fp = []
    trb_fp = []
    ast_fp = []
    otr_fp = []
    #calculating fantasy points
    for i in range(len(df.index)):
        #calculate FP from points
        f3m = f3m_list[i]
        f2m = fgm_list[i] - f3m_list[i]
        ftm = ftm_list[i]
        
        ct_trb = trb_list[i]
        ct_ast = ast_list[i]
        
        points = f3m*3 + f2m*2 + ftm*1
        rebounds = ct_trb*1.2
        assists = ct_ast*1.5
        main = points + rebounds + assists
        other = fp_list[i] - main
        
        pts_fp.append(points)
        trb_fp.append(rebounds)
        ast_fp.append(assists)
        otr_fp.append(other)
        
    df['PTS FP'] = pts_fp
    df['REB FP'] = trb_fp
    df['AST FP'] = ast_fp
    df['OTR FP'] = otr_fp
    
    return df

def Reverse(lst): 
    return [ele for ele in reversed(lst)] 

#this function compares the predicted draft data points to the actual draft datapoints
def compare(dfp, dfr):
    dfr = nameInconsistency(dfr)
    dfp['Actual FP'] = ""

    for i in dfp.index:
        #finding actual results of points
        tot_pts = 0

        #captain points
        cpt = dfp['CPT'][i]
        cpt_pts = 1.5*float(dfr[dfr.index == cpt]['FP'])
        #utility player points
        ut1 = dfp['UTIL1'][i]
        ut1_pts = float(dfr[dfr.index == ut1]['FP'])
        ut2 = dfp['UTIL2'][i]
        ut2_pts = float(dfr[dfr.index == ut2]['FP'])
        ut3 = dfp['UTIL3'][i]
        ut3_pts = float(dfr[dfr.index == ut3]['FP'])
        ut4 = dfp['UTIL4'][i]
        ut4_pts = float(dfr[dfr.index == ut4]['FP'])
        ut5 = dfp['UTIL5'][i]
        ut5_pts = float(dfr[dfr.index == ut5]['FP'])

        tot_pts = (cpt_pts + ut1_pts + ut2_pts + ut3_pts + ut4_pts + ut5_pts)

        dfp['Actual FP'][i] = tot_pts
    dfp['Actual FP'] = dfp['Actual FP'].astype(float)

    return dfp

# this function generates lineups for the DraftKings showdown game mode given a captain, pool of players and df of player & salary
def lineupCombinations(captain, pool, dfs):
    #creates the pool without the captain
    cpt = np.array(captain)
    arr = np.setdiff1d(pool, cpt)
    
    #initialize empty array
    draft = np.empty([1,8])
    
    #combinations of 5 from pool not including the captain
    comb = combinations(arr, 5)
    
    #create a dictionary with player salary key-pair and player fp key-paid
    plys = list(dfs.index.unique())
    sals = list(dfs['Salary'])
    sea_fp = list(dfs['AvgPointsPerGame'])
    sal_dict = dict(zip(plys, sals))
    sea_fp_dict = dict(zip(plys, sea_fp))
    
    #looping through all the combinations
    for i in list(comb):
        #tuple to contain captain = utility players
        newi = (captain,) + i
        
        #find total salary of tuple and remove if it exceeds $50000 and more than $40000
        tot_salary = 0
        cpt_salary = 1.5*sal_dict[captain]
        tot_salary += cpt_salary
        for k in i:
            util_salary = sal_dict[k]
            tot_salary += util_salary
        if ((tot_salary < 50000) and (tot_salary > 40000)):
            sali = newi + (tot_salary,)
            tot_pts = 0
            cpt_pts = 1.5*sea_fp_dict[captain]
            tot_pts += cpt_pts
            for j in i:
                util_pts = sea_fp_dict[j]
                tot_pts += util_pts
            
            #tuple to contain lineup and season average fantasy poitns
            sali = sali + (tot_pts,)
            draft = np.vstack((draft,sali))
    
    df = pd.DataFrame(draft, columns = ['CPT','UTIL1','UTIL2','UTIL3','UTIL4','UTIL5','Salary','Season FP'])
    return df[1:]

# this function generates all lineup combinations for all captain combinations 
def generateLineups(pool, draft):
    column_names = ['CPT','UTIL1','UTIL2','UTIL3','UTIL4','UTIL5','Salary','Season FP']
    df = pd.DataFrame(columns = column_names)
    for i in pool:
        captain = i
        df_temp = lineupCombinations(captain, pool, draft)
        df = df.append(df_temp)
    return df

#given a dataframe of lineups and a list of up to 4 players, the function returns a dataframe with lineups containing all 4 players
def filterLineups(player_filter,df):
    num = len(player_filter)
    if num >= 1 and num <= 4:
        temp = np.empty([1,9]) 
        if num == 1:
            p1 = player_filter[0]
            for index, row in df.iterrows():
                a = row.str.contains(p1, regex = False)
                if a.any():
                    temp = np.vstack((temp,row))
        
        elif num == 2:
            p1 = player_filter[0]
            p2 = player_filter[1]
            for index, row in df.iterrows():
                a = row.str.contains(p2, regex = False)
                if a.any():
                    b = row.str.contains(p1, regex = False)
                    if b.any():
                        temp = np.vstack((temp,row))
                        
        elif num == 3:
            p1 = player_filter[0]
            p2 = player_filter[1]
            p3 = player_filter[2]
            for index, row in df.iterrows():
                a = row.str.contains(p2, regex = False)
                if a.any():
                    b = row.str.contains(p1, regex = False)
                    if b.any():
                        c = row.str.contains(p3, regex = False)
                        if c.any():
                            temp = np.vstack((temp,row))
        else:
            p1 = player_filter[0]
            p2 = player_filter[1]
            p3 = player_filter[2]
            p4 = player_filter[3]
            for index, row in df.iterrows():
                a = row.str.contains(p2, regex = False)
                if a.any():
                    b = row.str.contains(p1, regex = False)
                    if b.any():
                        c = row.str.contains(p3, regex = False)
                        if c.any():
                            d = row.str.contains(p4, regex = False)
                            if d.any():
                                temp = np.vstack((temp,row))
        
        df_filtered = pd.DataFrame({'CPT': temp[1:, 0], 
                                 'UTIL1': temp[1:, 1], 
                                 'UTIL2': temp[1:, 2], 
                                 'UTIL3': temp[1:, 3], 
                                 'UTIL4': temp[1:, 4], 
                                 'UTIL5': temp[1:, 5], 
                                 'Salary': temp[1:, 6], 
                                 'Expected DFS': temp[1:, 7], 
                                 'STD': temp[1:, 8]})
        df_filtered['Expected DFS'] = df_filtered['Expected DFS'].astype(float)
        df_filtered['Salary'] = df_filtered['Salary'].astype(float)
        
        return df_filtered
    else: 
        return print('Can only filter up to 4 players')

#calculates the standard deviation and value of players based on ppast performances       
def dfsDistribution(boxscore, draft):
    draft['STD'] = ""

    for i in draft.index:
        pstd = (boxscore.loc[boxscore.index == i]['FP']).std()    
        draft.loc[draft.index == i, 'STD'] = pstd 
    return draft

def predictedOwnership(df):
    pred = []
    for i in range(len(df)):
        p_pred = -15.8374 + 2*df['DK FP'][i]
        pred.append(p_pred)
    df['PRED_OWN'] = pred
    return df

def nameInconsistency(df):
    df.rename(index = {'Juan Hernangómez':'Juancho Hernangomez','Gary Trent':'Gary Trent Jr.','Nikola Vučević':'Nikola Vucevic','Bojan Bogdanović':'Bojan Bogdanovic','Timothé Luwawu-Cabarrot':'Timothe Luwawu-Cabarrot','Derrick Jones':'Derrick Jones Jr.','Bogdan Bogdanović':'Bogdan Bogdanovic','Kristaps Porziņģis':'Kristaps Porzingis','Tomáš Satoranský':'Tomas Satoransky','Otto Porter':'Otto Porter Jr.','Dennis Schröder':'Dennis Schroder','Wendell Carter':'Wendell Carter Jr.','Troy Brown':'Troy Brown Jr.','Dāvis Bertāns': 'Davis Bertans','Marcus Morris':'Marcus Morris Sr.','Sviatoslav Mykhailiuk':'Svi Mykhailiuk','Dario Šarić':'Dario Saric','J.J. Redick':'JJ Redick','Nicolò Melli':'Nicolo Melli','Larry Nance':'Larry Nance Jr.','Jonas Valančiūnas': 'Jonas Valanciunas','Luka Dončić':'Luka Doncic','Goran Dragić':'Goran Dragic','P.J. Washington': 'PJ Washington','Kelly Oubre':'Kelly Oubre Jr.','Jusuf Nurkić': 'Jusuf Nurkic', 'Michael Porter':'Michael Porter Jr.', 'Nikola Jokić':'Nikola Jokic','Marvin Bagley': 'Marvin Bagley III', 'Danuel House': 'Danuel House Jr.','Tim Hardaway':'Tim Hardaway Jr.', 'Boban Marjanović':'Boban Marjanovic'}, inplace = True)
    return df

def dfsSMA(boxscore,draft):
    sma_10 = []
    for i in draft.index:
        p_perf = list(boxscore.loc[boxscore.index == i]['FP'])
        if len(p_perf) < 10:
            p_avg = draft.loc[draft.index == i]['DK FP']
        else:
            p_avg = sum(p_perf[len(p_perf)-10:])/10
        p_avg = float(round(p_avg, 2))
        sma_10.append(p_avg)
    draft['10SMA FP'] = sma_10
    return draft

#assign home and away column to df from nba api
def homeaway(df):
    venue_list = []
    for i in df['MATCHUP']:
        venue = i.split()[1]
        if venue == '@':
            p = 'Away'
        else:
            p = 'Home'
        venue_list.append(p)
    df['HomeAway'] = venue_list
    return df

#matchup summary from nba api
def matchupSummary(team, opp_team):
    df_season, df_career = teamData(team)
    team_dict = teams.get_teams()
    opp_acr = [team for team in team_dict if team['nickname'] == opp_team][0]['abbreviation']
    df_season = homeaway(df_season)
    df_season = fantasyPoints(df_season)
    df_career = fantasyPoints(df_career)
    players = df_season.index.unique()
    data = []
    for p in players:
        p_season = df_season.loc[df_season.index == p]
        p_career = df_career.loc[df_career.index == p]

        p_season_fp = round(p_season['FP'].mean(),1)  #grab their season average
        p_season_hfp = round(p_season.loc[p_season['HomeAway'] == 'Home']['FP'].mean(),1)    #grab season home performance
        p_season_afp = round(p_season.loc[p_season['HomeAway'] == 'Away']['FP'].mean(),1)    #grab season away performance
        p_career_fp = round(p_career['FP'].mean(),1)    #grab their career average
        p_last_10_fp = round(p_season['FP'][:10].mean(),1)    #grab their last 10 average

        #grab their average versus this team
        opp_list = []
        for i in range(len(p_career['MATCHUP'])):
            if p_career['MATCHUP'][i].split()[2] == opp_acr:
                opp_list.append(p_career['FP'][i])
        if len(opp_list) == 0: p_opp_fp = 'NaN'
        else: p_opp_fp = round(sum(opp_list)/len(opp_list),1)
        data.append([p, p_last_10_fp, p_season_fp, p_season_hfp, p_season_afp, p_opp_fp, p_career_fp])
        
    team_summary = pd.DataFrame(data, columns = ['Player', 'Last 10', 'Season', 'Home', 'Away', 'Versus', 'Career'])
    team_summary = team_summary.set_index('Player').sort_values('Season', ascending = False)
    
    return team_summary

#this function is the first step in creating lineups it pulls in the draftkings imported given a home team, away team, and the day
def draftMerge(away_team, home_team, date):
    #a list of players on both rosters
    team_dict = teams.get_teams()
    team_id_a = [team for team in team_dict if team['nickname'] == away_team][0]['id']
    team_id_b = [team for team in team_dict if team['nickname'] == home_team][0]['id']
    team_roster_a = list(commonteamroster.CommonTeamRoster(team_id = team_id_a).get_data_frames()[0]['PLAYER'])
    team_roster_b = list(commonteamroster.CommonTeamRoster(team_id = team_id_b).get_data_frames()[0]['PLAYER'])
    for p in team_roster_b:
        team_roster_a.append(p)
    
    #importing the csv file from and adjusting columns
    h_acr = teamAcronym(home_team)
    a_acr = teamAcronym(away_team)
    draft_url = 'Games/' + date + '/' + a_acr + 'at' + h_acr + '_' + date + '.csv'
    #importing the player's salary for showdown mode from Draft Kings
    draft = pd.read_csv(draft_url, index_col = 2)
    draft.drop(columns = {'Game Info', 'Name + ID', 'ID'}, inplace = True)
    draft = draft[draft['Roster Position'] != 'CPT']

    #return both the draft and the list of players
    return draft, team_roster_a
 
#attaches the player performance standard deviaion to the salary dataframe       
def performanceDistribution(draft, poss):
    draft['CPP'] = ""
    draft['Adj DFS'] = ""
    draft['DFS STD'] = ""
    draft['Salary'].apply(lambda x: float(x))
    poss['Adj DFS'].apply(lambda x: float(x))

    for i in draft.index:
        cost = draft.loc[draft.index == i,'Salary']
        exp_dfs = poss.loc[poss.index == i, 'Adj DFS']
        exp_cpp = (exp_dfs/cost)*1000
        draft.loc[draft.index == i, 'CPP'] = exp_cpp[0]
        draft.loc[draft.index == i, 'Adj DFS'] = poss.loc[poss.index == i, 'Adj DFS']
        draft.loc[draft.index == i, 'DFS STD'] = poss.loc[poss.index == i, 'DFS STD']
    return draft

#this function returns a dataframe that is compatible with the .corr() pandas function
#The function takes in one argument, a team's box score.
def boxscoretoCorrelation(bx):
    bx = fantasyPoints(bx)

    players = bx.index.unique()
    dates = bx.Date.unique()
    players

    test = np.zeros(shape =(len(dates),len(players)))

    row_count = 0
    for i in dates:
        col_count = 0
        for j in players:
            try:
                performance = bx.loc[(bx.index == j) & (bx['Date'] == i), 'DFS'].astype(float)
                value = performance[0]
            except:
                value = 'nan'
                #print(performance)
            test[row_count][col_count] = value
            col_count += 1
        row_count += 1
    df = pd.DataFrame(data = test, columns = players)
    df['Dates'] = dates
    df = df.set_index('Dates')
    return df

def gamePerformanceCorrelation(team1, team2):
    style.use('seaborn-darkgrid')

    title1 = team1 + ' Player Correlation'
    title2 = team2 + ' Player Correlation'

    team_1 = getTeamData(team1)
    team_2 = getTeamData(team2)
    
    df1 = boxscoretoCorrelation(team_1)
    df2 = boxscoretoCorrelation(team_2)
    
    mask1 = np.zeros_like(df1.corr())
    mask1[np.triu_indices_from(mask1)] = True
    mask2 = np.zeros_like(df2.corr())
    mask2[np.triu_indices_from(mask2)] = True
    
    plt.figure(figsize = (10,20))
    plt.subplot(2,1,1)
    sns.heatmap(df1.corr(), mask = mask1, square = True, linewidths = .5, cmap = 'coolwarm')
    plt.title(title1)

    plt.subplot(2,1,2)
    sns.heatmap(df2.corr(), mask = mask2, square = True, linewidths = .5, cmap = 'coolwarm')
    plt.title(title2)

def teamPerformanceCorrelation(team):
    style.use('seaborn-darkgrid')

    title = team + ' Player Correlation'

    df = getTeamData(team)
    
    df = boxscoretoCorrelation(df)
    
    mask = np.zeros_like(df.corr())
    mask[np.triu_indices_from(mask)] = True
        
    plt.figure(figsize = (10,10))
    sns.heatmap(df.corr(), mask = mask, square = True, linewidths = .5, cmap = 'coolwarm')
    #sns.color_palette("#552583", as_cmap=True)

    plt.title(title)

#this function graphs the last 6 performances ofa player
#this function also calculates the 5-game simple moving average of player performances
def teamPerformance(team):
    color1, color2 = colorScheme(team)
    style.use('seaborn-darkgrid')
    df = getTeamData(team)
    df = fantasyPoints(df)

    players = df.index.unique()
    sig_players = []
    for i in players:
        gp = len(df.loc[df.index == i]['Date'])
        if gp > 3:
            sig_players.append(i)

    num_row = math.ceil(len(sig_players)/3)

    plt_count = 1
    plt.figure(figsize = (25,8*num_row))
    for i in sig_players:
        title = i + ' DFS Performance & Moving Average'
        perf = df[df.index == i]['DFS']
        games_played = df[df.index == i]['Date']
        avg = []
        for j in range(len(perf)):
            if j < 10:
                float_avg = sum(perf[:j+1])/(j+1)
            else:
                float_avg = sum(perf[j-9:j+1])/10
            avg.append(float_avg)

        plt.subplot(num_row,3,plt_count)
        sns.barplot(x = games_played[-10:], y = perf[-10:], color = color1)
        plt.plot(games_played[-10:],avg[-10:], marker = 'o', color = color2, linewidth = 3)
        plt.ylim(top = 80)
        plt.xticks(rotation=315)
        plt.title(title, fontsize = 12)

        plt_count += 1
        
#returns the detailed chart of a team's fantasy points performance over their last 10 games
def graphDetailedTeamPerformance(team):
    #color scheme of the graph, dependent on the team
    color1a,color1b,color1c,color1d,color2 = detailedColorScheme(team)
    style.use('seaborn-darkgrid')
    
    #grabs the season 
    df_season, df_career = teamData(team)
    
    df_season = categoryFantasyPoints(df_season)
    sig_players = df_season.index.unique()
    max_count = len(sig_players)
    g = IntProgress(min = 0, max = max_count, bar_style = 'success')
    bar = (HBox([Label('Graphing Player Data:'), g]))
    display(bar)
    num_row = math.ceil(len(sig_players)/2)
    plt_count = 1
    plt.figure(figsize = (15,9*num_row))
    for i in sig_players:
        g.value += 1
        title = i + ' DFS Performance & Moving Average'
        perf = Reverse(df_season[df_season.index == i]['FP'])
        pts = Reverse(df_season[df_season.index == i]['PTS FP'])
        ast = Reverse(df_season[df_season.index == i]['AST FP'])
        trb = Reverse(df_season[df_season.index == i]['REB FP'])
        otr = Reverse(df_season[df_season.index == i]['OTR FP'])
        games_played = Reverse(df_season[df_season.index == i]['GAME_DATE'])
        avg = []
        for j in range(len(perf)):
            if j < 10:
                float_avg = sum(perf[:j+1])/(j+1)
            else:
                float_avg = sum(perf[j-9:j+1])/10
            avg.append(float_avg)        
        b2 = np.add(pts[-10:], ast[-10:])
        b3 = np.add(b2, trb[-10:])        
        plt.subplot(num_row,2,plt_count)
        sns.barplot(x = games_played[-10:], y = pts[-10:], color = color1a, label = 'points')
        sns.barplot(x = games_played[-10:], y = ast[-10:], bottom = pts[-10:], color = color1b, label = 'assists')
        sns.barplot(x = games_played[-10:], y = trb[-10:], bottom = b2, color = color1c, label = 'rebounds')
        sns.barplot(x = games_played[-10:], y = otr[-10:], bottom = b3, color = color1d, label = 'other')    
        plt.plot(games_played[-10:],avg[-10:], marker = 'o', color = color2, linewidth = 3, label = 'mov_avg')
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.09),ncol=5, fancybox=True, shadow=True)    
        plt.title(title, fontsize = 12)
        plt.xticks(rotation=315, fontsize = 8)
        plt.ylim(top = 90)
        plt.ylabel('Total FP')
        plt_count += 1
    clear_output()


#for backtesting
def detailedTeamPerformanceBT(team, date_cutoff):
    color1a,color1b,color1c,color1d,color2 = detailedColorScheme(team)
    style.use('seaborn-darkgrid')
    url = 'Teams/' + team + '/' + team + ' Box Score.csv'
    df = pd.read_csv(url, index_col = 0)
    df = categoryFantasyPoints(df)
    players = df.index.unique()
    sig_players = []
    #num_games = len(df['Date'].unique())
    for i in players:
        gp = len(df.loc[df.index == i]['Date'])
        if gp > 3:
            sig_players.append(i)

    num_row = math.ceil(len(sig_players)/3)

    plt_count = 1
    plt.figure(figsize = (25,9*num_row))
    for i in sig_players:
        title = i + ' DFS Performance & Moving Average'
        dates = df[df.index == i]['Date'].unique()
        try:
            cut = np.where(dates == date_cutoff)[0]
            cut = int(cut)
        except:
            cut = len(dates)
        games_played = df[df.index == i]['Date'][:cut]

        perf = df[df.index == i]['DFS'][:cut]
        pts = df[df.index == i]['PTS DFS'][:cut]
        ast = df[df.index == i]['AST DFS'][:cut]
        trb = df[df.index == i]['TRB DFS'][:cut]
        otr = df[df.index == i]['OTR DFS'][:cut]
        avg = []
        for j in range(len(perf)):
            if j < 10:
                float_avg = sum(perf[:j+1])/(j+1)
            else:
                float_avg = sum(perf[j-9:j+1])/10
            avg.append(float_avg)
        
        b2 = np.add(pts[-10:], ast[-10:])
        b3 = np.add(b2, trb[-10:])
        
        plt.subplot(num_row,3,plt_count)
        sns.barplot(x = games_played[-10:], y = pts[-10:], color = color1a, label = 'points')
        sns.barplot(x = games_played[-10:], y = ast[-10:], bottom = pts[-10:], color = color1b, label = 'assists')
        sns.barplot(x = games_played[-10:], y = trb[-10:], bottom = b2, color = color1c, label = 'rebounds')
        sns.barplot(x = games_played[-10:], y = otr[-10:], bottom = b3, color = color1d, label = 'other')
        

        plt.plot(games_played[-10:],avg[-10:], marker = 'o', color = color2, linewidth = 3, label = 'mov_avg')
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1),ncol=5, fancybox=True, shadow=True)    

        plt.title(title, fontsize = 12)
        plt.xticks(rotation=315)
        plt.ylim(top = 80)
        plt.ylabel('Total DFS')
        plt_count += 1
        
#requires 3 positional arguments. player. team. date cutoff (for backtesting primarily)       
def detailedPlayerPerformanceBT(player, team, date_cutoff):
    color1a,color1b,color1c,color1d,color2 = detailedColorScheme(team)
    style.use('seaborn-darkgrid')
    url = 'Teams/' + team + '/' + team + ' Box Score.csv'
    df = pd.read_csv(url, index_col = 0)
    df = categoryFantasyPoints(df)
    dates = df['Date'].unique()
    cut = np.where(dates == date_cutoff)[0]
    cut = int(cut)

    title = player + ' DFS Performance & Moving Average'
    try:
        perf = df[df.index == player]['DFS'][:cut]
        pts = df[df.index == player]['PTS DFS'][:cut]
        ast = df[df.index == player]['AST DFS'][:cut]
        pts_l = pts.to_list()
        ast_l = ast.to_list()
        trb_b = list(map(add, ast_l, pts_l))
        trb = df[df.index == player]['TRB DFS'][:cut]
        trb_l = trb.to_list()
        otr = df[df.index == player]['OTR DFS'][:cut]
        otr_b = list(map(add, trb_b, trb_l))
        games_played = df[df.index == player]['Date'][:cut]
        avg = []
        for j in range(len(perf)):
            if j < 10:
                float_avg = sum(perf[:j+1])/(j+1)
            else:
                float_avg = sum(perf[j-9:j+1])/10
            avg.append(float_avg)
        fig = plt.figure(figsize = (5,5))
        ax = fig.add_subplot(111)
    
        sns.barplot(x = games_played[-10:], y = pts[-10:], color = color1a, label = 'points')
        sns.barplot(x = games_played[-10:], y = ast[-10:], bottom = pts[-10:], color = color1b, label = 'assists')
        sns.barplot(x = games_played[-10:], y = trb[-10:], bottom = trb_b[-10:], color = color1c, label = 'rebounds')
        sns.barplot(x = games_played[-10:], y = otr[-10:], bottom = otr_b[-10:], color = color1d, label = 'other')
        
        ax.set_aspect(1.0/ax.get_data_ratio(), adjustable='box')
        
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2),ncol=4, fancybox=True, shadow=True)    
        plt.plot(games_played[-10:],avg[-10:], marker = 'o', color = color2, linewidth = 3)
        plt.title(title, fontsize = 12)
        plt.ylabel('Total DFS')
        plt.xlabel('Game Date')
    except:
        print('The player is spelled incorrectly or they do not exist on this team')
        

def graphTeamUsageRate(team):
    color1a,color1b,color1c,color1d,color2 = detailedColorScheme(team)
    df = getTeamData(team) #gets the season performances of every player on the team's current roster
    df = getMinutesPlayed(df) #finds the minutes played of each player's statline
    df = assistRate(df) #finds the assist rate of each player's statline
    df = reboundRate(df) #finds the rebound rate of each player's statline
    df = usageRate(df) #finds the usage rate of each player's statline
    players = df.index.unique() #find the number of players on the team
    num_row = math.ceil(len(players)/2) #subplot stuff
    plt_count = 1
    plt.figure(figsize = (17,8*num_row))
    for p in players:
        p_title = p + ' Usage Rate'
        p_df = df[df.index == p]
        dates = np.array(p_df['Date'])
        opp = np.array(p_df['Versus'])
        games = []
        for i in range(len(dates)):
            game = dates[i] + '\nvs ' + opp[i]
            games.append(game)    
        ast_r = np.array(p_df['AST%'])
        trb_r = np.array(p_df['TRB%'])
        usg_r = np.array(p_df['USG%'])
        if len(p_df) < 10:
            indx = np.arange(len(p_df))
        else:
            indx = np.arange(10)
        usg_avg = []
        for i in range(len(usg_r)):
            if i < 10:
                float_avg = sum(usg_r[:i+1])/(i+1)
            else:
                float_avg = sum(usg_r[i-9:i+1])/10
            usg_avg.append(float_avg)
        style.use('seaborn-darkgrid')
        plt.subplot(num_row,2,plt_count)
        bar_width = 0.15
        plt.bar(indx - bar_width, usg_r[-10:], bar_width, label = 'USG%', color = color1a)
        plt.bar(indx, ast_r[-10:], bar_width, label = 'AST%', color = color1b)
        plt.bar(indx + bar_width, trb_r[-10:], bar_width, label = 'TRB%', color = color1c)
        plt.plot(indx - bar_width, usg_avg[-10:], marker = 'o', color = color2, linewidth = 3)
        plt.xticks(indx, games[-10:], fontsize = 8)
        plt.ylim([0,60])
        plt.xticks(rotation=315)
        plt.ylabel('Percentage')
        plt.title(p_title)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1),ncol=3, fancybox=True, shadow=True)
        plt_count += 1

#4 core players total, no distinction between teams
def newFilterLineups(player_filter,df):
    column_names = ['CPT','UTIL1','UTIL2','UTIL3','UTIL4','UTIL5','Salary','Season FP']    
    df_np = df.to_numpy()
    df_f = np.empty(8)
    p1 = player_filter[0]
    p2 = player_filter[1]
    p3 = player_filter[2]
    p4 = player_filter[3]
    for row in df_np:
        if ((p1 in row) and (p2 in row) and (p3 in row) and (p4 in row)):
            df_f = np.vstack((df_f, row))
        else:
            pass
    df_temp = pd.DataFrame(data = df_f, columns = column_names)
    return df_temp

#makes sure each lineup has at least 2 core players from each team (4) total given a list of core players
def filterCorePlayers_team(core1, core2, df):
    column_names = ['CPT','UTIL1','UTIL2','UTIL3','UTIL4','UTIL5','Salary','Season FP']
    comb1 = list(combinations(core1, 2))
    comb2 = list(combinations(core2, 2))
    df_filtered = pd.DataFrame(columns = column_names)
    frames = []
    for i in comb1:
        for j in comb2:
            filter = i + j
            df_temp = newFilterLineups(filter, df)
            frames.append(df_temp)
    df_filtered = pd.concat(frames)
    df_filtered = df_filtered.drop_duplicates()
    return df_filtered

#makes sure each lineup has at least 4 of the "core players" given a list of core players
def filterCorePlayers_noteam(core, df):
    column_names = ['CPT','UTIL1','UTIL2','UTIL3','UTIL4','UTIL5','Salary','Season FP']    
    combs = list(combinations(core, 4))
    df_filtered = pd.DataFrame(columns = column_names)
    for i in combs:
        df_temp = newFilterLineups(i,df)
        df_filtered = df_filtered.append(df_temp)
    df_filtered = df_filtered.drop_duplicates()
    indexZeroes = df_filtered[df_filtered['CPT'] == 0.0].index
    df_filtered.drop(indexZeroes, inplace = True)
    return df_filtered

#calculates thes players' sma from boxscore
def setupML(team):
    url = 'Teams/'+team+'/'+team+' Box Score.csv'
    df = pd.read_csv(url, index_col = 0)
    df = nameInconsistency(fantasyPoints(usageRate(reboundRate(assistRate(getMinutesPlayed(df))))))
    return df

#adds a players sma to the draftkings csv
def appendtoDraft(team, draft):
    players = team.index.unique()
    for i in players:
        player = team[team.index == i]  #player dataframe
        num_games = len(player['Date'].unique())
        p_dfs = player['DFS'].values #numpy array
        p_usg = player['USG%'].values
        p_mp = player['MP1'].values
        if num_games < 10:
            dfs_sma = sum(p_dfs[:num_games+1])/(num_games)
            usg_sma = sum(p_usg[:num_games+1])/(num_games)
            mp_sma = sum(p_mp[:num_games+1])/(num_games)
        else: 
            dfs_sma = sum(p_dfs[num_games-9:num_games+1])/10
            usg_sma = sum(p_usg[num_games-9:num_games+1])/10
            mp_sma = sum(p_mp[num_games-9:num_games+1])/10
        draft.at[draft.index == i,'MP_SMA'] = mp_sma
        draft.at[draft.index == i,'USG_SMA'] = usg_sma
        draft.at[draft.index == i,'DFS_SMA'] = dfs_sma
    return draft

#function removes all items from a list
def remAll(L, item):
    answer = []
    for i in L:
        if i!=item:
            answer.append(i)
    return answer

from IPython.display import HTML
from random import randint

def hide_toggle(for_next=False):
    this_cell = """$('div.cell.code_cell.rendered.selected')"""
    next_cell = this_cell + '.next()'

    toggle_text = 'Toggle show/hide'  # text shown on toggle link
    target_cell = this_cell  # target cell to control with toggle
    js_hide_current = ''  # bit of JS to permanently hide code in current cell (only when toggling next cell)

    if for_next:
        target_cell = next_cell
        toggle_text += ' next cell'
        js_hide_current = this_cell + '.find("div.input").hide();'

    js_f_name = 'code_toggle_{}'.format(str(randint(1,2**64)))

    html = """
        <script>
            function {f_name}() {{
                {cell_selector}.find('div.input').toggle();
            }}

            {js_hide_current}
        </script>

        <a href="javascript:{f_name}()">{toggle_text}</a>
    """.format(
        f_name=js_f_name,
        cell_selector=target_cell,
        js_hide_current=js_hide_current, 
        toggle_text=toggle_text
    )

    return HTML(html)

def matchPlayerToTeam(players, draft, home_acr):
    core_h = []
    core_a = []
    for i in players:
        team = draft[draft.index == i]['TeamAbbrev']
        if team[0] == home_acr:
            core_h.append(i)
        else:
            core_a.append(i)
    return core_a, core_h   

def getGameResults(away_team, home_team, date):
    bx = pd.read_csv('Teams/Box Scores.csv', index_col = 0)
    away_results = bx.loc[(bx['Team'] == away_team) & (bx['Versus'] == home_team) & (bx['Date'] == date)]
    home_results = bx.loc[(bx['Team'] == home_team) & (bx['Versus'] == away_team) & (bx['Date'] == date)]
    game_results = pd.concat([away_results, home_results])
    game_results = fantasyPoints(game_results).sort_values('FP', ascending = False)
    return game_results   

def resultsSetup(away_team, home_team, date):
    split_date = date.split()
    a_acr = teamAcronym(away_team)
    h_acr = teamAcronym(home_team)
    results_date = split_date[1]+'-'+split_date[0]
    dfr = getGameResults(away_team, home_team, results_date)
    field_url = 'Games/'+date+'/'+a_acr+'at'+h_acr+'_'+date+'_Field.csv'
    draft_url = 'Games/'+date+'/'+a_acr+'at'+h_acr+'_'+date+'_D.csv'
    draftf_url = 'Games/'+date+'/'+a_acr+'at'+h_acr+'_'+date+'_DF.csv'
    field = pd.read_csv(field_url)
    df_d = pd.read_csv(draft_url)
    df_df = pd.read_csv(draftf_url)

    df_d = df_d.drop(df_d.columns[0], axis=1)
    df_df = df_df.drop(df_df.columns[0], axis = 1)
    
    return df_d, df_df, field, dfr

def bootstrapLineups_nobias(pool, lineups):
    boxscore = pd.read_csv('Teams/Box Scores.csv', index_col = 0)
    boxscore = nameInconsistency(boxscore)
    count = 1
    for i in pool:
        player_bx = boxscore.loc[boxscore.index == i]
        if count == 1:
            bx = player_bx
            count += 1
        else:
            bx = pd.concat([bx, player_bx])
    bx = fantasyPoints(bx)
    bootstrap_avg = []
    bootstrap_std = []
    for j in range(len(lineups)):
        row = lineups.iloc[j]

        cpt = row['CPT']
        cpt_games = bx[bx.index == cpt]
        cpt_fp = list(cpt_games['FP'])

        ut1 = row['UTIL1']
        ut1_games = bx[bx.index == ut1]
        ut1_fp = list(ut1_games['FP'])

        ut2 = row['UTIL2']
        ut2_games = bx[bx.index == ut2]
        ut2_fp = list(ut2_games['FP'])
        
        ut3 = row['UTIL3']
        ut3_games = bx[bx.index == ut3]
        ut3_fp = list(ut3_games['FP'])

        ut4 = row['UTIL4']
        ut4_games = bx[bx.index == ut4]
        ut4_fp = list(ut4_games['FP'])

        ut5 = row['UTIL5']
        ut5_games = bx[bx.index == ut5]
        ut5_fp = list(ut5_games['FP'])

        lineup_sum = []
        #simulate 500 games being played with no bias.
        for k in range(1000):
            cpt_perf = cpt_fp[randint(0, len(cpt_games['Date']) - 1)]
            ut1_perf = ut1_fp[randint(0, len(ut1_games['Date']) - 1)]
            ut2_perf = ut2_fp[randint(0, len(ut2_games['Date']) - 1)]
            ut3_perf = ut3_fp[randint(0, len(ut3_games['Date']) - 1)]
            ut4_perf = ut4_fp[randint(0, len(ut4_games['Date']) - 1)]
            ut5_perf = ut5_fp[randint(0, len(ut5_games['Date']) - 1)]    
            tot = 1.5*cpt_perf + ut1_perf + ut2_perf + ut3_perf + ut4_perf + ut5_perf
            lineup_sum.append(tot)

        lineup_avg = sum(lineup_sum)/len(lineup_sum)
        lineup_std = statistics.stdev(lineup_sum)
        bootstrap_avg.append(lineup_avg)
        bootstrap_std.append(lineup_std)
    lineups['BTSP No Bias FP'] = bootstrap_avg
    lineups['BTSP No Bias STD'] = bootstrap_std
    return lineups

#this function simulates each lineup 1000 times and returns the bootstrapped average and standard deviation of lineups
def bootstrapLineups_bias(pool, lineups):
    boxscore = pd.read_csv('Teams/Box Scores.csv', index_col = 0)
    boxscore = nameInconsistency(boxscore)
    count = 1
    for i in pool:
        player_bx = boxscore.loc[boxscore.index == i]
        if count == 1:
            bx = player_bx
            count += 1
        else:
            bx = pd.concat([bx, player_bx])
    bx = fantasyPoints(bx)
    bootstrap_avg = []
    bootstrap_std = []
    for j in range(len(lineups)):
        row = lineups.iloc[j]

        cpt = row['CPT']
        cpt_games = bx[bx.index == cpt]
        cpt_fp = list(cpt_games['FP'])
        cpt_l10 = cpt_fp[-10:]

        ut1 = row['UTIL1']
        ut1_games = bx[bx.index == ut1]
        ut1_fp = list(ut1_games['FP'])
        ut1_l10 = ut1_fp[-10:]

        ut2 = row['UTIL2']
        ut2_games = bx[bx.index == ut2]
        ut2_fp = list(ut2_games['FP'])
        ut2_l10 = ut2_fp[-10:]
        
        ut3 = row['UTIL3']
        ut3_games = bx[bx.index == ut3]
        ut3_fp = list(ut3_games['FP'])
        ut3_l10 = ut3_fp[-10:]

        ut4 = row['UTIL4']
        ut4_games = bx[bx.index == ut4]
        ut4_fp = list(ut4_games['FP'])
        ut4_l10 = ut4_fp[-10:]

        ut5 = row['UTIL5']
        ut5_games = bx[bx.index == ut5]
        ut5_fp = list(ut5_games['FP'])
        ut5_l10 = ut5_fp[-10:]

        lineup_sum = []
        #simulate 500 games being played with no bias.
        for k in range(500):
            cpt_perf = cpt_fp[randint(0, len(cpt_games['Date']) - 1)]
            ut1_perf = ut1_fp[randint(0, len(ut1_games['Date']) - 1)]
            ut2_perf = ut2_fp[randint(0, len(ut2_games['Date']) - 1)]
            ut3_perf = ut3_fp[randint(0, len(ut3_games['Date']) - 1)]
            ut4_perf = ut4_fp[randint(0, len(ut4_games['Date']) - 1)]
            ut5_perf = ut5_fp[randint(0, len(ut5_games['Date']) - 1)]    
            tot = 1.5*cpt_perf + ut1_perf + ut2_perf + ut3_perf + ut4_perf + ut5_perf
            lineup_sum.append(tot)
        #simulate 500 games being played with extra bias given to previous 10 games (hot/cold streak)
        for g in range(500):
            
            if len(cpt_l10) < 10:
                cpt_perf = cpt_l10[randint(0, len(cpt_l10)-1)]
            else:
                cpt_perf = cpt_l10[randint(0, 9)]
            
            if len(ut1_l10) < 10:
                ut1_perf = ut1_l10[randint(0, len(ut1_l10)-1)]
            else:
                ut1_perf = ut1_l10[randint(0, 9)]

            if len(ut2_l10) < 10:
                ut2_perf = ut2_l10[randint(0, len(ut2_l10)-1)]
            else:
                ut2_perf = ut2_l10[randint(0, 9)]
            
            if len(ut3_l10) < 10:
                ut3_perf = ut3_l10[randint(0, len(ut3_l10)-1)]
            else:
                ut3_perf = ut3_l10[randint(0, 9)]
                
            if len(ut4_l10) < 10:
                ut4_perf = ut4_l10[randint(0, len(ut4_l10)-1)]
            else:
                ut4_perf = ut4_l10[randint(0, 9)]

            if len(ut5_l10) < 10:
                ut5_perf = ut5_l10[randint(0, len(ut5_l10)-1)]
            else:
                ut5_perf = ut5_l10[randint(0, 9)]
            tot = 1.5*cpt_perf + ut1_perf + ut2_perf + ut3_perf + ut4_perf + ut5_perf
            lineup_sum.append(tot)
            
        lineup_avg = sum(lineup_sum)/len(lineup_sum)
        lineup_std = statistics.stdev(lineup_sum)
        bootstrap_avg.append(lineup_avg)
        bootstrap_std.append(lineup_std)
    lineups['BTSP Bias FP'] = bootstrap_avg
    lineups['BTSP Bias STD'] = bootstrap_std
    return lineups

def rootMSE(draft_compare):
    actual = list(draft_compare['Actual FP'])
    strat1_estimated = list(draft_compare['DK FP'])
    strat2_estimated = list(draft_compare['10SMA FP'])
    strat3_estimated = list(draft_compare['BTSP FP'])
    strat1_diff = []
    strat2_diff = []
    strat3_diff = []
    for i in range(len(actual)):
        diff1 = actual[i] - strat1_estimated[i]
        diff2 = actual[i] - strat2_estimated[i]
        diff3 = actual[i] - strat3_estimated[i]
        
        diff1 = diff1**2
        diff2 = diff2**2
        diff3 = diff3**2
        
        strat1_diff.append(diff1)
        strat2_diff.append(diff2)
        strat3_diff.append(diff3)
        
    strat1_rmse = sum(strat1_diff)/len(strat1_diff)
    strat1_rmse = (sum(strat1_diff)/len(strat1_diff))**0.5
    
    strat2_rmse = sum(strat2_diff)/len(strat2_diff)
    strat2_rmse = (sum(strat2_diff)/len(strat2_diff))**0.5
    
    strat3_rmse = sum(strat3_diff)/len(strat3_diff)
    strat3_rmse = (sum(strat3_diff)/len(strat3_diff))**0.5
    print("Strat 1: ", strat1_rmse)
    print("Strat 2: ", strat2_rmse)
    print("Strat 3: ", strat3_rmse)

def simulateGames(h_nick, h_acr, a_nick, a_acr, df, draft, pool):
    a_pool, h_pool = matchPlayerToTeam(pool, draft, h_acr)
    
    team_dict = teams.get_teams()
    team_id_a = [team for team in team_dict if team['nickname'] == a_nick][0]['id']
    team_acr_a = [team for team in team_dict if team['nickname'] == a_nick][0]['abbreviation']
    team_roster_a = commonteamroster.CommonTeamRoster(team_id = team_id_a).get_data_frames()[0]
    team_id_h = [team for team in team_dict if team['nickname'] == h_nick][0]['id']
    team_acr_h = [team for team in team_dict if team['nickname'] == h_nick][0]['abbreviation']
    team_roster_h = commonteamroster.CommonTeamRoster(team_id = team_id_h).get_data_frames()[0]
    
    min_dict_10 = {}
    min_dict_5 = {}
    #simulating 1000 games for visiting team
    sim_games_a = pd.DataFrame()
    for p in a_pool:
        venue = 'Away'
        p_id = team_roster_a[team_roster_a['PLAYER'] == p]['PLAYER_ID']
        p_all = playergamelog.PlayerGameLog(p_id, season = SeasonAll.all).get_data_frames()[0]
        p_all = homeaway(fantasyPoints(p_all))
        
        p_season = p_all[p_all['SEASON_ID'] == '22020']
        p_prev1 = p_all[p_all['SEASON_ID'] == '22019']
        p_prev2 = p_all[p_all['SEASON_ID'] == '22018']
        p_last3 = p_all[(p_all['SEASON_ID'] == '22020') | (p_all['SEASON_ID'] == '22019')| (p_all['SEASON_ID'] == '22018')]
        
        p_min = p_season['MIN']
        if len(p_season['MIN']) >= 10:
            min_dict_10[p] = sum(p_min[:10])/10
            min_dict_5[p] = sum(p_min[:5])/5
        else:
            min_dict_10[p] = sum(p_min)/len(p_min)
            min_dict_5[p] = sum(p_min)/len(p_min)

        #player career performance
        p_all_fp = list(p_all['FP'])

        #player season performance
        p_season_fp = list(p_season['FP'])
        if len(p_season_fp) == 0: p_season_fp = p_all_fp

        #player average versus opponent
        p_opp = []
        for i in range(len(p_last3['MATCHUP'])):
            if p_last3['MATCHUP'][i].split()[2] == team_acr_h:
                p_opp.append(p_last3['FP'][i])
        if len(p_opp) == 0: p_opp = p_season_fp

        #player last 10 games performance
        p_season_l10 = p_season_fp[:10]
        if len(p_season_l10) == 0: p_season_l10 = p_season_fp

        #player last season performance
        p_prev1_fp = list(p_prev1['FP'])
        if len(p_prev1_fp) == 0: p_prev1_fp = p_season_fp

        #player last last season performance
        p_prev2_fp = list(p_prev2['FP'])
        if len(p_prev2_fp) == 0: p_prev2_fp = p_season_fp

        #player home/away performance
        p_prev_ha = list(p_season[p_season['HomeAway'] == venue]['FP'])
        if len(p_prev_ha) == 0: p_prev_ha = p_season_fp

        #away team 1000 simulated games
        p_sim = []
        for j in range(1000):
            num = random.uniform(0,10)
            if num >= 0 and num < 3:
                perf = p_season_fp[randint(0, len(p_season_fp) - 1)]
            elif num >= 3 and num < 5:
                perf = p_season_l10[randint(0, len(p_season_l10) - 1)]
            elif num >= 5 and num < 7:
                perf = p_prev1_fp[randint(0, len(p_prev1_fp) - 1)]
            elif num >= 7 and num < 8:
                perf = p_prev2_fp[randint(0, len(p_prev2_fp) - 1)]
            elif num >= 8 and num < 9:
                perf = p_prev_ha[randint(0, len(p_prev_ha) - 1)]
            else:
                perf = p_opp[randint(0, len(p_opp) - 1)]
            p_sim.append(perf)
        sim_games_a[p] = p_sim

    #simulating 1000 games for home team
    sim_games_h = pd.DataFrame()
    for p in h_pool:
        venue = 'Home'
        p_id = team_roster_h[team_roster_h['PLAYER'] == p]['PLAYER_ID']
        p_all = playergamelog.PlayerGameLog(p_id, season = SeasonAll.all).get_data_frames()[0]
        p_all = homeaway(fantasyPoints(p_all))
        
        p_season = p_all[p_all['SEASON_ID'] == '22020']
        p_prev1 = p_all[p_all['SEASON_ID'] == '22019']
        p_prev2 = p_all[p_all['SEASON_ID'] == '22018']
        p_last3 = p_all[(p_all['SEASON_ID'] == '22020') | (p_all['SEASON_ID'] == '22019')| (p_all['SEASON_ID'] == '22018')]
        
        p_min = p_season['MIN']
        if len(p_season['MIN']) >= 10:
            min_dict_10[p] = sum(p_min[:10])/10
            min_dict_5[p] = sum(p_min[:5])/5
        else:
            min_dict_10[p] = sum(p_min)/len(p_min)
            min_dict_5[p] = sum(p_min)/len(p_min)

        #player career performance
        p_all_fp = list(p_all['FP'])

        #player season performance
        p_season_fp = list(p_season['FP'])
        if len(p_season_fp) == 0: p_season_fp = p_all_fp

        #player average versus opponent
        p_opp = []
        for i in range(len(p_last3['MATCHUP'])):
            if p_last3['MATCHUP'][i].split()[2] == team_acr_a:
                p_opp.append(p_last3['FP'][i])
        if len(p_opp) == 0: p_opp = p_season_fp

        #player last 10 games performance
        p_season_l10 = p_season_fp[:10]
        if len(p_season_l10) == 0: p_season_l10 = p_season_fp

        #player last season performance
        p_prev1_fp = list(p_prev1['FP'])
        if len(p_prev1_fp) == 0: p_prev1_fp = p_season_fp

        #player last last season performance
        p_prev2_fp = list(p_prev2['FP'])
        if len(p_prev2_fp) == 0: p_prev2_fp = p_season_fp

        #player home/away performance
        p_prev_ha = list(p_season[p_season['HomeAway'] == venue]['FP'])
        if len(p_prev_ha) == 0: p_prev_ha = p_season_fp

        #away team 1000 simulated games
        p_sim = []
        for j in range(1000):
            num = random.uniform(0,10)
            if num >= 0 and num < 3:
                perf = p_season_fp[randint(0, len(p_season_fp) - 1)]
            elif num >= 3 and num < 5:
                perf = p_season_l10[randint(0, len(p_season_l10) - 1)]
            elif num >= 5 and num < 7:
                perf = p_prev1_fp[randint(0, len(p_prev1_fp) - 1)]
            elif num >= 7 and num < 8:
                perf = p_prev2_fp[randint(0, len(p_prev2_fp) - 1)]
            elif num >= 8 and num < 9:
                perf = p_prev_ha[randint(0, len(p_prev_ha) - 1)]
            else:
                perf = p_opp[randint(0, len(p_opp) - 1)]
            p_sim.append(perf)
        sim_games_h[p] = p_sim
   
    #combining the simulated games into one dataframe
    sim_games_a.reset_index(drop=True, inplace=True)
    sim_games_h.reset_index(drop=True, inplace=True)
    sim_games = pd.concat([sim_games_a, sim_games_h], axis=1) 
    return sim_games, min_dict_10, min_dict_5

def valueProbability(df_filtered, sim_games):
    sim_np = sim_games.to_numpy()      #creating a list of dictionaries of the simulated games
    plys = list(sim_games.columns)        #players in order of sim_games

    #creating a players' dictionary
    plys_indx = list(range(0, len(plys)))
    plys_dict = dict(zip(plys, plys_indx))

    perf_matrix = np.zeros((len(df_filtered), len(plys)))
    var_matrix = np.zeros((len(df_filtered), len(plys)))

    #create sims avg dictionary
    sims_avg = []
    for i in plys_indx:
        sims_avg.append(sum(sim_np[:,i])/1000)

    sims_perf_dict = dict(zip(plys, sims_avg))

    #creating utl sims std dictionary
    sims_std = []
    for i in plys_indx:
        sims_std.append(statistics.pstdev(sim_np[:,i]))

    #creating cpt sims std dictionary
    cpt_arr = np.zeros((1000, len(plys)))
    for i in range(1000):
        r = [x*1.5 for x in sim_np[i]]
        cpt_arr[i] = r

    cpt_std = []
    for i in plys_indx:
        cpt_std.append(statistics.pstdev(cpt_arr[:,i]))

    utl_std_dict = dict(zip(plys, sims_std))
    cpt_std_dict = dict(zip(plys, cpt_std))

    #captain matrix
    cpts = list(df_filtered['CPT'])
    for i in range(len(cpts)):
        cpt = cpts[i]
        perf_matrix[i, plys_dict[cpt]] = 1.5*sims_perf_dict[cpt]
        var_matrix[i, plys_dict[cpt]] = cpt_std_dict[cpt]**2

    #util matrix
    utl_df = df_filtered.drop(['CPT', 'Salary', 'Season FP'], axis = 1)
    utls = utl_df.to_numpy()

    for i in range(len(utls)):
        for utl in utls[i]:
            perf_matrix[i, plys_dict[utl]] = sims_perf_dict[utl]
            var_matrix[i, plys_dict[utl]] = utl_std_dict[utl]**2

    #transform performance matrices
    sim_mean = []
    for i in range(len(utls)):
        sim_mean.append(sum(perf_matrix[i]))

    #calculate standard deviation matrices
    sim_std = []
    for i in range(len(utls)):
        sim_std.append(sum(var_matrix[i])**0.5)

    p_4x = []
    p_5x = []
    f = IntProgress(min = 0, max = len(utls), bar_style = 'success')
    bar = (HBox([Label('Loading Probabilities:'), f]))
    display(bar)
    for i in range(len(utls)):
        p_4x.append(1 - sc.norm(sim_mean[i], sim_std[i]).cdf(200))
        p_5x.append(1 - sc.norm(sim_mean[i], sim_std[i]).cdf(250))
        f.value += 1
    clear_output()

    df_filtered['Sims Mean'] = sim_mean
    df_filtered['Sims STD'] = sim_std
    df_filtered['Probs 4x'] = p_4x
    df_filtered['Probs 5x'] = p_5x
    
    return df_filtered


def minPlayed(df, min_dict_5, min_dict_10):
    df_np = df.drop(['Salary','Season FP','Sims Mean','Sims STD','Probs 4x','Probs 5x'], axis = 1).to_numpy()
    min_10 = []
    min_5 = []
    for i in df_np:
        min_row_10 = 0
        min_row_5 = 0
        for p in i:
            p_min_10 = min_dict_10[p]
            p_min_5 = min_dict_5[p]
            min_row_10 += p_min_10
            min_row_5 += p_min_5
        min_10.append(min_row_10)
        min_5.append(min_row_5)
    df['L5 Min'] = min_5
    df['L10 Min'] = min_10
    return df

def usageMetric(df, players):
    from nba_api.stats.endpoints import leaguedashplayerstats
    season_usg = leaguedashplayerstats.LeagueDashPlayerStats(measure_type_detailed_defense = 'Usage',per_mode_detailed = 'PerGame').get_data_frames()[0] 
    last5_usg = leaguedashplayerstats.LeagueDashPlayerStats(measure_type_detailed_defense = 'Usage',per_mode_detailed = 'PerGame', last_n_games = 5).get_data_frames()[0]
    last10_usg = leaguedashplayerstats.LeagueDashPlayerStats(measure_type_detailed_defense = 'Usage',per_mode_detailed = 'PerGame', last_n_games = 10).get_data_frames()[0]

    df_np = df.drop(['Salary', 'Season FP', 'Sims Mean', 'Sims STD', 'Probs 4x', 'Probs 5x', 'L10 Min', 'L5 Min'],axis = 1).to_numpy()
    
    #for season metric
    usg_dict = {}
    reb_dict = {}
    ast_dict = {}
    min_dict = {}
    sea_metric_dict = {}
    for p in players:
        try:
            usg_dict[p] = float(season_usg[season_usg['PLAYER_NAME'] == p]['USG_PCT'])
            reb_dict[p] = float(season_usg[season_usg['PLAYER_NAME'] == p]['PCT_REB'])
            ast_dict[p] = float(season_usg[season_usg['PLAYER_NAME'] == p]['PCT_AST'])
            min_dict[p] = float(season_usg[season_usg['PLAYER_NAME'] == p]['MIN'])/float(season_usg[season_usg['PLAYER_NAME'] == p]['GP'])
            #print(p, usg_dict[p], reb_dict[p], ast_dict[p], min_dict[p])
            sea_metric_dict[p] = min_dict[p]*(usg_dict[p] + 0.5*reb_dict[p] + 0.5*ast_dict[p])/48
            #print(sea_metric_dict[p])
        except:
            sea_metric_dict[p] = 0
    #for last 10 metric
    usg_dict = {}
    reb_dict = {}
    ast_dict = {}
    min_dict = {}
    l10_metric_dict = {}
    for p in players:
        try:
            usg_dict[p] = float(last10_usg[last10_usg['PLAYER_NAME'] == p]['USG_PCT'])
            reb_dict[p] = float(last10_usg[last10_usg['PLAYER_NAME'] == p]['PCT_REB'])
            ast_dict[p] = float(last10_usg[last10_usg['PLAYER_NAME'] == p]['PCT_AST'])
            min_dict[p] = float(last10_usg[last10_usg['PLAYER_NAME'] == p]['MIN'])/float(last10_usg[last10_usg['PLAYER_NAME'] == p]['GP'])
            l10_metric_dict[p] = min_dict[p]*(usg_dict[p] + 0.5*reb_dict[p] + 0.5*ast_dict[p])/48
        except:
            l10_metric_dict[p] = sea_metric_dict[p]
    #for last 5 metric
    usg_dict = {}
    reb_dict = {}
    ast_dict = {}
    min_dict = {}
    l5_metric_dict = {}
    for p in players:
        try:
            usg_dict[p] = float(last5_usg[last5_usg['PLAYER_NAME'] == p]['USG_PCT'])
            reb_dict[p] = float(last5_usg[last5_usg['PLAYER_NAME'] == p]['PCT_REB'])
            ast_dict[p] = float(last5_usg[last5_usg['PLAYER_NAME'] == p]['PCT_AST'])
            min_dict[p] = float(last5_usg[last5_usg['PLAYER_NAME'] == p]['MIN'])/float(last5_usg[last5_usg['PLAYER_NAME'] == p]['GP'])
            l5_metric_dict[p] = min_dict[p]*(usg_dict[p] + 0.5*reb_dict[p] + 0.5*ast_dict[p])/48
        except:
            try:
                l5_metric_dict[p] = l10_metric_dict[p]
            except:
                l5_metric_dict[p] = sea_metric_dict[p]
    
    #get last 5 and 10 games' metric
    L5_Metric = []
    L10_Metric = []
    for i in df_np:
        l5_metric_sum = 0
        l10_metric_sum = 0
        for p in range(len(i)):
            #print(p, l5_metric_dict[p])
            if p == 0:
                l5_metric_sum += 1.5*l5_metric_dict[i[p]]
                l10_metric_sum += 1.5*l10_metric_dict[i[p]]
            else:
                l5_metric_sum += l5_metric_dict[i[p]]
                l10_metric_sum += l10_metric_dict[i[p]]
        #print("test")

        L5_Metric.append(l5_metric_sum)
        L10_Metric.append(l10_metric_sum)

    df['L5 Metric'] = L5_Metric
    df['L10 Metric'] = L10_Metric
    
    return df


def removePlayer(player,df):
    df_np = df.to_numpy()
    count = 0
    for row in df_np:
        if player in row:
            df = df.drop([count])
        count += 1
    return df

#pulls from fantasy basketball nerd, (who's source is Fox Sports), the injury reports of players.
def getInjuryReports(players):
    
    #get the raw content from the site
    r = requests.get('https://www.fantasybasketballnerd.com/service/injuries/')
    
    #split the content into a list
    l1 = r.text.split('<Player>')
    l1.pop(0)
    l2 = [p.split('</Player>') for p in l1]

    #initiate lists for player name, injury, notes, and last updated 
    l_name = []
    l_injury = []
    l_notes = []
    l_updates = []

    #loop to pull and append information to player name, injury, and notes
    for entry in l2:
        temp = entry[0].split('<name>')
        l_name_temp = temp[1].split('</name>')
        l_name.append(l_name_temp[0])

        l_inj_temp = l_name_temp[1].split('<injury>')[1].split('</injury>')
        l_injury.append(l_inj_temp[0])

        l_note_temp = l_inj_temp[1].split('<notes>')[1].split('</notes>')
        l_notes.append(l_note_temp[0])

        l_update_temp = l_note_temp[1].split('<updated>')[1].split('</updated>')
        l_updates.append(l_update_temp[0])
    #combine the lists into one numpy array
    injury_news = []
    for i in range(len(l_name)):
        temp_line = [l_name[i], l_injury[i], l_notes[i], l_updates[i]]
        injury_news.append(temp_line)
    
    #get the indicies of the players in roster list 
    indeces = []
    for p in players:
        if p in l_name:
            indeces.append(l_name.index(p))
    
    #append the injury news the players in the roster
    roster_injuries = []
    for index in indeces:
        roster_injuries.append(injury_news[index])
    
    inj_dict = {}
    for inj in roster_injuries:
        line = inj[0] + ' is unlikely to play due to ' + inj[1] + ' (' + inj[2] + ').'
        inj_dict[inj[0]] = line
        
    #returns which players are injured given the list of players
    return inj_dict

def teamCareerData(team_roster_id):
    team_career = pd.DataFrame()
    for p in team_roster_id:
        team_career = team_career.append(playergamelog.PlayerGameLog(player_id = p, season = SeasonAll.all).get_data_frames()[0])
        time.sleep(0.5)
    
    return team_career

def teamLastNGamesPlot(team_name, team_roster_id, id_to_name_dict, team_career, n):
    
    dates = team_career['GAME_DATE']                                   #grabs the dates of each player's game
    dates = [date.capitalize().replace(',','') for date in dates]      #transforms the dates to remove capitalization and commas
    team_career['Dates'] = dates                                       #append transformed data as a new column to the dataframe

    game_dates = list(team_career.Dates)                                        #takes a list of the dates
    game_dates.sort(key = lambda date: datetime.strptime(date, '%b %d %Y'))     #organizes the dates in ascending order

    cnt = Counter(game_dates)                                                   #using collection.Counter
    unique_dates = [k for k in cnt if cnt[k] > 5]                               #show items that occur at least 5 times (for trades)
    ln_game_dates = unique_dates[-n:]                                           #grab the last n games

    game_id_dict = {}                                                           #initiate a dictionary of game_id's to game dates key-pairs
    for d in ln_game_dates:
        game_id_dict[d] = team_career[team_career['Dates'] == d]['Game_ID'].unique()[0]
        

    game_fp = []       #initiate a list of dictionaries for fantasy points
    game_min = []      #initiate a list of dictionaries for minutes played
    for g in game_id_dict:                                               #looping through the last n games
        game = team_career[team_career['Game_ID'] == game_id_dict[g]]    #pull the dataframe of each game    

        game_p_to_fp_dict = {}                                           #initiate dictionary for player name to fantasy points key-pair
        game_p_to_min_dict = {}                                          #initiate dictionary for player name to minutes played key-pair
        for p in id_to_name_dict:                                        #looping through player id to name dictionary
            p_perf = game[game['Player_ID'] == p]['FP'].values           #grab player fantasy points per game
            if len(p_perf) == 0: p_perf = 0                              #set fantasy points to 0 if player did not play
            else: p_perf = p_perf[0]                                     #grab only the value from pandacore series
            game_p_to_fp_dict[id_to_name_dict[p]] = p_perf               #set player name to fantasy points dictionary for each player

            p_min = game[game['Player_ID'] == p]['MIN'].values           #basically the same thing as above, just for minutes played
            if len(p_min) == 0: p_min = 0
            else: p_min = p_min[0]
            game_p_to_min_dict[id_to_name_dict[p]] = p_min

        game_fp.append(game_p_to_fp_dict)                                #append player to points dictionary to the initialized list of dictionaries for fantasy points
        game_min.append(game_p_to_min_dict)                              #append player to minutes dictionary to the initialized list of dictionaries for minutes played

    avg_fp_dict = {}        #initiate a dictionary for avg fantasy points
    avg_min_dict = {}       #initiate a dictionary for avg minutes played
    gp_dict = {}            #initiate a dictionary for games played
    for p in id_to_name_dict:                         #looping through each player on the roster
        perfs = []                                    #initiate list to store performances
        mins = []                                     #initiate list to store minutes 
        for g in range(len(game_fp)):                                                                 #looping through each game
            perfs.append(game_fp[g][id_to_name_dict[p]])                                              #append fantasy points for each game to list                                                  
            mins.append(game_min[g][id_to_name_dict[p]])                                              #append minutes for each game to list
        gp = len(mins) - sum([1 for m in mins if m == 0])                                             #count number of games played per last n
        if gp == 0: avg_fp = avg_min = 0                                                              #if 0 gp, avg fp and avg min = 0
        else:  
            avg_fp = sum(perfs)/gp                                                                    #calculate average fp of ln games
            avg_min = sum(mins)/gp                                                                    #calculate average min of ln games 

        name = id_to_name_dict[p].split()
        name_entry = name[0] + ' ' + name[1][0] + '.'                                                 
        avg_fp_dict[name_entry] = avg_fp                                                      #attach name-avg fp key-pair to dictionary
        avg_min_dict[id_to_name_dict[p]] = avg_min                                                    #attach name-avg min key-pair to dictionary
        gp_dict[id_to_name_dict[p]] = gp                                                              #attach name=gp key-pair to dictionary

    d = {'Player': avg_fp_dict.keys(),'Avg FP': avg_fp_dict.values(), 'Avg Min': avg_min_dict.values(), 'GP': gp_dict.values()}
    ln_df = pd.DataFrame(data = d).sort_values('Avg FP', ascending = False)
    
    title = team_name + "' Average Fantasy Points Over Last " + str(n) + " Games"
    x_axis = "Players on Current " + team_name + " Roster"
    y_axis = "Fantasy Points per Game"
    
    c1, c2 = colorScheme(team_name)
    
    sns.set_style('darkgrid')
    sns.set(rc={'figure.figsize':(12,10)})
    sns.barplot(x = 'Player', y = 'Avg FP', data = ln_df, 
                color = c1,
                edgecolor = c2,
                linewidth = 2).set_title(title, fontsize = 19)

    plt.xticks(rotation=90, fontsize = 19)
    plt.xlabel(x_axis, fontsize = 15).set_visible(False)
    plt.ylabel(y_axis, fontsize = 19)
    plt.ylim(top = 60)
    plt.tight_layout()

    plt.savefig('team.png')
    
def teamLastNGamesData(team_roster_id, id_to_name_dict, team_career, n):            #returns a dictionary of how many games each player played with the team given a window
    dates = team_career['GAME_DATE']                                   #panda series of game dates of the dataframe
    dates = [date.capitalize().replace(',','') for date in dates]      #transforms the dates to remove capitalization and commas
    team_career['Dates'] = dates                                       #append transformed data as a new column to the dataframe
    team_season = team_career[team_career['SEASON_ID'] == '22020']     #data frame of only the 2020-21 season performances
    game_dates = list(team_career.Dates)                                        #takes a list of the dates
    game_dates.sort(key = lambda date: datetime.strptime(date, '%b %d %Y'))     #organizes the dates in ascending order
    cnt = Counter(game_dates)                                                   #using collection.Counter
    unique_dates = [k for k in cnt if cnt[k] > 5]                               #show items that occur at least 5 times (for trades)
    ln_game_dates = unique_dates[-n:]                                           #grab the last n games
    
    gp_dict = {}            #initiate a dictionary for games played
    for p in id_to_name_dict:                                                #looping through each player on the roster
        p_gp_ct = 0                                                          #games played count
        p_gp = list(team_career[team_career['Player_ID'] == p]['Dates'])     #list of player's game dates played this season
        p_gp_ct = sum([1 for gp in p_gp if gp in ln_game_dates])             #number of games the player has played in the team's last n games
        gp_dict[id_to_name_dict[p]] = p_gp_ct                                #attach name=gp key-pair to dictionary

    return team_season, gp_dict

def gamesPlayedText(gp_txt, n):    #returns text based on player participation given a dictionary of player to games played and a window of time
    gp_txt_dict = {}                                       #initiate dictionary for name to text key-pair
    for i in gp_txt:                                                                                     #for each player on the roster 
        if gp_txt[i] == n:                                                                               #if player has played in all n games
            num_games_txt = "has played in all of the team's last " + str(n) + " games."                        #text for above condition
        else:                                                                                                  
            num_games_txt = "has played in " + str(gp_txt[i]) + " of the team's last " + str(n) + " games."   #text if player has played in less than all n games with team
            if (gp_txt[i] == 0):                                                                         #if player has played in zero games           
                num_games_txt = "has not played in the team's last " + str(n) + " games."                     #text for above condition
        gp_txt_dict[i] = num_games_txt                                                                   #attach name to text key-pair
    return gp_txt_dict

def EMA(smoothing, days, data):       #function that calculates the exponential moving average of a time series given smoothing value, window, and list of data       
    alpha = smoothing/(1 + days)                #calculates alpha
    ema_list = []                               #initiates EMA list
    prev_ema = 0                                #prev_ema for the first calculation
    for p in data:                              #looping through each value in data
        ema = p*alpha + prev_ema*(1 - alpha)    #calculates the EMA
        ema_list.append(ema)                    #appends EMA to EMA list
        prev_ema = ema                          #sets prev_ema for the next calculation
    return ema_list

def minutesPlayedText(id_to_name_dict, window, team_season, threshold):   #returns a dictionary of text based on a player's minutes per game
    min_txt_dict = {}                        #initializes dictionary for player-text key-pair
    for i in id_to_name_dict:                #for each player on the roster
        p_career = team_season[team_season['Player_ID'] == i]           #grabs the data frame of the player's performances from the team's dataframe
        p_season = p_career[p_career['SEASON_ID'] == '22020']           #makes sure the data is from the current 2020-21 season
        mins = list(p_season['MIN'])                                    #list of player's minutes played this season
        mins = mins[::-1]                                               #reverse the list as time series input
                        
        ema_10 = EMA(2, window, mins)                                   #calculates the EMA of the list          
        long_trend_txt = ""                                             #initiates text as empty string

        if len(mins) < window:                                          #no text if player has played less than 10 games
            long_trend_txt = ""
             
        else:
            sea_avg = sum(mins)/len(mins)                               #calculates the season average of minutes played
            
            if (ema_10[-1] > sea_avg) & (ema_10[-1] - sea_avg >= sea_avg*threshold):                                                                                           #if the 10-day EMA is greater than season average by certain threshold
                long_trend_txt = "while averaging " + str(round(ema_10[-1])) + " minutes (" + str(round(ema_10[-1] - sea_avg)) + " minutes more than his season average)."     #text for above condition
            if (ema_10[-1] < sea_avg) & (-1*(ema_10[-1] - sea_avg) >= sea_avg*threshold):                                                                                      #if the 10-day EMA is less than season average by certain threshold
                long_trend_txt = "while averaging " + str(round(ema_10[-1])) + " minutes (" + str(-1*round(ema_10[-1] - sea_avg)) + " minutes less than his season average)."  #text for above condition
            if (abs(ema_10[-1] - sea_avg) <= sea_avg*0.10):                                                                                                                    #if the 10-day EMA is within the season average by certain threshold
                long_trend_txt = "while averaging " + str(round(sea_avg,1)) + " minutes."                                                                                      #text for above condition
        min_txt_dict[id_to_name_dict[i]] = long_trend_txt               #adds player-text key-pair to dictionary
    return min_txt_dict

def fantasyPointsText(id_to_name_dict, window, team_season, threshold):   #returns a dictionary of text based on a player's fantasy points per game 
    return_txt_dict = {}                      #initializes dictionary for player-text key-pair
    for i in id_to_name_dict:                 #looping through each player in roster
        p_career = team_season[team_season['Player_ID'] == i]      #grabs the data frame of the player's performances from the team's dataframe
        p_season = p_career[p_career['SEASON_ID'] == '22020']      #makes sure the data is from the current 2020-21 season
        fp = list(p_season['FP'])                                  #list of player's fanyasy points this season
        fp = fp[::-1]                                              #reverse the list as time series input

        ema_10 = EMA(2, window, fp)                                #calculates the EMA of the list             
        ema_5 = EMA(2, window/2, fp)                               #calculates the EMA of the list given half the window

        long_trend_txt = ""             #initialize long trend text
        short_trend_txt = ""            #initialize short trend text

        if len(fp) < 10:                                                   #if player has played less than 10 games
            long_trend_txt = "has not played enough games for data."       #long_trend text given condition
            short_trend_txt = ""

        else:
            sea_avg = sum(fp)/len(fp)       #season average of player's fantasy points
            l10_avg = sum(fp[-10:])/10      #average of player's last 10 games played
            if (ema_10[-1] > sea_avg) & (ema_10[-1] - sea_avg >= sea_avg*threshold):                                                                                      #if the n-day EMA is greater than season average by given threshold
                long_trend_txt = "is on the rise at " + str(round(ema_10[-1])) + " FP (" + str(round(ema_10[-1] - sea_avg)) + " FP more than his season average)"         #text for above condition
            if (ema_5[-1] > l10_avg) & (ema_5[-1] - l10_avg >= l10_avg*threshold):                                                                                        #if the n/2-day EMA is greater than last 10 average by given threshold
                short_trend_txt = "is on a hot streak"                                                                                                                    #text for above condition
            if (ema_10[-1] < sea_avg) & (-1*(ema_10[-1] - sea_avg) >= sea_avg*threshold):                                                                                 #if the n-day EMA is less than season average by given threshold
                long_trend_txt = "is on the decline at " + str(round(ema_10[-1])) + " FP (" + str(-1*round(ema_10[-1] - sea_avg)) + " FP less than his season average)"   #text for above condition
            if (ema_5[-1] > l10_avg) & (-1*(ema_5[-1] - l10_avg) >= l10_avg*threshold):                                                                                   #if the n/2-day EMA is less than last 10 average by given treshold
                short_trend_txt = "is on a cold streak"                                                                                                                   #text for above condition
            if (abs(ema_10[-1] - sea_avg) <= sea_avg*threshold):                                                                                                               #if n-day EMA is within season average by give threshold
                long_trend_txt = "has been performing about average at " + str(round(sea_avg,1)) + " fantasy points"                                                      #text for above condition
        if not short_trend_txt:      #if player is not on cold/hot streak
            if not long_trend_txt:   #if player has not played enough games
                return_txt = ""      #return output for above conditions
            else:
                return_txt = "He " + long_trend_txt  #return output for first condition
        else:
            if (("decline" in long_trend_txt) & ("cold" in short_trend_txt))|(("rise" in long_trend_txt) & ("hot" in short_trend_txt)):  #if player is on rise/decline and on a hot/cold streak
                return_txt = "He " + long_trend_txt + ", and " + short_trend_txt + ","                                                   #return text for above condition
            else:
                return_txt = "He " + long_trend_txt + ", but " + short_trend_txt + ","                                                   #return text if not previous condition
        return_txt_dict[id_to_name_dict[i]] = return_txt        #add name-fantasy points as key-pair to dictionary
    return return_txt_dict

def gameNotes(team_roster_id, id_to_name_dict, team_df, window, threshold = 0.10):
    team_career, gp_dict = teamLastNGamesData(team_roster_id, id_to_name_dict, team_df, n = window)
    gp_txt = gamesPlayedText(gp_dict, window)
    min_txt = minutesPlayedText(id_to_name_dict, window, team_career, threshold)
    fp_txt = fantasyPointsText(id_to_name_dict, window, team_career, threshold)
    
    injuries = getInjuryReports(list(id_to_name_dict.values())) #function that returns the injury reports of players given a list of player names
    
    sea_dict = {}
    for i in id_to_name_dict:      #this block orders the player in descending order by FP season average
        p_sea = list(team_career[team_career['Player_ID'] == i]['FP'])
        if len(p_sea) == 0:
            sea_dict[id_to_name_dict[i]] = 0
        else:
            sea_dict[id_to_name_dict[i]] = sum(p_sea)/len(p_sea) 
    sea_dict = dict(sorted(sea_dict.items(), key=lambda item: item[1]))
    p_rank = list(sea_dict.keys())
    p_rank = p_rank[::-1]
    
    inj_txt = {} 
    reg_txt = {}
    for i in p_rank:
        if i in injuries:
            text = injuries[i] + " " +fp_txt[i] + " " + min_txt[i]
            inj_txt[i] = text
        else:
            text = i + ' ' + gp_txt[i] + ' ' + fp_txt[i] + ' ' + min_txt[i]
            if ("rise" in text) | ("decline" in text) | ("hot" in text) | ("cold" in text):
                reg_txt[i] = text
            else: 
                pass
            
    return reg_txt, inj_txt

def teamLastNGamesTable(team_name, team_roster_id, id_to_name_dict, team_career, n):
    dates = team_career['GAME_DATE']                                   #grabs the dates of each player's game
    dates = [date.capitalize().replace(',','') for date in dates]      #transforms the dates to remove capitalization and commas
    team_career['Dates'] = dates                                       #append transformed data as a new column to the dataframe

    game_dates = list(team_career.Dates)                                        #takes a list of the dates
    game_dates.sort(key = lambda date: datetime.strptime(date, '%b %d %Y'))     #organizes the dates in ascending order

    cnt = Counter(game_dates)                                                   #using collection.Counter
    unique_dates = [k for k in cnt if cnt[k] > 5]                               #show items that occur at least 5 times (for trades)
    ln_game_dates = unique_dates[-n:]                                           #grab the last n games

    game_id_dict = {}                                                           #initiate a dictionary of game_id's to game dates key-pairs
    for d in ln_game_dates:
        game_id_dict[d] = team_career[team_career['Dates'] == d]['Game_ID'].unique()[0]


    game_fp = []       #initiate a list of dictionaries for fantasy points
    game_min = []      #initiate a list of dictionaries for minutes played
    for g in game_id_dict:                                               #looping through the last n games
        game = team_career[team_career['Game_ID'] == game_id_dict[g]]    #pull the dataframe of each game    
        game_p_to_fp_dict = {}                                           #initiate dictionary for player name to fantasy points key-pair
        game_p_to_min_dict = {}                                          #initiate dictionary for player name to minutes played key-pair
        for p in id_to_name_dict:                                        #looping through player id to name dictionary
            p_perf = game[game['Player_ID'] == p]['FP'].values           #grab player fantasy points per game
            if len(p_perf) == 0: p_perf = 0                              #set fantasy points to 0 if player did not play
            else: p_perf = p_perf[0]                                     #grab only the value from pandacore series
            game_p_to_fp_dict[id_to_name_dict[p]] = p_perf               #set player name to fantasy points dictionary for each player

            p_min = game[game['Player_ID'] == p]['MIN'].values           #basically the same thing as above, just for minutes played
            if len(p_min) == 0: p_min = 0
            else: p_min = p_min[0]
            game_p_to_min_dict[id_to_name_dict[p]] = p_min

        game_fp.append(game_p_to_fp_dict)                                #append player to points dictionary to the initialized list of dictionaries for fantasy points
        game_min.append(game_p_to_min_dict)                              #append player to minutes dictionary to the initialized list of dictionaries for minutes played

    avg_fp_dict = {}        #initiate a dictionary for avg fantasy points
    avg_min_dict = {}       #initiate a dictionary for avg minutes played
    gp_dict = {}            #initiate a dictionary for games played
    sea_fp_dict = {}
    sea_min_dict = {}
    for p in id_to_name_dict:                         #looping through each player on the roster
        perfs = []                                    #initiate list to store performances
        mins = []                                     #initiate list to store minutes 

        #to find the season averages
        p_sea = team_career[(team_career['Player_ID'] == p) & (team_career['SEASON_ID'] == '22020')]
        sea_fp = list(p_sea['FP'])
        sea_min = list(p_sea['MIN'])
        if len(sea_min) == 0:
            sea_fp_avg = 0
            sea_min_avg = 0
        else:
            sea_fp_avg = sum(sea_fp)/len(sea_fp)
            sea_min_avg = sum(sea_min)/len(sea_min)
        sea_fp_dict[id_to_name_dict[p]] = round(sea_fp_avg,1)
        sea_min_dict[id_to_name_dict[p]] = round(sea_min_avg,1)

        for g in range(len(game_fp)):                                                                 #looping through each game
            perfs.append(game_fp[g][id_to_name_dict[p]])                                              #append fantasy points for each game to list                                                  
            mins.append(game_min[g][id_to_name_dict[p]])                                              #append minutes for each game to list
        gp = len(mins) - sum([1 for m in mins if m == 0])                                             #count number of games played per last n
        if gp == 0: avg_fp = avg_min = 0                                                              #if 0 gp, avg fp and avg min = 0
        else:  
            avg_fp = sum(perfs)/gp                                                                    #calculate average fp of ln games
            avg_min = sum(mins)/gp                                                                    #calculate average min of ln games
        avg_fp_dict[id_to_name_dict[p]] = round(avg_fp,1)                                             #attach name-avg fp key-pair to dictionary
        avg_min_dict[id_to_name_dict[p]] = round(avg_min,1)                                           #attach name-avg min key-pair to dictionary
        gp_dict[id_to_name_dict[p]] = gp                                                              #attach name=gp key-pair to dictionary

        
    l10FP_name = 'L'+str(n)+ ' FP'
    l10MIN_name = 'L'+str(n)+ ' MIN'
    df = pd.DataFrame.from_dict(avg_fp_dict, orient='index', columns =[l10FP_name])
    l10_mins = list(avg_min_dict.values())
    sea_mins = list(sea_min_dict.values())
    sea_fp = list(sea_fp_dict.values())
    df['SEA FP'] = sea_fp
    df[l10MIN_name] = l10_mins
    df['SEA MIN'] = sea_mins

    df = df.sort_values('L10 FP', ascending = False)
    return df

def onePager_GraphDetailedPlayerPerformance(team, player_id, team_career, id_to_name_dict):
    #color scheme of the graph, dependent on the team
    color1a,color1b,color1c,color1d,color2 = detailedColorScheme(team)
    style.use('seaborn-darkgrid')
    
    #team_career = categoryFantasyPoints(team_career)
    
    player_season = team_career[(team_career['Player_ID'] == player_id) & (team_career['SEASON_ID'] == '22020')]
    
    title = id_to_name_dict[player_id] + ' FP Performance & Moving Average'
    perf = Reverse(player_season['FP'])
    pts = Reverse(player_season['PTS FP'])
    ast = Reverse(player_season['AST FP'])
    trb = Reverse(player_season['REB FP'])
    otr = Reverse(player_season['OTR FP'])
    games_played = Reverse(player_season['GAME_DATE'])
    avg = []
    for j in range(len(perf)):
        if j < 10:
            float_avg = sum(perf[:j+1])/(j+1)
        else:
            float_avg = sum(perf[j-9:j+1])/10
        avg.append(float_avg)        
    b2 = np.add(pts[-10:], ast[-10:])
    b3 = np.add(b2, trb[-10:])
    if len(games_played) == 0:
        plt.figure(figsize = (6.5,7))
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12),ncol=5, fancybox=True, shadow=True)    
        plt.title(title, fontsize = 12)
        plt.xticks(rotation=315, fontsize = 8)
        plt.ylim(top = 80)
        plt.ylabel('Total FP')
        file_name = "Performances/" + str(player_id) + '.png'
        plt.savefig(file_name)
    else:
        plt.figure(figsize = (6.5,7))
        sns.barplot(x = games_played[-10:], y = pts[-10:], color = color1a, label = 'points')
        sns.barplot(x = games_played[-10:], y = ast[-10:], bottom = pts[-10:], color = color1b, label = 'assists')
        sns.barplot(x = games_played[-10:], y = trb[-10:], bottom = b2, color = color1c, label = 'rebounds')
        sns.barplot(x = games_played[-10:], y = otr[-10:], bottom = b3, color = color1d, label = 'other')    
        plt.plot(games_played[-10:],avg[-10:], marker = 'o', color = color2, linewidth = 3, label = 'mov_avg')
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12),ncol=5, fancybox=True, shadow=True)    
        plt.title(title, fontsize = 12)
        plt.xticks(rotation=315, fontsize = 8)
        plt.ylim(top = 80)
        plt.ylabel('Total FP')
        file_name = "Performances/" + str(player_id) + '.png'
        plt.savefig(file_name)
    clear_output()


def playerPeformanceToPDF(pdf, team_name, team_roster_id, id_to_name_dict, df_fp):
    WIDTH = 215.9
    num_pages = math.ceil(len(team_roster_id)/4)
    player_index = [0, 1, 2, 3]
    for page in range(num_pages):
        pdf.add_page()
        pdf.set_font('DejaVu', 'B', 20)
        title = "Player Performances"
        if page == 0:
            pdf.cell(0, 10, title, 0, 1, 'C')
        else:
            title += " cont."
            pdf.cell(0, 10, title, 0, 1, 'C')

        onePager_GraphDetailedPlayerPerformance(team_name, team_roster_id[player_index[0]], df_fp, id_to_name_dict)
        file_name = "Performances/" + str(team_roster_id[player_index[0]]) + ".png"
        pdf.image(file_name, x = 8, y = 35, w = WIDTH*.45)

        try:
            onePager_GraphDetailedPlayerPerformance(team_name, team_roster_id[player_index[1]], df_fp, id_to_name_dict)
            file_name = "Performances/" + str(team_roster_id[player_index[1]]) + ".png"
            pdf.image(file_name, x = WIDTH*.48, y = 35, w = WIDTH*.45)
        except:
            break
        try:
            onePager_GraphDetailedPlayerPerformance(team_name, team_roster_id[player_index[2]], df_fp, id_to_name_dict)
            file_name = "Performances/" + str(team_roster_id[player_index[2]]) + ".png"
            pdf.image(file_name, x = 8, y = 150, w = WIDTH*.45)
        except:
            break
        try:
            onePager_GraphDetailedPlayerPerformance(team_name, team_roster_id[player_index[3]], df_fp, id_to_name_dict)
            file_name = "Performances/" + str(team_roster_id[player_index[3]]) + ".png"
            pdf.image(file_name, x = WIDTH*.48, y = 150, w = WIDTH*.45)
        except:
            break
        player_index = [x+4 for x in player_index]
        
def FAQ(pdf, site):
    
    if (site == "DraftKings") | (site == "DK"):
        point_system = "DraftKings"
    elif (site =="Fanduel") | (site == "FD"):
        point_system = "FanDuel"
    
    pdf.add_page()
    pdf.set_font('DejaVu', 'B', 20)
    pdf.cell(0, h = 10, txt = "Document FAQs", border = 0, ln = 1, align = 'L')
    pdf.ln(10)

    pdf.set_font('DejaVu', '', 10)
    pdf.cell(18, h = 4, txt = "What are Fantasy Points?", border = 0, ln = 1, align = 'L')
    pdf.ln(3)
    pdf.set_font('DejaVu', 'I', 9)
    pdf.cell(18, h = 5, txt = f"Fantasy points is a point-system concept from Daily Fantasy Sports. For this report, we adopted {point_system}'s", border = 0, ln = 1, align = 'L')
    if point_system == "DraftKings":
        pdf.cell(18, h = 5, txt = "scoring system which is as follows: +1 point for every point scored, +0.5 points if a three is made, +1.25", border = 0, ln = 1, align = 'L')
        pdf.cell(18, h = 5, txt = "points for a rebound, +1.5 points for an assist, +2 points for a block or steal, +1.5 points for a ", border = 0, ln = 1, align = 'L')
        pdf.cell(18, h = 5, txt = "double-double, +3 points for a triple-double, and -0.5 points for a turnover.", border = 0, ln = 1, align = 'L')
    elif point_system == "FanDuel":
        pdf.cell(18, h = 5, txt = "scoring system which is as follows: +3 points for a 3-pointer made, +2 points for a 2-pointer made,", border = 0, ln = 1, align = 'L')
        pdf.cell(18, h = 5, txt = "+1 point for a free throw made, +1.2 points for a rebound, +1.5 points for an assist, +3 points", border = 0, ln = 1, align = 'L')
        pdf.cell(18, h = 5, txt = "for a block or steal, and -1 point for a turnover.", border = 0, ln = 1, align = 'L')
        
    pdf.ln(8)
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(18, h = 4, txt = "Where do we get the data?", border = 0, ln = 1, align = 'L')
    pdf.ln(3)
    pdf.set_font('DejaVu', 'I', 9)
    pdf.cell(18, h = 5, txt = "Majority of the data is obtained through the NBA API. The injury reports are pulled from Fantasy", border = 0, ln = 1, align = 'L')
    pdf.cell(18, h = 5, txt = "Basketball Nerd, whose source is Fox Sports.", border = 0, ln = 1, align = 'L')

    pdf.ln(8)
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(18, h = 4, txt = "How do I read the Team Graph & Chart?", border = 0, ln = 1, align = 'L')
    pdf.ln(3)
    pdf.set_font('DejaVu', 'I', 9)
    pdf.cell(18, h = 5, txt = "The team graph displays average player performances in the team's last 10 games. The chart shows both player", border = 0, ln = 1, align = 'L')
    pdf.cell(18, h = 5, txt = "averages of performance and minutes played in the team's last 10 games and the players' overall season.", border = 0, ln = 1, align = 'L')

    pdf.ln(8)
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(18, h = 4, txt = "How did we determine if a player is on the rise or decline?", border = 0, ln = 1, align = 'L')
    pdf.ln(3)
    pdf.set_font('DejaVu', 'I', 9)
    pdf.cell(18, h = 5, txt = "A player is determined to be on the rise/decline if their 10-game exponential moving average for fantasy", border = 0, ln = 1, align = 'L')
    pdf.cell(18, h = 5, txt = "points is greater/less than their season average by a 15% threshold.", border = 0, ln = 1, align = 'L')

    pdf.ln(8)
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(18, h = 4, txt = "How did we determine if a player is on a hot or cold streak?", border = 0, ln = 1, align = 'L')
    pdf.ln(3)
    pdf.set_font('DejaVu', 'I', 9)
    pdf.cell(18, h = 5, txt = "A player is determined to be on a hot/cold streak if their 5-game exponential moving average for fantasy", border = 0, ln = 1, align = 'L')
    pdf.cell(18, h = 5, txt = "points is greater/less than their 10 game average by a 15% threshold.", border = 0, ln = 1, align = 'L')


    pdf.ln(8)
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(18, h = 4, txt = "Why do the numbers from Player Trends not match with the Team Visualizations?", border = 0, ln = 1, align = 'L')
    pdf.ln(3)
    pdf.set_font('DejaVu', 'I', 9)
    pdf.cell(18, h = 5, txt = "Two reasons. One, as stated above, Player Trends are determined by exponential moving averages as", border = 0, ln = 1, align = 'L')
    pdf.cell(18, h = 5, txt = "opposed to simple moving averages (what the team visualizations are created with). Two, Player Trends ", border = 0, ln = 1, align = 'L')
    pdf.cell(18, h = 5, txt = "only account for the games the Player has played in. With this logic, a Player's last 10 games may", border = 0, ln = 1, align = 'L')
    pdf.cell(18, h = 5, txt = "not always be the same as the team's last 10 games due to rest, injury, and trade shenanigans.", border = 0, ln = 1, align = 'L')

    pdf.ln(8)
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(18, h = 4, txt = "How was this report created?", border = 0, ln = 1, align = 'L')
    pdf.ln(3)
    pdf.set_font('DejaVu', 'I', 9)
    pdf.cell(18, h = 5, txt = "Reports are created using Python. The code is available upon request or on github.com/LwrncLiu.", border = 0, ln = 1, align = 'L')

    pdf.ln(8)
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(18, h = 4, txt = "Why do I feel something is off?", border = 0, ln = 1, align = 'L')
    pdf.ln(3)
    pdf.set_font('DejaVu', 'I', 9)
    pdf.cell(18, h = 5, txt = "Because of your American-ness. This report was generated based off of A4 dimensions.", border = 0, ln = 1, align = 'L')
    
    
    pdf.ln(8)
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(18, h = 4, txt = "What if I think this report sucks?", border = 0, ln = 1, align = 'L')
    pdf.ln(3)
    pdf.set_font('DejaVu', 'I', 9)
    pdf.cell(18, h = 5, txt = "Take a chill pill. Constructive criticism and words of affirmation are welcome.", border = 0, ln = 1, align = 'L')


def generateTeamReport(team_name, site):
    #from fpdf import FPDF
    team_dict = teams.get_teams()                                                           #get team dictionary
    team_id = [team for team in team_dict if team['nickname'] == team_name][0]['id']        #get team id from team dictionary
    team_roster = commonteamroster.CommonTeamRoster(team_id = team_id).get_data_frames()[0] #use team id to get team roster
    team_roster_id = list(team_roster['PLAYER_ID'])                                         #list of roster player_id's 
    team_roster_names = list(team_roster['PLAYER'])                                         #list of roster player names
    df_fp = teamCareerData(team_roster_id)
    if (site == "DraftKings") | (site == "DK"):
        df_fp = fantasyPoints(df_fp)  #calculate fantasy points (draftkings)
        df_fp = categoryFantasyPoints(df_fp)  #calculate category fantasy points (draftkings)
    elif (site == "FanDuel") | (site == "FD"):
        df_fp = fantasyPointsFD(df_fp)
        df_fp = categoryFantasyPointsFD(df_fp)
    id_to_name_dict = {}                                               #intiates a dictionary for id-name key pair
    for i in range(len(team_roster_id)):                               #for each id in roster_id list
        id_to_name_dict[team_roster_id[i]] = team_roster_names[i]      #id key is set to name pair


    teamLastNGamesPlot(team_name, team_roster_id, id_to_name_dict, df_fp, 10) #plots the fantasy reports of the team
    reg_dict, inj_dict = gameNotes(team_roster_id, id_to_name_dict, df_fp, window = 10, threshold = 0.15) #game notes
    table = teamLastNGamesTable(team_name, team_roster_id, id_to_name_dict, df_fp, 10)

    players = table.index
    ordered_name_to_id_dict = {}
    for i in players:
        ordered_name_to_id_dict[i] = dict(map(reversed, id_to_name_dict.items()))[i]
    ordered_team_roster_id = list(ordered_name_to_id_dict.values())

    columnNameList = list(table.columns)
    columnNameList.insert(0, "Player")
    players = list(table.index)

    ids = df_fp['Player_ID']
    names = []
    for i in ids:
        names.append(id_to_name_dict[i])
    df_fp['Players'] = names
    df_fp = df_fp.set_index('Players')
    
    WIDTH = 215.9
    #from datetime import date
    today = str(date.today())
    pdf = FPDF(orientation = 'P', unit = 'mm', format = 'A4')
    #one-pager
    pdf.add_page()

    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni = True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni = True)
    pdf.add_font('DejaVu', 'I', 'DejaVuSerif-Italic.ttf', uni = True)
    pdf.set_font('DejaVu', 'B', 20)

    #set background logo

    #title of page
    pdf.cell(0, 10, f'{team_name} Synopsis', 0, 1, 'C')
    pdf.set_font('DejaVu', '', 7)
    pdf.ln(-4)
    pdf.cell(0, 10, f'Report Created on: {today}', 0, 1, 'C')
    #graph from L10 team performances

    pdf.set_font('DejaVu', '', 8)
    pdf.image('team.png',x = 5, y = 28, w = WIDTH*(.57))

    #table of L10 FP, MIN and SEA FP, MIN
    pdf.set_font('DejaVu', 'B', 7)
    pdf.ln(6)
    pdf.cell(WIDTH - 95, ln = 0)
    pdf.cell(18, h = 6, txt = columnNameList[0], border = 0, ln = 0, align = 'R')
    pdf.set_fill_color(234, 234, 242)
    for header in columnNameList[1:]:
        if header == 'SEA MIN':
            pdf.cell(13,h = 6, txt = header, border = 1, ln = 1,align = 'C', fill = True)
        else:
            pdf.cell(13,h = 6, txt = header, border = 1, ln = 0,align = 'C', fill = True)
    pdf.set_font('DejaVu', '', 7)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(WIDTH - 95, ln = 0)
    for row in range(0, len(table)):
        for col_num, col_name in enumerate(columnNameList):
            if (row % 2) == 0:
                pdf.set_fill_color(247, 247, 255)
            else:
                pdf.set_fill_color(234, 234, 242)
            if col_num == 0:
                name = players[row].split()
                name_entry = name[0] + ' ' + name[1][0] + '.'
                pdf.cell(18, h = 6, txt = name_entry, border = 0, ln = 0, align = 'R')
            else:
                if col_num != len(columnNameList) - 1:
                    pdf.cell(13, h = 6, txt = str(float(table[table.index == players[row]][col_name].values)), border = 1, ln = 0, align = 'C', fill = True)
                else:
                    pdf.cell(13, h = 6, txt = str(float(table[table.index == players[row]][col_name].values)), border = 1, ln = 1, align = 'C', fill = True)
                    pdf.cell(WIDTH - 95, ln = 0)

    #text for player trends
    pdf.ln(4)
    pdf.set_font('DejaVu', 'B', 13)
    pdf.write(4, "Player Trends")
    pdf.ln(8)
    pdf.set_font('DejaVu', '', 8)
    for i in reg_dict:
        split_line = reg_dict[i].split()
        num_char = 0
        for i in range(len(split_line)):
            char_limit = 105 + i
            if num_char >= char_limit:
                first_line = split_line[:i-1]
                second_line = split_line[i-1:]
                break
            elif i == len(split_line) - 1:
                first_line = split_line
                second_line = ""
            else:
                num_char += len(split_line[i]) + 1
        first_txt = ""
        second_txt = ""
        for i in first_line:
            first_txt += i + ' '
        for j in second_line:
            second_txt += j + ' '
        pdf.cell(WIDTH, h = 5, txt = first_txt, border = 0, ln = 1, align = "L")
        if len(second_line) == 0:
            pass
        else:
            pdf.cell(WIDTH, h = 3, txt = second_txt, border = 0, ln = 1, align = "L")
        pdf.ln(2)
    #text for players in injury news
    pdf.ln(8)
    pdf.set_font('DejaVu', 'B', 13)
    pdf.write(4, "Player Injury News")
    pdf.ln(8)
    pdf.set_font('DejaVu', '', 8)
    for i in inj_dict:
        split_line = inj_dict[i].split()
        num_char = 0
        for i in range(len(split_line)):
            char_limit = 105 + i
            if num_char >= char_limit:
                first_line = split_line[:i-1]
                second_line = split_line[i-1:]
                break
            elif i == len(split_line) - 1:
                first_line = split_line
                second_line = ""
            else:
                num_char += len(split_line[i]) + 1
        first_txt = ""
        second_txt = ""
        for i in first_line:
            first_txt += i + ' '
        for j in second_line:
            second_txt += j + ' '
        pdf.cell(WIDTH, h = 5, txt = first_txt, border = 0, ln = 1, align = "L")
        if len(second_line) == 0:
            pass
        else:
            pdf.cell(WIDTH, h = 3, txt = second_txt, border = 0, ln = 1, align = "L")
        pdf.ln(2)

    #second page, beginning player graphs
    playerPeformanceToPDF(pdf, team_name, ordered_team_roster_id, id_to_name_dict, df_fp)
    #FAQ page
    FAQ(pdf, site)
    output_file_name = 'Reports/'+ team_name + " "+ site + ' Report.pdf'
    pdf.output(output_file_name, 'F')
    
    
def teamSummary(team_nick):
    #dataframe of player box scores
    df_season, df_career = teamData(team_nick)
    players = df_season.index.unique().to_list()
    player_ids = df_season.Player_ID.unique()

    #game_ids of team's last 10 games
    games = leaguegamelog.LeagueGameLog().get_data_frames()[0]
    team_game_ids_l10 = games[games['TEAM_ABBREVIATION'] == teamAcronym(team_nick)]['GAME_ID'][-10:]

    
    #dataframe of last 10 games
    df_season = fantasyPoints(df_season)
    team_l10_df = df_season[df_season['Game_ID'].isin(team_game_ids_l10)]
    
    data = np.empty([1,8])
    for i in range(len(players)):
        p = players[i]
        p_season = team_l10_df[team_l10_df.index == p]
        p_fp = p_season['FP'].values
        p_min = p_season['MIN'].values
        p_pts = p_season['PTS'].values
        p_ast = p_season['AST'].values
        p_reb = p_season['REB'].values
        gp = len(p_season)
        if gp == 0:
            p_fp_avg = p_min_avg = p_pts_avg = p_ast_avg = p_reb_avg = 0.0
        else:
            p_fp_avg = round(sum(p_fp)/gp,1)
            p_min_avg = round(sum(p_min)/gp,1)
            p_pts_avg = round(sum(p_pts)/gp,1)
            p_ast_avg = round(sum(p_ast)/gp,1)
            p_reb_avg = round(sum(p_reb)/gp,1)
        p_img = str(player_ids[i])
        p_arr = [p, gp, p_fp_avg, p_min_avg, p_pts_avg, p_ast_avg, p_reb_avg, p_img]
        data = np.vstack((data,p_arr))
    team_sum = pd.DataFrame(data, columns = ['Player', 'GP', 'FP', 'MIN', 'PTS', 'AST', 'REB', 'IMG'])
    team_sum.FP = pd.to_numeric(team_sum.FP, errors='coerce')
    team_sum.sort_values('FP', ascending = False, inplace = True)
    return team_sum.drop([0])
