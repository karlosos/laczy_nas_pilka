from unittest import TestCase
from okregowastats.Database import Database

class TestDatabase(TestCase):
    def test_get_average_points_per_match(self):
        database = Database("test.db")
        url_to_matches_list_page = "https://www.laczynaspilka.pl/druzyna-sezon/stal-szczecin/208849.html"
        url_to_club_page = "https://www.laczynaspilka.pl/druzyna/stal-szczecin,208849.html"
        competition = "https://www.laczynaspilka.pl/rozgrywki/nizsze-ligi,20725.html"
        self.assertAlmostEqual(database.get_average_points_per_match(url_to_club_page, competition), 1.4333, places=2)
