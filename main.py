#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Scrapper import Parser
from Database import Database
# from Analyser import Analyser
import sqlite3

database = Database("newstal.db")
url_to_matches_list_page = "https://www.laczynaspilka.pl/druzyna-sezon/stal-szczecin/208849.html"
url_to_club_page = "https://www.laczynaspilka.pl/druzyna/stal-szczecin,208849.html"
# url_to_matches_list_page = "https://www.laczynaspilka.pl/rozgrywki/nizsze-ligi,20725.html?round=19"
# url_to_club_page = None
parser = Parser(url_to_matches_list_page, None)
database.add_scores(parser.matches)
squads = parser.squads
seen = set()
players = []
for player in squads:
    if player[1] not in seen:
        seen.add(player[1])
        players.append((player[1], player[0]))

database.add_players(players)
database.add_squads(squads)
database.add_events(parser.events)
database.add_teams(parser.teams)
database.add_competitions(parser.competitions)

# analyser = Analyser(database.db_connection)
# analyser.get_all_goals()

goals = database.get_scored_goals(url_to_club_page)
print(goals)
scored_goals_time = [0, 0, 0, 0, 0, 0]
all_goals = len(goals)
for goal in goals:
    if goal['time'] < 15:
        scored_goals_time[0] += 1
    elif goal['time'] < 30:
        scored_goals_time[1] += 1
    elif goal['time'] < 45:
        scored_goals_time[2] += 1
    elif goal['time'] < 60:
        scored_goals_time[3] += 1
    elif goal['time'] < 75:
        scored_goals_time[4] += 1
    elif goal['time'] < 90:
        scored_goals_time[5] += 1
print("Strzelone gole: ", all_goals)
print("0-15: ", scored_goals_time[0], str(scored_goals_time[0] / float(all_goals) * 100) + "%")
print("16-30: ", scored_goals_time[1], str(scored_goals_time[1] / float(all_goals) * 100) + "%")
print("31-45: ", scored_goals_time[2], str(scored_goals_time[2] / float(all_goals) * 100) + "%")
print("46-60: ", scored_goals_time[3], str(scored_goals_time[3] / float(all_goals) * 100) + "%")
print("61-75: ", scored_goals_time[4], str(scored_goals_time[4] / float(all_goals) * 100) + "%")
print("76-90: ", scored_goals_time[5], str(scored_goals_time[5] / float(all_goals) * 100) + "%")

goals = database.get_conceded_goals(url_to_club_page)
print(goals)
scored_goals_time = [0, 0, 0, 0, 0, 0]
all_goals = len(goals)
for goal in goals:
    if goal['time'] < 15:
        scored_goals_time[0] += 1
    elif goal['time'] < 30:
        scored_goals_time[1] += 1
    elif goal['time'] < 45:
        scored_goals_time[2] += 1
    elif goal['time'] < 60:
        scored_goals_time[3] += 1
    elif goal['time'] < 75:
        scored_goals_time[4] += 1
    elif goal['time'] < 90:
        scored_goals_time[5] += 1
print("Stracone gole: ", all_goals)
print("0-15: ", scored_goals_time[0], str(scored_goals_time[0] / float(all_goals) * 100) + "%")
print("16-30: ", scored_goals_time[1], str(scored_goals_time[1] / float(all_goals) * 100) + "%")
print("31-45: ", scored_goals_time[2], str(scored_goals_time[2] / float(all_goals) * 100) + "%")
print("46-60: ", scored_goals_time[3], str(scored_goals_time[3] / float(all_goals) * 100) + "%")
print("61-75: ", scored_goals_time[4], str(scored_goals_time[4] / float(all_goals) * 100) + "%")
print("76-90: ", scored_goals_time[5], str(scored_goals_time[5] / float(all_goals) * 100) + "%")

conn = sqlite3.connect("stal.db")
cur = conn.cursor()

import timeit

start = timeit.default_timer()

database.get_squad(url_to_club_page)

stop = timeit.default_timer()

print(stop - start)

print("Kadra:")
cur.execute(
    "SELECT player_name, SUM(time_played), player_id FROM squads GROUP BY `player_id` ORDER BY sum(time_played) DESC")
team_squad_tmp = cur.fetchall()
team_squad = []
for player in team_squad_tmp:
    start = timeit.default_timer()
    cur.execute("SELECT numer, count(numer) FROM squads WHERE player_id = ? GROUP BY numer ORDER BY count(numer) DESC",
                (player[2],))
    numery = cur.fetchall()
    cur.execute("SELECT numer FROM squads WHERE player_id = ? limit 1", (player[2],))
    last_number = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM event WHERE zawodnik=? AND typ='i-report-ball'", (player[2],))
    goals = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM event WHERE zawodnik=? AND typ='i-yellow-card'", (player[2],))
    yellow_cards = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM event WHERE zawodnik=? AND typ='i-red-card'", (player[2],))
    red_cards = cur.fetchone()[0]
    team_squad.append((player[0], player[1], numery, last_number, goals, yellow_cards, red_cards));
    stop = timeit.default_timer()
    print(stop - start)
print(team_squad)
