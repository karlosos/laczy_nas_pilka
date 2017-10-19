import requests
import sqlite3
from bs4 import BeautifulSoup


class Parser:
    def __init__(self, url_to_matches_list_page, url_to_club_page):
        self.url_to_matches_list_page = url_to_matches_list_page
        self.url_to_club_page = url_to_club_page
        self.matches_links_list = []
        self.matches = []
        self.db_connection = self.create_db()
        self.create_schema()

        self.get_matches_links_list()
        self.analyze_matches()

    def get_matches_list_page(self):
        result = requests.get(self.url_to_matches_list_page)
        matches_list_page = result.content
        return matches_list_page

    def create_db(self):
        db_connection = sqlite3.connect("stats.db")
        return db_connection

    def create_schema(self):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute(
                'CREATE TABLE `event` ( `match_id` TEXT, `minuta` INTEGER, `typ` TEXT, `zawodnik` TEXT, `team` TEXT )')
            cursor.execute(
                'CREATE TABLE `mecz` ( `match_id` TEXT NOT NULL, `team_a` TEXT, `team_b` TEXT, `score_a` INTEGER, \
                `score_b` INTEGER, PRIMARY KEY(`match_id`) )')
            cursor.execute(
                'CREATE TABLE `squads` ( `player_name` TEXT, `player_id` TEXT, `numer` INTEGER,`time_played`\
                 INTEGER, `sklad` INTEGER, `team_id` TEXT, `match_id` TEXT, PRIMARY KEY(`player_id`,`match_id`) )')
            cursor.execute('CREATE TABLE `team` ( `team_id` TEXT, `team_name` TEXT, PRIMARY KEY(`team_id`) )')
        except:
            print("Could not create db schema")

    def get_matches_links_list(self):
        soup = BeautifulSoup(self.get_matches_list_page(), "html.parser")
        all_matches = soup.find_all("div", {'class': 'season__game-action'})
        for match in all_matches:
            for match_details_link in match.find_all('a', {'class': 'action'}):
                self.matches_links_list.append(match_details_link['href'])

        self.clean_matches_links_list()

    def clean_matches_links_list(self):
        self.matches_links_list = [x for x in self.matches_links_list if x != "#"]

    def analyze_matches(self):
        for match in self.matches_links_list:
            soup = BeautifulSoup(self.get_match_page(match), "html.parser")

            teams = {}
            score_section = soup.find('section', {'class': 'report-result-logos'})
            clubs = []
            club_names = []

            for team_info_div in score_section.find_all('div', {'class': 'grid-20'}):
                team_link = team_info_div.find_all('a')[1]['href'].strip()
                team_name = team_info_div.find_all('a')[1].text.strip()
                clubs.append(team_info_div.find_all('a')[1]['href'].strip())
                club_names.append(team_info_div.find_all('a')[1].text.strip())

            teams[club_names[0]] = clubs[0]
            teams[club_names[1]] = clubs[1]
            score = score_section.find('div', {'class': 'grid-8'}).text.strip()
            score_a = score[:score.find(":")]
            score_b = score[score.find(":") + 1:]

            self.matches.append((match, clubs[0], clubs[1], score_a, score_b))
            print(club_names[0] + " " + score_a + ":" + score_b + " " + club_names[1])

    def get_match_page(self, match_link):
        result = requests.get(match_link)
        match_page = result.content
        return match_page