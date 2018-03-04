import matplotlib.pyplot as plt
import numpy as np

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

        for goal in scored_goals:
            goals[goal[0]] = goals[goal[0]] + 1

        xp = np.linspace(0, 95, 950)
        z = np.polyfit(range(0,150),goals, 2)
        p = np.poly1d(z)

        plt.plot(goals)
        print(p(xp))
        plt.plot(p(xp))
        plt.title("Bramki liga okręgowa")
        plt.xlabel("Minuta")
        plt.ylabel("Bramki")
        plt.axis([0, 95, 0, 30])

        fig = plt.gcf()
        plt.show()

        print(goals)