#!/usr/bin/env python

import random
import sys
import time
import json

def log5(a,b):
  return (a-a*b)/(a+b-2*a*b)

def pythag(c,d,e):
  return (c**e)/(c**e+d**e)

EXP = 11.5
HCA = .014
SIMS = 10000

conference = "Big 12"
conf_mapping = json.load(open('conferences.json', 'r'))
conf_data = json.load(open(conf_mapping[conference], 'r'))

f = open('summary15 (9).csv', 'r')
f.next()
team_data = {}
for line in f:
    d = line.split(',')
    team_data[d[0]] = [float(d[7]), float(d[11]), int(d[14])]

f.close()

teams = conf_data['teams']
team_champs = dict(zip(teams, [[0,0,0] for i in teams]))
games = conf_data['schedule']

for i in range(SIMS):
    season_wins = dict(zip(teams, [0]*len(teams)))
    wle = dict(zip(teams, [[0,0,0] for i in teams]))
    for g in games:
        home_oe = team_data[g['home-team']][0]
        home_de = team_data[g['home-team']][1]
        away_oe = team_data[g['away-team']][0]
        away_de = team_data[g['away-team']][1]
        home_pyth = pythag(home_oe*(1+HCA), home_de*(1-HCA), EXP)
        away_pyth = pythag(away_oe*(1-HCA), away_de*(1+HCA), EXP)
        home_win_prob = log5(home_pyth, away_pyth)
        if g['winner']:
            season_wins[g['winner']] += 1
            wle[g['winner']][0] += 1
            if g['winner'] == g['home-team']:
                loser = g['away-team']
            elif g['winner'] == g['away-team']:
                loser = g['home-team']
            else:
                raise NameError('Winner not in game')
            wle[loser][1] += 1
            wle[g['home-team']][2] += home_win_prob
            wle[g['away-team']][2] += (1-home_win_prob)
        else:
            if random.random() <= home_win_prob:
                season_wins[g['home-team']] += 1
            else:
                season_wins[g['away-team']] += 1

    max_wins = max([season_wins[t] for t in teams])
    champions = [t for t in teams if season_wins[t] == max_wins]
    for champ in champions:
        team_champs[champ][0] += 1
        team_champs[champ][2] += 1.0/len(champions)
        if len(champions) == 1:
            team_champs[champ][1] += 1

print('{:16}  {:4} {:2} {:2} {:4}  {:6} {:6} {:6} {:}'.format('Team', 'Rnk', 'W', 'L', 'Luck', 'Share', 'Outrt', '1Seed', 'EWins'))


for team in sorted(teams, key= lambda x: team_champs[x][0], reverse=True):
    # print '{0:15s}{1:4d}  {2:.3f}  {3:.3f}  '\
    # '{4:.3f}'.format(team, team_data[team][2], float(team_champs[team][0])/SIMS,
    #     float(team_champs[team][1])/SIMS, team_champs[team][2]/SIMS)

    print('{0:16} {1:4}  {2:1}  {3:1}  {4:4.1f}  {5:0.3f}  {6:0.3f}  {7:0.3f}  '\
       '{8:.3}'.format(team, team_data[team][2], wle[team][0], wle[team][1],
        wle[team][0]-wle[team][2], float(team_champs[team][0])/SIMS, 
        float(team_champs[team][1])/SIMS, float(team_champs[team][2])/SIMS, 1.0))
