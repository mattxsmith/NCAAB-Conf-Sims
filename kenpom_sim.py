#!/usr/bin/env python

from __future__ import division
from random import random
from time import time
from json import load
from os.path import isfile
from math import erf
import argparse

time_count = time()

def log5(a,b):
  return (a-a*b)/(a+b-2*a*b)

def pythag(c,d,e):
  return (c**e)/(c**e+d**e)

# default constants
SUMMARY_FILE = 'summary17 (13).csv'
EXP = 11.5 # pythag exponent
HCA = .014 # home court advantage
AVG_TEMPO = 69.7 # used to calculate tempo of each game


parser = argparse.ArgumentParser()
parser.add_argument("conference", help="This argument is the name of the"
    "conference you want to simulate. Conference names can be found in the"
    "conferences.json file")
parser.add_argument('-n','--number', help="This argument is the number of"
    " simulations you want to run", type=int, default=10000)
parser.add_argument('-w','--wins', help="This argument is the team"
    " that you want to show a win distribution of")
args = parser.parse_args()

SIMS = args.number

if not isfile(SUMMARY_FILE):
    raise NameError('Cannot find the %s file.' % SUMMARY_FILE)

conference = args.conference
conf_mapping = load(open('conferences.json', 'r'))
conf_data = load(open(conf_mapping[conference], 'r'))

f = open(SUMMARY_FILE, 'r')
f = [i.strip() for i in f.readlines()][:]
header = f.pop(0)
header = header.split(',')
cols = ['"TeamName"', '"AdjOE"', '"AdjDE"', '"AdjEM"', '"RankAdjEM"', '"AdjTempo"']
col_inds = dict([(c, header.index(c)) for c in cols])
# this should really be in some sort of data table structure
# the order of metrics is adjo, adjd, rank, adjtempo, adjEM
team_data = {}
for line in f:
    d = line.split(',')
    team_data[d[col_inds['"TeamName"']].replace('"', '')] = [float(d[col_inds['"AdjOE"']]),
        float(d[col_inds['"AdjDE"']]), int(d[col_inds['"RankAdjEM"']]),
        float(d[col_inds['"AdjTempo"']]), float(d[col_inds['"AdjEM"']])]

teams = conf_data['teams']
games = conf_data['schedule']

# cache the win probabilities in order to not redo calculations each sim
g_p = []
wle = dict(zip(teams, [[0,0,0] for i in teams]))


for g in games:
    tempo = team_data[g['home-team']][3]*team_data[g['away-team']][3]/AVG_TEMPO
    home_margin = (team_data[g['home-team']][4] - team_data[g['away-team']][4])*(tempo/100) + 3.75
    #if g['home-team'] == "Kansas":
    #    home_margin += 100
    #home_oe = team_data[g['home-team']][0]
    #home_de = team_data[g['home-team']][1]
    #away_oe = team_data[g['away-team']][0]
    #away_de = team_data[g['away-team']][1]
    #home_pyth = pythag(home_oe*(1+HCA), home_de*(1-HCA), EXP)
    #away_pyth = pythag(away_oe*(1-HCA), away_de*(1+HCA), EXP)
    #home_win_prob = log5(home_pyth, away_pyth)
    home_win_prob = .5*(1+erf((home_margin)/(11*(2)**.5)))
    g_p.append(home_win_prob)
    #g['winner'] = None
    if g['winner']:
        if g['winner'] == g['home-team']:
            loser = g['away-team']
        elif g['winner'] == g['away-team']:
            loser = g['home-team']
        else:
            raise NameError('Winner not in game')
        wle[g['winner']][0] += 1
        wle[loser][1] += 1
        wle[g['home-team']][2] += home_win_prob
        wle[g['away-team']][2] += (1-home_win_prob)


#print(g_p)
# calculate games in season by finding the most games a team is scheduled to play
games_per_team = [len([g for g in games if g['home-team'] == t
    or g['away-team'] == t]) for t in teams]
games_in_season = max(games_per_team)
if games_in_season != min(games_per_team):
    raise NameError('Not all teams have the same number of games. Fix json.')

# dict for counting championships
# index 0 is for any share of title, 1 is for outright and 2 is for 1 seed odds
team_champs = dict(zip(teams, [[0,0,0] for i in teams]))
# dict for keeping track of win distributions
win_dist = dict(zip(teams, [[0]*(games_in_season+1) for i in teams]))

for i in range(SIMS):
    season_wins = dict(zip(teams, [0]*len(teams)))

    # initiate dict for keeping current wins, losses and expected wins

    # this is inefficient in that it does the calcs for every SIM, but
    # it's more simple than making a seperate loop through the schedule
    for g, game_num in [(games[i], i) for i in range(len(games))]:
        home_win_prob = g_p[game_num]
        if g['winner']:
            season_wins[g['winner']] += 1
        else:
            if random() <= home_win_prob:
                season_wins[g['home-team']] += 1
            else:
                season_wins[g['away-team']] += 1

    max_wins = max([season_wins[t] for t in teams])
    # get list of all teams that tied for most wins (i.e. are champs)
    champions = [t for t in teams if season_wins[t] == max_wins]
    for champ in champions:
        team_champs[champ][0] += 1
        team_champs[champ][2] += 1.0/len(champions)
        if len(champions) == 1:
            team_champs[champ][1] += 1

    for t in teams:
        win_dist[t][season_wins[t]] += 1

print('{:16}  {:4} {:2} {:2} {:4}  {:6} {:6} {:6} {:}'.format('Team', 'Rnk',
    'W', 'L', 'Luck', 'Share', 'Outrt', '1Seed', 'EWins'))

for team in sorted(teams, key= lambda x: sum([i*win_dist[x][i]/SIMS
            for i in range(len(win_dist[x]))]), reverse=True):
    print('{0:16} {1:4}  {2:1}  {3:1}  {4:4.1f}  {5:0.3f}  {6:0.3f}  {7:0.3f}  '\
       '{8:.3}'.format(team, team_data[team][2], wle[team][0], wle[team][1],
        wle[team][0]-wle[team][2], team_champs[team][0]/SIMS,
        team_champs[team][1]/SIMS, team_champs[team][2]/SIMS,
        sum([i*win_dist[team][i]/SIMS
            for i in range(len(win_dist[team]))])))
if args.wins:
    wd_teams = []
    if args.wins == "All":
        wd_teams = teams
    elif args.wins not in teams:
        raise NameError('Win distribution team not in conference')
    else:
        wd_teams = [args.wins]
    for t in wd_teams:
        print('\nWin distribution for', t)
        print("Wins  Prob.   Cumulative")
        wd = 0
        for bb in range(games_in_season+1):
            w = win_dist[t][bb]/SIMS
            wd += w
            print('{:5} {:0.4f}  {:0.4f}'.format(str(bb), w, wd))

print('\n')