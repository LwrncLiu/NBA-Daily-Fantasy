# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 22:56:49 2021
These functions can be called in a Jupyter Notebook to display a graphical representation of an NBA team's dfs points per last 10 contests.
@author: lwrnc
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import math
import time
from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.endpoints import playergamelog
from ipywidgets import IntProgress, HBox, Label
from IPython.display import display, clear_output

#do not show pandas "best-practices" warnings
pd.options.mode.chained_assignment = None

#a dictionary of color schemes to use for each team
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
              'Magic1a':'#004874','Magic1b':'#0067a7','Magic1c':'#0087da','Magic1d':'#0ea3ff','Magic2':'#C4CED4','Sixers1a':'#003e6a','Sixers1b':'#005c9d','Sixers1c':'#007ad0','Sixers1d':'#0397ff','Sixers2':'#ED174C',
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

#calculates the fantasy points given a traditional box score
def fantasyPoints(df):
    #creating fantasy points column
    df['FP'] =""
    #looping through each row in a boxscore
    for i in range(len(df.index)):
        count = 0

        #keeping count of the main stats
        points = df['PTS'][i]
        ct_trb = df['REB'][i]
        ct_ast = df['AST'][i]
        ct_stl = df['STL'][i]
        ct_blk = df['BLK'][i]

        #assigning fantasy points to the main stats
        three_pointers = df['FG3M'][i]*0.5
        rebounds = (ct_trb)*1.25
        assists = (ct_ast)*1.5
        steals= (ct_stl)*2
        blocks = (ct_blk)*2
        turnovers = df['TOV'][i]*0.5
        mainstats = [points, ct_trb, ct_ast, ct_stl, ct_blk]
        count = points + three_pointers + rebounds + assists + steals + blocks
        count -= turnovers

        #checking for double-double
        if sum(1 for j in mainstats if j > 10) >= 2:
            count += 1.5
        #checking for triple-double
        elif sum(1 for j in mainstats if j > 10) >= 3:
            count += 3

        #attaching the calculated fantasy points to the box score
        df['FP'][i] = count
    return df

#function breaks down fantasy points by category for visualizations
def categoryFantasyPoints(df):
    #first calculating the overall fantasy points
    df = fantasyPoints(df)

    #creating categorical fantasy points columns
    df['PTS FP'] = ""
    df['REB FP'] = ""
    df['AST FP'] = ""
    df['OTR FP'] = ""

    #looping through each row in a boxscore
    for i in range(len(df.index)):
        #fantasy points from points scored
        pts_count = 0
        points = df['PTS'][i]
        three_pointers = df['FG3M'][i]*0.5
        pts_count += points + three_pointers
        df['PTS FP'][i] = pts_count

        #fantasy points from rebounds
        rebounds = (df['REB'][i])*1.25
        df['REB FP'][i] = rebounds

        #fantasy points from assists
        assists = df['AST'][i]*1.5
        df['AST FP'][i] = assists

        #fantasy points from other
        main = pts_count + rebounds + assists
        other = df['FP'][i] - main
        df['OTR FP'][i] = other
    return df

#grabs the career and season performances of each player on a team's roster
def teamData(team_name):
    #grabs the team_id of the team
    team_dict = teams.get_teams()
    team_id = [team for team in team_dict if team['nickname'] == team_name][0]['id']

    #grabs the roster of the team
    team_roster = commonteamroster.CommonTeamRoster(team_id = team_id).get_data_frames()[0]
    team_roster_id = list(team_roster['PLAYER_ID'])

    #int progress bar for collecting data
    max_count = len(team_roster_id)
    f = IntProgress(min = 0, max = max_count, bar_style = 'success')
    bar = (HBox([Label('Loading Player Data:'), f]))
    display(bar)

    #create a dataframe for the team's career box scores
    team_career = pd.DataFrame()

    #looping through each player on the roster
    for i in team_roster_id:
        #grabbing the player's career box scores
        player_career = playergamelog.PlayerGameLog(player_id = i).get_data_frames()[0]
        team_career = team_career.append(player_career)
        time.sleep(0.2) #pause to avoid timeout error?
        #move collecting data progress bar
        f.value += 1

    #clear collecting data progress bar
    clear_output()

    #int progress bar for data-beautification
    max_count_c = len(team_career['Player_ID'])
    c = IntProgress(min = 0, max = max_count_c, bar_style = 'success')
    bar1 = (HBox([Label('Calculating Player Data:'), c]))
    display(bar1)

    #initailize a list for player names
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

#reverse the order of a list
def Reverse(lst):
    return [ele for ele in reversed(lst)]

#returns the detailed chart of a team's fantasy points performance over their last 10 games
def graphDetailedTeamPerformance(team):
    #color scheme of the graph, dependent on the team
    try:
        color1a,color1b,color1c,color1d,color2 = detailedColorScheme(team)
    except:
        print('Make sure the team nickname is spelled correctly.')
    plt.style.use('seaborn-darkgrid')

    try:
        #grabs the season and career data of the players on the team roster
        df_season, df_career = teamData(team)

        #calculates the fantasy points of the players and breaks down the fantasy points by major categories
        df_season = categoryFantasyPoints(df_season)

        #list of the players
        sig_players = df_season.index.unique()

        #int progress bar for graphing each player's past 10 performances
        max_count = len(sig_players)
        g = IntProgress(min = 0, max = max_count, bar_style = 'success')
        bar = (HBox([Label('Graphing Player Data:'), g]))
        display(bar)

        #the number of rows for subplots, given the number of players
        num_row = math.ceil(len(sig_players)/2)

        #the size of the whole plot size given the number of rows
        plt.figure(figsize = (15,9*num_row))

        plt_count = 1
        #looping through each players
        for i in sig_players:
            title = i + ' DFS Performance & Moving Average'
            #finds the length of the bars of the last 10 performances by category
            perf = Reverse(df_season[df_season.index == i]['FP'])
            pts = Reverse(df_season[df_season.index == i]['PTS FP'])
            ast = Reverse(df_season[df_season.index == i]['AST FP'])
            trb = Reverse(df_season[df_season.index == i]['REB FP'])
            otr = Reverse(df_season[df_season.index == i]['OTR FP'])
            games_played = Reverse(df_season[df_season.index == i]['GAME_DATE'])

            #calculate the 10-game floating average
            avg = []
            for j in range(len(perf)):
                if j < 10:
                    float_avg = sum(perf[:j+1])/(j+1)
                else:
                    float_avg = sum(perf[j-9:j+1])/10
                avg.append(float_avg)

            #bottoms for the stacked bar chart
            b2 = np.add(pts[-10:], ast[-10:])
            b3 = np.add(b2, trb[-10:])

            #intialize the position of the player's graph
            plt.subplot(num_row,2,plt_count)

            #plots the stacked bar charts ans
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

            #updates the progress bar
            g.value += 1
        clear_output()
        plt.show()
    except:
        print('Probably NBA Timeout error. Try again in a few minutes.')
