from unittest import TestCase
import unittest.mock
import io

from okregowastats.Updater import Updater

class TestUpdater(TestCase):
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def assert_stdout_average_points_per_match(self, updater, competition, expected_output, mock_stdout):

        updater.print_average_points_per_match(competition)
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    def test_print_average_points_per_match_number(self):
        updater = Updater("test.db", "https://www.laczynaspilka.pl/druzyna-sezon/stal-szczecin/208849.html",
                          "https://www.laczynaspilka.pl/druzyna/stal-szczecin,208849.html")
        self.assert_stdout_average_points_per_match(updater, "https://www.laczynaspilka.pl/rozgrywki/nizsze-ligi,20725.html", '1.4333333333333333\n')
