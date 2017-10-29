import requests
from bs4 import BeautifulSoup


class Parser:
    def __init__(self, url_to_matches_list_page, url_to_club_page):
        self.url_to_matches_list_page = url_to_matches_list_page
        self.url_to_club_page = url_to_club_page
        self.matches_links_list = []
        self.matches = []
        self.teams = {}
        self.squads = []
        self.events = []

        self.get_matches_links_list()
        self.analyze_matches()

    def get_matches_list_page(self):
        result = requests.get(self.url_to_matches_list_page)
        matches_list_page = result.content
        return matches_list_page

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
            self.matches.append(self.get_scores(soup, match))
            self.squads += self.get_squads(soup, match)
            self.events += self.get_events(soup, match)

    def get_scores(self, page, match):
        score_section = page.find('section', {'class': 'report-result-logos'})
        clubs = []
        club_names = []

        for team_info_div in score_section.find_all('div', {'class': 'grid-20'}):
            team_link = team_info_div.find_all('a')[1]['href'].strip()
            team_name = team_info_div.find_all('a')[1].text.strip()
            clubs.append(team_info_div.find_all('a')[1]['href'].strip())
            club_names.append(team_info_div.find_all('a')[1].text.strip())

        self.teams[club_names[0]] = clubs[0]
        self.teams[club_names[1]] = clubs[1]
        score = score_section.find('div', {'class': 'grid-8'}).text.strip()
        score_a = score[:score.find(":")]
        score_b = score[score.find(":") + 1:]
        return ((match, clubs[0], clubs[1], score_a, score_b))
        #self.matches.append((match, clubs[0], clubs[1], score_a, score_b))
        #print(club_names[0] + " " + score_a + ":" + score_b + " " + club_names[1])

    def get_squads(self, page, match):
        players = []
        squad_grid = page.find('section', {'class': 'report-teams-players'})
        squads = squad_grid.find_all('div', {'class': 'grid-24'})
        for squad in squads:
            club = squad.find('span').find('a')['href']
            if (club == self.url_to_club_page):
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
            zawodnik = action_name.find('a')['href'].strip();
            team = self.team_clean(team)
            if (minuta == ''):
                minuta = 0
            events.append((game, int(minuta), type[0], zawodnik, self.teams[team]))
        return events

    def get_match_page(self, match_link):
        result = requests.get(match_link)
        match_page = result.content
        return match_page