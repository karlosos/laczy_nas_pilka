#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import sqlite3
from jinja2 import Template
import io

def create_schema(cursor):
    try:
        cursor.execute('CREATE TABLE `event` ( `match_id` TEXT, `minuta` INTEGER, `typ` TEXT, `zawodnik` TEXT, `team` TEXT )')
        cursor.execute('CREATE TABLE `mecz` ( `match_id` TEXT NOT NULL, `team_a` TEXT, `team_b` TEXT, `score_a` INTEGER, `score_b` INTEGER, PRIMARY KEY(`match_id`) )')
        cursor.execute('CREATE TABLE `squads` ( `player_name` TEXT, `player_id` TEXT, `numer` INTEGER,`time_played` INTEGER, `sklad` INTEGER, `team_id` TEXT, `match_id` TEXT, PRIMARY KEY(`player_id`,`match_id`) )')
        cursor.execute('CREATE TABLE `team` ( `team_id` TEXT, `team_name` TEXT, PRIMARY KEY(`team_id`) )')
    except:
        pass

def team_clean(team):
    if team.find('opuścił') != -1:
        team = team[:team.find(" opuścił")]
    elif team.find('wszedł') != -1:
        team = team[:team.find(" wszedł")]
    elif team.find('strzelił') != -1:
        team = team[:team.find(" strzelił")]
    elif team.find('otrzymał') != -1:
        team = team[:team.find(" otrzymał")]
    return team.upper()

def player_clean(player):
    change_time = 0
    if player.find("(") != -1:
        change_time = player[player.find("(")+1:player.find("'")]
        change_time = int(change_time)
        player = player[:player.find("(")]
    return (player.strip(), change_time)

# this_club = "https://www.laczynaspilka.pl/druzyna-sezon/stal-szczecin/159615.html" # 2016/17
matches_link = "https://www.laczynaspilka.pl/druzyna-sezon/stal-szczecin/208849.html"  # 2017/18

result = requests.get(matches_link)
this_club = "https://www.laczynaspilka.pl/druzyna/stal-szczecin,208849.html"
c = result.content

conn = sqlite3.connect("stats.db")

create_schema(conn.cursor())
games_links = []

# pobieranie linkow do meczy
soup = BeautifulSoup(c, "html.parser")
season_game_divs = soup.find_all("div", {'class': 'season__game-action'})
for game in season_game_divs:
    for e in game.find_all('a', {'class': 'action'}):
        games_links.append(e['href'])

print(games_links)

games_links = [x for x in games_links if x != "#"]

players = []
matches = []
events = []
teams = {}

