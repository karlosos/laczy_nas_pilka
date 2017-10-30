import sqlite3


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.db_connection = self.create_db()
        self.create_schema()

    def create_db(self):
        db_connection = sqlite3.connect(self.db_name)
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

    def add_scores(self, scores):
        cursor = self.db_connection.cursor()
        for score in scores:
            try:
                cursor.execute("INSERT INTO mecz VALUES(?, ?, ?, ?, ?)", score)
            except sqlite3.IntegrityError:
                pass
        self.db_connection.commit()

    def add_squads(self, squads):
        cursor = self.db_connection.cursor()
        for squad in squads:
            try:
                cursor.execute("INSERT INTO squads VALUES(?, ?, ?, ?, ?, ?, ?)", squad)
            except sqlite3.IntegrityError:
                pass
        self.db_connection.commit()

    def add_events(self, events):
        cursor = self.db_connection.cursor()
        for event in events:
            try:
                cursor.execute("INSERT INTO event VALUES(?, ?, ?, ?, ?)", event)
            except sqlite3.IntegrityError:
                print(event)
        self.db_connection.commit()

    def add_teams(self, teams):
        cursor = self.db_connection.cursor()
        for team_id, team_name in teams.items():
            try:
                cursor.execute("INSERT INTO team VALUES(?, ?)", (team_id, team_name))
            except sqlite3.IntegrityError:
                print(team_name)
        self.db_connection.commit()
