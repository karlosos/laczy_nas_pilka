#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from okregowastats.Updater import Updater

updater = Updater("newstal.db", "https://www.laczynaspilka.pl/druzyna-sezon/stal-szczecin/208849.html", "https://www.laczynaspilka.pl/druzyna/stal-szczecin,208849.html")
#updater.update()
updater.print_scored_goals()
updater.print_conceded_goals()
updater.print_squad()
updater.print_form()
updater.print_average_points_per_match("https://www.laczynaspilka.pl/rozgrywki/nizsze-ligi,20725.html")
updater.print_win_percentage("https://www.laczynaspilka.pl/rozgrywki/nizsze-ligi,20725.html")
updater.print_draw_percentage("https://www.laczynaspilka.pl/rozgrywki/nizsze-ligi,20725.html")
updater.print_lose_percentage("https://www.laczynaspilka.pl/rozgrywki/nizsze-ligi,20725.html")