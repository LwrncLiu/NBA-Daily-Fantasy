# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 16:57:20 2021

@author: lwrnc
"""


import pandas as pd
from fantasyrate import fantasyUsageRate
from fantasy import *
import time

df = pd.read_csv('2020-21_BoxScores.csv')
df_game_ids = df['GAME_ID'].astype(str).unique()

adj_df = pd.read_csv('2020-21_BoxScores_Adj.csv')
adj_df_game_ids = adj_df['GAME_ID'].astype(str).unique()

new_game_ids = list(set(df_game_ids).difference(adj_df_game_ids))
new_game_ids_alt = ['00'+i for i in new_game_ids]

column_names = ['game_id', 'player', 'fusg']
temp = pd.DataFrame(columns = column_names)

for i in range(len(new_game_ids_alt)):
    print('Start Tracking: ', new_game_ids_alt[i])
    try:
         home, away = fantasyUsageRate(game_id = new_game_ids_alt[i]) #calculate FUSG for game
    #     print('Tracking Done')
    #     #upload to temp dataframe
         try:
             for p in home:
                 new_row = pd.Series(data = {'game_id': new_game_ids[i],'player' : p,'fusg' : home[p]['usg']})
                 temp = temp.append(new_row, ignore_index = True)
             for p in away:
                 new_row = pd.Series(data ={'game_id': new_game_ids[i],'player':p,'fusg':away[p]['usg']})
                 temp = temp.append(new_row, ignore_index = True)
         except:
             print('Error here')
         print('Uploaded to temp dataframe')
         #delay for timeout purposes
         time.sleep(2)
    except:
         print('bad game id')
         time.sleep(2)
    print('Timer Done')
    print('Finished: ', i/len(new_game_ids_alt), '%')

#%%

existing_game_ids = ['00'+i for i in existing_game_ids]

df = fantasyPointsFD(df)
df = categoryFantasyPointsFD(df)

df.to_csv('2020-21_BoxScores.csv')
column_names = ['game_id', 'player', 'fusg']
temp = pd.DataFrame(columns = column_names)

for i in range(len(games_alt)):
    print('Starting Tracking', games_alt[i])
    try:        
        home, away = fantasyUsageRate(game_id = games_alt[i]) #calculate FUSG for game
        print('Tracking Done')
        #upload to temp dataframe
        for p in home:
            new_row = pd.Series(data ={'game_id': games[i],'player':p,'fusg':home[p]['usg']})
            temp = temp.append(new_row, ignore_index = True)
        for p in away:
            new_row = pd.Series(data ={'game_id': games[i],'player':p,'fusg':away[p]['usg']})
            temp = temp.append(new_row, ignore_index = True)
        print('Uploaded to temp dataframe')
        #delay for timeout purposes
        time.sleep(2)
    except: 
        #sometimes a game_id is just bad. 
        print('bad game_id')
        time.sleep(2)
    print('Finished: ', i/len(games_alt), '%')
    print('Timer done')
    
#%%
#attach fusg from temp to df
new_df = pd.merge(df, temp, how = 'left', left_on = ['GAME_ID','PLAYER_NAME'], right_on = ['game_id','player'])
#%%
df = pd.read_csv('2020-21_BoxScores_Adj.csv')

