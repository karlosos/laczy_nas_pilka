from okregowastats.parser import Parser

from okregowastats.database import Database


class Updater:
    def __init__(self, database_name, url_to_matches_list_page, url_to_club_page):
        """

        :param database_name: filename of database
        :param url_to_matches_list_page: where from download matches list
        :param url_to_club_page: used only for getting stats from database, not used in scrapping
        """
        self.database = Database(database_name)
        self.url_to_matches_list_page = url_to_matches_list_page
        self.url_to_club_page = url_to_club_page
        # url_to_matches_list_page = "https://www.laczynaspilka.pl/rozgrywki/nizsze-ligi,20725.html?round=19"
        # url_to_club_page = None

    def update(self):
        parser = Parser(self.url_to_matches_list_page, None)
        self.database.add_scores(parser.matches)
        self.database.add_players(parser.players)
        self.database.add_squads(parser.squads)
        self.database.add_events(parser.events)
        self.database.add_teams(parser.teams)
        self.database.add_competitions(parser.competitions)

    def print_scored_goals(self):
        goals = self.database.get_scored_goals(self.url_to_club_page)
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

    def print_conceded_goals(self):
        goals = self.database.get_conceded_goals(self.url_to_club_page)

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

    def print_squad(self):
        for i in self.database.get_squad(self.url_to_club_page):
            print(i)

    def print_form(self):
        """Print form of a team"""
        print(self.database.get_team_form(self.url_to_club_page, 5))

    def print_average_points_per_match(self, competition_id):
        """
        Print average points per match of a team
        :param competition_id: 
        :return: 
        """
        print(self.database.get_average_points_per_match(self.url_to_club_page, competition_id))

    def print_win_percentage(self, competition_id):
        """
        Print win percentage for a team in given competition
        :param competition_id: 
        :return: 
        """
        print(self.database.get_win_percentage(self.url_to_club_page, competition_id))

    def print_draw_percentage(self, competition_id):
        """
        Print draw percentage for a team in given competition
        :param competition_id: 
        :return: 
        """
        print(self.database.get_draw_percentage(self.url_to_club_page, competition_id))

    def print_lose_percentage(self, competition_id):
        """
        Print lose percentage for a team in given competition
        :param competition_id: 
        :return: 
        """
        print(self.database.get_lose_percentage(self.url_to_club_page, competition_id))

    def print_last_matches(self, competition_id, count=5):
        """
        Print last matches for a team in given competition
        :param competition_id: 
        :param count: 
        :return: 
        """
        print(self.database.get_last_matches(self.url_to_club_page, competition_id, count))

    def print_last_home_matches(self, competition_id, count=5):
        """
        Print last matches for a team in given competition
        :param competition_id: 
        :param count: 
        :return: 
        """
        print(self.database.get_last_home_matches(self.url_to_club_page, competition_id, count))

    def print_last_away_matches(self, competition_id, count=5):
        """
        Print last matches for a team in given competition
        :param competition_id: 
        :param count: 
        :return: 
        """
        print(self.database.get_last_away_matches(self.url_to_club_page, competition_id, count))
