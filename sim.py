#!/usr/bin/env python

import random
import sys
import time
import pandas
import json

def log5(a,b):
  return (a-a*b)/(a+b-2*a*b)

def pythag(c,d,e):
  return (c**e)/(c**e+d**e)

EXP = 11.5
HCA = .014
SIMS = 10000

kenpom_data = pandas.read_csv('summary15 (9).csv', index_col=0)

conf_file = open('conferences.json', 'r')
conf_data = json.load(conf_file)

teams = conf_data['Big 12']['teams']
team_eff = {}
for t in teams:
    team_eff[t] = [kenpom_data.loc[t, 'AdjOE'], kenpom_data.loc[t, 'AdjDE']]

team_champs = dict(zip(teams, [0]*len(teams)))

games = conf_data['Big 12']['schedule']

for i in range(SIMS):
    season_wins = dict(zip(teams, [0]*len(teams)))
    for g in games:
        if g['winner']:
            season_wins[g['winner']] += 1
        else:
            home_oe = team_eff[g['home-team']][0]
            home_de = team_eff[g['home-team']][1]
            away_oe = team_eff[g['away-team']][0]
            away_de = team_eff[g['away-team']][1]

            home_pyth = pythag(home_oe*(1+HCA), home_de*(1-HCA), EXP)
            away_pyth = pythag(away_oe*(1-HCA), away_de*(1+HCA), EXP)
            home_win_prob = log5(home_pyth, away_pyth)

            if random.random() <= home_win_prob:
                season_wins[g['home-team']] += 1
            else:
                season_wins[g['away-team']] += 1

    max_wins = max([season_wins[t] for t in teams])
    champions = [t for t in teams if season_wins[t] == max_wins]
    for champ in champions:
        team_champs[champ] += 1

print team_champs