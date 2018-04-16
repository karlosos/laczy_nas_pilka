#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Scrapper import Parser
from Database import Database
#from Analyser import Analyser
import sqlite3


# database = Database("stal.db")
url_to_matches_list_page = "https://www.laczynaspilka.pl/druzyna-sezon/stal-szczecin/208849.html"
# url_to_club_page = "https://www.laczynaspilka.pl/druzyna/stal-szczecin,208849.html"
# url_to_matches_list_page = "https://www.laczynaspilka.pl/rozgrywki/nizsze-ligi,20725.html"
# url_to_club_page = None
# parser = Parser(url_to_matches_list_page, url_to_club_page)
# database.add_scores(parser.matches)
# database.add_squads(parser.squads)
# database.add_events(parser.events)
# database.add_teams(parser.teams)
# database.add_competitions(parser.competitions)

# analyser = Analyser(database.db_connection)
# analyser.get_all_goals()

teams_output = []
conn = sqlite3.connect("stal.db")
cur = conn.cursor()
cur.execute("SELECT minuta, match_id from event WHERE typ = 'i-report-ball' AND team = ? ORDER BY minuta ASC", (url_to_matches_list_page,))
scored_goals = cur.fetchall()
scored_goals_time = [0,0,0,0,0,0]
all_goals = len(scored_goals)
for goal in scored_goals:
    if goal[0] < 15:
        scored_goals_time[0] += 1
    elif goal[0] < 30:
        scored_goals_time[1] += 1
    elif goal[0] < 45:
        scored_goals_time[2] += 1
    elif goal[0] < 60:
        scored_goals_time[3] += 1
    elif goal[0] < 75:
        scored_goals_time[4] += 1
    elif goal[0] < 90:
        scored_goals_time[5] += 1
print("Strzelone gole: ", all_goals)
print("0-15: ", scored_goals_time[0], str(scored_goals_time[0]/float(all_goals) * 100) + "%")
print("16-30: ", scored_goals_time[1], str(scored_goals_time[1]/float(all_goals) * 100) + "%")
print("31-45: ", scored_goals_time[2], str(scored_goals_time[2]/float(all_goals) * 100) + "%")
print("46-60: ", scored_goals_time[3], str(scored_goals_time[3]/float(all_goals) * 100) + "%")
print("61-75: ", scored_goals_time[4], str(scored_goals_time[4]/float(all_goals) * 100) + "%")
print("76-90: ", scored_goals_time[5], str(scored_goals_time[5]/float(all_goals) * 100) + "%")
scored_goals = [all_goals, scored_goals_time]

cur.execute("SELECT minuta, match_id from event WHERE typ = 'i-report-ball' AND team != ? ORDER BY minuta ASC", (url_to_matches_list_page,))
conceded_goals = cur.fetchall()
conceded_goals_time = [0,0,0,0,0,0]
all_goals = len(conceded_goals)
for goal in conceded_goals:
    if goal[0] < 15:
        conceded_goals_time[0] += 1
    elif goal[0] < 30:
        conceded_goals_time[1] += 1
    elif goal[0] < 45:
        conceded_goals_time[2] += 1
    elif goal[0] < 60:
        conceded_goals_time[3] += 1
    elif goal[0] < 75:
        conceded_goals_time[4] += 1
    elif goal[0] < 90:
        conceded_goals_time[5] += 1
print("Gole tracone: ", all_goals)
print("0-15: ", conceded_goals_time[0], str(conceded_goals_time[0]/float(all_goals) * 100) + "%")
print("16-30: ", conceded_goals_time[1], str(conceded_goals_time[1]/float(all_goals) * 100) + "%")
print("31-45: ", conceded_goals_time[2], str(conceded_goals_time[2]/float(all_goals) * 100) + "%")
print("46-60: ", conceded_goals_time[3], str(conceded_goals_time[3]/float(all_goals) * 100) + "%")
print("61-75: ", conceded_goals_time[4], str(conceded_goals_time[4]/float(all_goals) * 100) + "%")
print("76-90: ", conceded_goals_time[5], str(conceded_goals_time[5]/float(all_goals) * 100) + "%")
conceded_goals = [all_goals, conceded_goals_time]

print("Kadra:")
cur.execute("SELECT player_name, SUM(time_played), player_id FROM squads GROUP BY `player_id` ORDER BY sum(time_played) DESC")
team_squad_tmp = cur.fetchall()
team_squad = []
for player in team_squad_tmp:
    cur.execute("SELECT numer, count(numer) FROM squads WHERE player_id = ? GROUP BY numer ORDER BY count(numer) DESC", (player[2],))
    numery = cur.fetchall()
    cur.execute("SELECT numer FROM squads WHERE player_id = ? limit 1", (player[2], ))
    last_number = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM event WHERE zawodnik=? AND typ='i-report-ball'", (player[2], ))
    goals = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM event WHERE zawodnik=? AND typ='i-yellow-card'", (player[2],))
    yellow_cards = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM event WHERE zawodnik=? AND typ='i-red-card'", (player[2],))
    red_cards = cur.fetchone()[0]
    team_squad.append((player[0], player[1], numery, last_number, goals, yellow_cards, red_cards));

print(team_squad)

teams_output.append((scored_goals, conceded_goals, team_squad, url_to_matches_list_page))