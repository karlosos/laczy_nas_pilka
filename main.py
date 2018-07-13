#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Scrapper import Parser
from Database import Database
from Updater import Updater
import sqlite3

updater = Updater("newstal.db", "https://www.laczynaspilka.pl/druzyna-sezon/stal-szczecin/208849.html", "https://www.laczynaspilka.pl/druzyna/stal-szczecin,208849.html")
updater.update()
updater.print_scored_goals()
updater.print_conceded_goals()
updater.print_squad()