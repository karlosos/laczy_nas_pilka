import matplotlib.pyplot as plt

class Analyser:
    def __init__(self, db):
        self.db = db

    def get_all_goals(self):
        cur = self.db.cursor()
        cur.execute("SELECT minuta, match_id from event WHERE typ = 'i-report-ball' ORDER BY minuta ASC")
        scored_goals = cur.fetchall()
        goals = []
        for i in range(0,150):
            goals.append(0);

        print(goals)
        for goal in scored_goals:
            print(goal[0])
            goals[goal[0]] = goals[goal[0]] + 1

        print(scored_goals)