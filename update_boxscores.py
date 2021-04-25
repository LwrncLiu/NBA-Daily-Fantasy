# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 18:28:04 2021

@author: lwrnc
"""
import time
import schedule
from nba_api.stats.endpoints import boxscoretraditionalv2, leaguegamelog
import pandas as pd

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
        print(f3m_list[i])
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

def update_boxscores():
    #loading existing dataset and game_ids
    df = pd.read_csv('2020-21_BoxScores.csv')
    existing_game_ids = df['GAME_ID'].astype(str).unique()
    existing_game_ids = ['00'+i for i in existing_game_ids]

    #loading game_ids from nba_api
    game_ids = leaguegamelog.LeagueGameLog().get_data_frames()[0]['GAME_ID'].unique()

    #compare game_ids
    new_game_ids = set(game_ids).difference(existing_game_ids)
    if len(new_game_ids) == 0:
        print('No New Games to Update')
    else:
    #add new boxscores to masterfile
        for i in new_game_ids:#new_game_ids:
            game_bs = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id = i).get_data_frames()[0]
            game_bs = categoryFantasyPoints(game_bs)
            frames = [df, game_bs]
            df = pd.concat(frames)
            time.sleep(0.5)
        df.drop(['Unnamed: 0'], axis = 1, inplace = True)
        df.to_csv('2020-21_BoxScores.csv')

#schedule.every().day.at("03:00").do(update_boxscores)

#while 1:
#    schedule.run_pending()
#    time.sleep(1)
update_boxscores()