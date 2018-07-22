# -*- coding: utf-8 -*-
import requests
import os
from bs4 import BeautifulSoup
import urllib
from datetime import datetime

class Parser:
    def __init__(self, url_to_matches_list_page, url_to_club_page):
        self.url_to_matches_list_page = url_to_matches_list_page
        self.url_to_club_page = url_to_club_page
        self.matches_links_list = []
        self.matches = []
        self.teams = {}
        self.competitions = {}
        self.squads = []
        self.events = []
        self.players = []

        self.get_matches_links_list()
        self.analyze_matches()
        self.analyze_players()

    def get_matches_list_page(self):
        result = requests.get(self.url_to_matches_list_page)
        matches_list_page = result.content
        return matches_list_page

    def get_matches_links_list(self):
        soup = BeautifulSoup(self.get_matches_list_page(), "html.parser")
        all_matches = soup.find_all("article", {'class': "season__game"})
        for match in all_matches:
            match_link = match.find_all("div", {'class': 'season__game-action'})[0].find_all('a', {'class': 'action'})[0]['href']
            match_date_div = match.find_all("div", {'class': 'season__game-data'})[0]
            match_day = match_date_div.find_all("span", {'class': 'day'})[0].text.strip()
            match_month = match_date_div.find_all("span", {'class': 'month'})[0].text.strip()
            match_hour = match_date_div.find_all("span", {'class': 'hour'})[0].text.strip()
            match_date_str = match_day + "/" + match_month + " " + match_hour
            match_date = datetime.strptime(match_date_str, "%d/%m/%Y %H:%M")
            self.matches_links_list.append((match_link, match_date))

        self.clean_matches_links_list()

    def clean_matches_links_list(self):
        self.matches_links_list = [x for x in self.matches_links_list if x[0] != "#"]

    def analyze_matches(self):
        for match in self.matches_links_list:
            soup = BeautifulSoup(self.get_match_page(match[0]), "html.parser")
            scores = self.get_scores(soup, match[0])
            if scores != 0:
                self.matches.append(self.get_scores(soup, match))
                self.squads += self.get_squads(soup, match[0])
                self.events += self.get_events(soup, match[0])

    def get_competition(self, page):
        nav_bar = page.select("nav#breadcrumbs")
        link_series = nav_bar[0].find_all('a')
        next_is_competition = False
        competition = ("","")
        for link in link_series:
            if next_is_competition:
                competition = (link.string.strip(), link['href'].strip())
                break
            if link.string.strip() == "Rozgrywki":
                next_is_competition = True
        return competition

    def get_scores(self, page, match):
        score_section = page.find('section', {'class': 'report-result-logos'})
        clubs = []
        club_names = []

        for team_info_div in score_section.find_all('div', {'class': 'grid-20'}):
            team_link = team_info_div.find_all('a')[1]['href'].strip()
            team_name = team_info_div.find_all('a')[1].text.strip()
            clubs.append(team_info_div.find_all('a')[1]['href'].strip())
            club_names.append(team_info_div.find_all('a')[1].text.strip())

        if len(clubs) == 0:
            return 0

        self.teams[club_names[0]] = clubs[0]
        self.teams[club_names[1]] = clubs[1]
        score = score_section.find('div', {'class': 'grid-8'}).text.strip()
        score_a = score[:score.find(":")]
        score_b = score[score.find(":") + 1:]

        competition = self.get_competition(page)
        self.competitions[competition[0]] = competition[1]

        return ((match[0], clubs[0], clubs[1], score_a, score_b, competition[1], match[1]))

    def get_squads(self, page, match):
        players = []
        squad_grid = page.find('section', {'class': 'report-teams-players'})
        squads = squad_grid.find_all('div', {'class': 'grid-24'})
        for squad in squads:
            club = squad.find('span').find('a')['href']
            if (club == self.url_to_club_page or self.url_to_club_page is None):
                # coach = club.find('span', {'class': 'coach-name'})
                lists = squad.find_all('div', {'class': 'report-players-list'})
                first_players = lists[0].find_all('a')
                for player in first_players:
                    player_name = player.find('div', {'class': 'player-name'}).text.strip()
                    player_name, time_played = self.player_clean(player_name)
                    if time_played == 0:
                        time_played = 90;
                    player_number = player.find('div', {'class': 'player-nr'}).text.strip()
                    player_id = player['href']
                    players.append((player_name, player_id, player_number, time_played, 1, club, match))

                bench_players = lists[1].find_all('a')
                for player in bench_players:
                    player_name = player.find('div', {'class': 'player-name'}).text.strip()
                    player_name, time_sub = self.player_clean(player_name)
                    if time_sub > 0:
                        time_played = 90 - int(time_sub)
                        if time_played < 0:
                            time_played = 1
                    else:
                        time_played = 0
                    player_number = player.find('div', {'class': 'player-nr'}).text.strip()
                    player_id = player['href']
                    players.append((player_name, player_id, player_number, time_played, 0, club, match))
        return players

    def analyze_players(self):
        seen = set()
        for player in self.squads:
            if player[1] not in seen:
                seen.add(player[1])
                player_info = self.get_player(player[1])
                # player_link, birth, club, matches, minutes, goals, yellow_cards, red_cards
                self.players.append((player[1], player[0], player_info[1], player_info[2], player_info[3], player_info[4], player_info[5], player_info[6], player_info[7]))

    def player_clean(self, player):
        change_time = 0
        if player.find("(") != -1:
            change_time = player[player.find("(")+1:player.find("'")]
            change_time = int(change_time)
            player = player[:player.find("(")]
        return (player.strip(), change_time)

    def team_clean(self, team):
        if team.find('opuścił') != -1:
            team = team[:team.find(" opuścił")]
        elif team.find('wszedł') != -1:
            team = team[:team.find(" wszedł")]
        elif team.find('strzelił') != -1:
            team = team[:team.find(" strzelił")]
        elif team.find('otrzymał') != -1:
            team = team[:team.find(" otrzymał")]
        team = team.strip()
        return team.upper()

    def get_events(self, soup, game):
        events = []
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
            zawodnik = action_name.find('a')['href'].strip()
            team = self.team_clean(team)
            if (minuta == ''):
                minuta = 0
            events.append((game, int(minuta), type[0], zawodnik, self.teams[team]))
        return events

    def get_player(self, player_link):
        try:
            soup = BeautifulSoup(self.get_player_page(player_link), "html.parser")
            birth = soup.find('div', {'class': 'about-player'}).find_all('span')[1].text.strip()
            club = soup.find('section', {'class': 'fav-team'}).find('a')['href'].strip()
            stats = soup.find('section', {'class': 'season__stats'}).find_all('div')
            matches = stats[0].find('span', {'class': 'qty'}).text.strip();
            minutes = stats[1].find('span', {'class': 'qty'}).text.strip();
            goals = stats[2].find('span', {'class': 'qty'}).text.strip();
            yellow_cards = stats[3].find_all('span')[1].text.strip();
            red_cards = stats[3].find_all('span')[2].text.strip();
            return player_link, birth, club, matches, minutes, goals, yellow_cards, red_cards
        except:
            return (player_link, '', '', '', '', '', '', '')

    def get_match_page(self, match_link):
        self.create_directory_if_not_exists("pages")
        match_path = "pages/" + urllib.parse.quote(match_link, safe='')
        if not os.path.isfile(match_path):
            match_page = self.download_match_page(match_link, match_path)
        else:
            match_page = self.read_match_page_from_disk(match_path)
        return match_page

    def get_player_page(self, player_link):
        self.create_directory_if_not_exists("pages")
        player_path = "pages/" + urllib.parse.quote(player_link, safe='')
        if not os.path.isfile(player_path):
            match_page = self.download_player_page(player_link, player_path)
        else:
            match_page = self.read_player_page_from_disk(player_path)
        return match_page

    def create_directory_if_not_exists(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def download_match_page(self, match_link, match_path):
        print("Nie mamy tego kurwa: " + match_path)
        result = requests.get(match_link)
        match_page = result.content
        file = open(match_path, 'wb')
        file.write(match_page)
        file.close()
        return match_page

    def download_player_page(self, player_link, player_path):
        print("Jescze nie mam strony tego zawodnika: " + player_path)
        result = requests.get(player_link)
        player_page = result.content
        file = open(player_path, 'wb')
        file.write(player_page)
        file.close()
        return player_page

    def read_match_page_from_disk(self, match_path):
        print("Mamy to!:" + match_path)
        file = open(match_path, 'rb')
        match_page = file.read()
        file.close()
        return match_page

    def read_player_page_from_disk(self, player_path):
        print("Mamy to!: " + player_path)
        file = open(player_path, 'rb')
        player_page = file.read()
        file.close()
        return player_page
