#!/usr/bin/env python3
from Scrapper import Parser

url_to_matches_list_page = "https://www.laczynaspilka.pl/druzyna-sezon/stal-szczecin/208849.html"
url_to_club_page = "https://www.laczynaspilka.pl/druzyna/stal-szczecin,208849.html"
parser = Parser(url_to_matches_list_page, url_to_club_page)

