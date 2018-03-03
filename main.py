#!/usr/bin/env python3
from Scrapper import Parser
from Database import Database

database = Database("stal.db")
#url_to_matches_list_page = "https://www.laczynaspilka.pl/druzyna-sezon/stal-szczecin/208849.html"
#url_to_club_page = "https://www.laczynaspilka.pl/druzyna/stal-szczecin,208849.html"
url_to_matches_list_page = "https://www.laczynaspilka.pl/rozgrywki/nizsze-ligi,20725.html"
url_to_club_page = None
parser = Parser(url_to_matches_list_page, url_to_club_page)
database.add_scores(parser.matches)
database.add_squads(parser.squads)
database.add_events(parser.events)
database.add_teams(parser.teams)
database.add_competitions(parser.competitions)

# alanyze two teams
