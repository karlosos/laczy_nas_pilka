from unittest import TestCase
from okregowastats.Database import Database

class TestDatabase(TestCase):
    def test_get_average_points_per_match(self):
        database = Database("test.db")
        url_to_matches_list_page = "https://www.laczynaspilka.pl/druzyna-sezon/stal-szczecin/208849.html"
        url_to_club_page = "https://www.laczynaspilka.pl/druzyna/stal-szczecin,208849.html"
        competition = "https://www.laczynaspilka.pl/rozgrywki/nizsze-ligi,20725.html"
        self.assertAlmostEqual(database.get_average_points_per_match(url_to_club_page, competition), 1.4333, places=2)

    def test_get_number_of_matches_sum(self):
        database = Database("test.db")
        url_to_matches_list_page = "https://www.laczynaspilka.pl/druzyna-sezon/stal-szczecin/208849.html"
        url_to_club_page = "https://www.laczynaspilka.pl/druzyna/stal-szczecin,208849.html"
        competition = "https://www.laczynaspilka.pl/rozgrywki/nizsze-ligi,20725.html"
        number_of_matches = database.get_number_of_matches(url_to_club_page, competition)
        self.assertEqual(number_of_matches[3], number_of_matches[0] + number_of_matches[1] + number_of_matches[2])

    def test_get_win_draw_lose_percentage_sum(self):
        database = Database("test.db")
        url_to_matches_list_page = "https://www.laczynaspilka.pl/druzyna-sezon/stal-szczecin/208849.html"
        url_to_club_page = "https://www.laczynaspilka.pl/druzyna/stal-szczecin,208849.html"
        competition = "https://www.laczynaspilka.pl/rozgrywki/nizsze-ligi,20725.html"
        win = database.get_win_percentage(url_to_club_page, competition)
        draw = database.get_draw_percentage(url_to_club_page, competition)
        lose = database.get_lose_percentage(url_to_club_page, competition)
        self.assertAlmostEqual(win+draw+lose, 1)