for game in games_links:
    result = requests.get(game)
    c = result.content
    soup = BeautifulSoup(c, "html.parser")

    headers = soup.find_all('section', {'class': 'report-result-logos'})
    clubs = []
    club_names = []
    for header in headers:
        for e in header.find_all('div', {'class': 'grid-20'}):
            clubs.append(e.find_all('a')[1]['href'].strip())
            club_names.append(e.find_all('a')[1].text.strip())
        teams[club_names[0]] = clubs[0]
        teams[club_names[1]] = clubs[1]
        score = header.find('div', {'class': 'grid-8'}).text.strip()
        score_a = score[:score.find(":")]
        score_b = score[score.find(":") + 1:]

        matches.append((game, clubs[0], clubs[1], score_a, score_b))
        print(club_names[0] + " " + score_a + ":" + score_b + " " + club_names[1])

    squad_grid = soup.find('section', {'class': 'report-teams-players'})
    squads = squad_grid.find_all('div', {'class': 'grid-24'})
    for e in squads:
        club = e.find('span').find('a')['href']
        if (club == this_club):
            # coach = club.find('span', {'class': 'coach-name'})
            lists = e.find_all('div', {'class': 'report-players-list'})
            first_players = lists[0].find_all('a')
            for player in first_players:
                player_name = player.find('div', {'class': 'player-name'}).text.strip()
                player_name, time_played = player_clean(player_name)
                if time_played == 0:
                    time_played = 90;
                player_number = player.find('div', {'class': 'player-nr'}).text.strip()
                player_id = player['href']
                players.append((player_name, player_id, player_number, time_played, 1, club, game))

            bench_players = lists[1].find_all('a')
            for player in bench_players:
                player_name = player.find('div', {'class': 'player-name'}).text.strip()
                player_name, time_sub = player_clean(player_name)
                if time_sub > 0:
                    time_played = 90 - int(time_sub)
                    if time_played < 0:
                        time_played = 1
                else:
                    time_played = 0
                player_number = player.find('div', {'class': 'player-nr'}).text.strip()
                player_id = player['href']
                players.append((player_name, player_id, player_number, time_played, 0, club, game))

    reports = soup.find_all('div', {'class': 'report-tracking-action'})
    for report in reports:
        minuta = report.find('div', {'class': 'action-time'}).text.strip();
        minuta = minuta[:-5]
        # print(minuta)
        # print(game)
        if (minuta.find("+") > 0):
            minuta = minuta[:minuta.find("+")]
        type = report.find('div', {'class': 'action-icon'}).find('i')['class'];
        action_name = report.find('div', {'class': 'action-name'})
        team = action_name.text[action_name.text.find(" z ") + 3:]
        zawodnik = action_name.find('a')['href'].strip();
        team = team_clean(team)
        if (minuta == ''):
            minuta = 0
        events.append((game, int(minuta), type[0], zawodnik, teams[team]))

## Dodawanie danych do bazy
cur = conn.cursor()

for match in matches:
    try:
        cur.execute("INSERT INTO mecz VALUES(?, ?, ?, ?, ?)", match)
    except sqlite3.IntegrityError:
        pass

for player in players:
    try:
        cur.execute("INSERT INTO squads VALUES(?, ?, ?, ?, ?, ?, ?)", player)
    except sqlite3.IntegrityError:
        pass
for event in events:
    try:
        cur.execute("INSERT INTO event VALUES(?, ?, ?, ?, ?)", event)
    except sqlite3.IntegrityError:
        print(event)

for team_id, team_name in teams.items():
    try:
        cur.execute("INSERT INTO team VALUES(?, ?)", (team_id, team_name))
    except sqlite3.IntegrityError:
        print(team)

conn.commit()

cur = conn.cursor()
cur.execute("SELECT minuta, match_id from event WHERE typ = 'i-report-ball' AND team = ? ORDER BY minuta ASC", (this_club,))
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

cur.execute("SELECT minuta, match_id from event WHERE typ = 'i-report-ball' AND team != ? ORDER BY minuta ASC", (this_club,))
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

teams = []
teams.append((scored_goals, conceded_goals, team_squad))
teams.append((scored_goals, conceded_goals, team_squad))
template = Template(open("template/match_report.html").read())
output = template.render(teams=teams)


with io.open('output.html', "w", encoding="utf-8") as f:
    f.write(output)

f.close()
# strzelane gole
# SELECT minuta, match_id from event WHERE typ = "i-report-ball" AND team = "https://www.laczynaspilka.pl/druzyna/stal-szczecin,208849.html" ORDER BY minuta ASC
# stracone gole
# SELECT minuta, match_id from event WHERE typ = "i-report-ball" AND team != "https://www.laczynaspilka.pl/druzyna/stal-szczecin,208849.html" ORDER BY minuta ASC
# SELECT `player_name`, sum(time_played) FROM squads GROUP BY `player_id`
# SELECT player_name, SUM(time_played) FROM squads GROUP BY `player_id` ORDER BY sum(time_played) DESC


#SELECT count(*) FROM event WHERE zawodnik='https://www.laczynaspilka.pl/zawodnik/mariusz-sypula,449493.html' AND typ='i-report-ball'