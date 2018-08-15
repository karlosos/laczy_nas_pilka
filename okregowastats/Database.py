import sqlite3

from sqlalchemy import Table, Column, String, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from sqlalchemy import desc
from sqlalchemy import create_engine
from sqlalchemy import exc
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Team(Base):
    __tablename__ = 'team'
    id = Column(String, primary_key=True)
    name = Column(String)


class Match(Base):
    __tablename__ = 'match'
    id = Column(String, primary_key=True)
    team_a_id = Column(String, ForeignKey('team.id'))
    team_a = relationship(Team, foreign_keys=[team_a_id], backref=backref('matches_home', uselist=True))
    team_b_id = Column(String, ForeignKey('team.id'))
    team_b = relationship(Team, foreign_keys=[team_b_id], backref=backref('matches_away', uselist=True))
    score_a = Column(Integer)
    score_b = Column(Integer)
    competition_id = Column(String, ForeignKey('competition.id'))
    competition = relationship(lambda: Competition, backref=backref('matches', uselist=True))
    date = Column(DateTime)
    # team a team b score a score b competition_id


class Event(Base):
    __tablename__ = 'event'
    match_id = Column(String, ForeignKey('match.id'), primary_key=True, )
    match = relationship(Match, backref=backref('events'), uselist=True)
    type = Column(String, primary_key=True)
    time = Column(Integer, primary_key=True)
    player_id = Column(String, ForeignKey('player.id'), primary_key=True)
    player = relationship(lambda: Player, backref=backref('events'), uselist=True)
    team_id = Column(String, ForeignKey('team.id'))
    team = relationship(Team, backref=backref('events'), uselist=True)


class Squad(Base):
    __tablename__ = 'squad'
    player_id = Column(String, ForeignKey('player.id'), primary_key=True)
    player = relationship(lambda: Player, backref=backref('appearances'), uselist=True)
    match_id = Column(String, ForeignKey('match.id'), primary_key=True)
    match = relationship(Match, backref=backref('squads'), uselist=True)
    number = Column(Integer)
    time_played = Column(Integer)
    is_first_eleven = Column(Integer)
    team_id = Column(String, ForeignKey('team.id'))
    team = relationship(lambda: Team, backref=backref('squads'), uselist=True)


class Competition(Base):
    __tablename__ = 'competition'
    id = Column(String, primary_key=True)
    name = Column(String)


class Player(Base):
    __tablename__ = 'player'
    id = Column(String, primary_key=True)
    name = Column(String)
    date_of_birth = Column(Date)
    team_id = Column(String, ForeignKey('team.id'))
    team = relationship(lambda: Team, backref=backref('sqads'), uselist=True)
    matches = Column(Integer)
    minutes = Column(Integer)
    goals = Column(Integer)
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)



class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.engine = create_engine('sqlite:///' + db_name)
        self.session = sessionmaker()
        self.session.configure(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def add_scores(self, matches):
        s = self.session()
        for match in matches:
            db_match = Match()
            db_match.id = match[0]
            db_match.team_a_id = match[1]
            db_match.team_b_id = match[2]
            db_match.score_a = match[3]
            db_match.score_b = match[4]
            db_match.competition_id = match[5]
            db_match.date = match[6]
            try:
                s.add(db_match)
                s.commit()
            except exc.IntegrityError:
                s.rollback()

    def add_players(self, players):
        s = self.session()
        for player in players:
            # player_link, birth, club, matches, minutes, goals, yellow_cards, red_cards
            db_player = Player()
            db_player.id = player[0]
            db_player.name = player[1]
            if player[2] != '':
                db_player.date_of_birth = datetime.strptime(player[2], "%d.%m.%Y").date()
            else:
                db_player.date_of_birth = None


            db_player.team_id = player[3]
            db_player.matches = player[4]
            db_player.minutes = player[5]
            db_player.goals = player[6]
            db_player.yellow_cards = player[7]
            db_player.red_cards = player[8]
            try:
                s.add(db_player)
                s.commit()
            except exc.IntegrityError:
                print("Duplicate error " + db_player.name)
                s.rollback()

    def add_squads(self, squads):
        s = self.session()
        for squad in squads:
            # player_name, player_id, numer, time_played, sklad, team_id, match_id
            sq = Squad()
            sq.player_id = squad[1]
            sq.number = squad[2]
            sq.time_played = squad[3]
            sq.is_first_eleven = squad[4]
            sq.team_id = squad[5]
            sq.match_id = squad[6]
            try:
                s.add(sq)
                s.commit()
            except exc.IntegrityError:
                s.rollback()

    def add_events(self, events):
        s = self.session()
        for event in events:
            # match_id minuta typ zawodnik team
            e = Event()
            e.match_id = event[0]
            e.time = event[1]
            e.type = event[2]
            e.player_id = event[3]
            e.team_id = event[4]
            try:
                s.add(e)
                s.commit()
            except exc.IntegrityError:
                s.rollback()

    def add_teams(self, teams):
        # team_id, name
        s = self.session()
        for team_name, team_id in teams.items():
            team = Team()
            team.id = team_id
            team.name = team_name
            try:
                s.add(team)
                s.commit()
            except exc.IntegrityError:
                s.rollback()

    def add_competitions(self, competitions):
        # id name
        s = self.session()
        for competition_id, competition_name in competitions.items():
            competition = Competition()
            competition.id = competition_id
            competition.name = competition_name
            try:
                s.add(competition)
                s.commit()
            except exc.IntegrityError:
                s.rollback()

    def get_scored_goals(self, club_id):
        s = self.session()
        goals = [u.__dict__ for u in
                 s.query(Event).filter(Event.type == "i-report-ball").filter(Event.team_id == club_id).all()]
        return goals

    def get_conceded_goals(self, club_id):
        s = self.session()
        goals = [u.__dict__ for u in s.query(Event).filter(Event.type == "i-report-ball").filter(
            or_(Event.match.any(team_a_id=club_id), Event.match.any(team_b_id=club_id))).filter(
            Event.team_id != club_id).all()]
        return goals

    def get_squad(self, club_id):
        import timeit
        squad = []
        s = self.session()
        players = s.query(Player).filter(Player.appearances.any(team_id=club_id)).all()
        for player in players:
            # TODO minutes player and last number - they return sqlalchemy.orm.query.Query object
            start = timeit.default_timer()
            goals = s.query(Event).filter(Event.player_id == player.id,
                                          Event.type == 'i-report-ball').count()
            yellow_cards = s.query(Event).filter(Event.player_id == player.id,
                                                 Event.type == 'i-yellow-card').count()
            red_cards = s.query(Event).filter(Event.player_id == player.id,
                                              Event.type == 'i-red-card').count()
            last_number = s.query(Squad.number).filter(Squad.player_id == player.id).limit(1)
            numbers = s.query(Squad.number, func.count(Squad.number)).filter(Squad.player_id == player.id).group_by(
                Squad.number).all()
            minutes_played = s.query(func.sum(Squad.time_played)).filter(Squad.player_id == player.id)
            squad.append((player.name, last_number, numbers, minutes_played, goals, yellow_cards, red_cards))
            stop = timeit.default_timer()
            # print(stop - start)
        return squad

    def get_squad_sql(self, club_id):
        import timeit
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        cur.execute(
            "SELECT player_id, SUM(time_played) FROM squad INNER JOIN player ON (squad.player_id = player.id) WHERE squad.team_id = ? GROUP BY `player_id` ORDER BY sum(time_played) DESC", (club_id,))
        team_squad_tmp = cur.fetchall()
        team_squad = []
        for player in team_squad_tmp:
            player_id = player[0]
            start = timeit.default_timer()
            cur.execute(
                "SELECT number, count(number) FROM squad WHERE player_id = ? GROUP BY number ORDER BY count(number) DESC",
                (player_id,))
            numbers = cur.fetchall()
            cur.execute("SELECT number FROM squad WHERE player_id = ? limit 1", (player_id,))
            last_number = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM event WHERE player_id=? AND type='i-report-ball'", (player_id,))
            goals = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM event WHERE player_id=? AND type='i-yellow-card'", (player_id,))
            yellow_cards = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM event WHERE player_id=? AND type='i-red-card'", (player_id,))
            red_cards = cur.fetchone()[0]
            team_squad.append((player[0], player[1], numbers, last_number, goals, yellow_cards, red_cards));
            stop = timeit.default_timer()
            # print(stop - start)
        return team_squad

    def get_team_form(self, club_id, numer_of_matches):
        """
        Get last matches and return list
        
        List contains tuples of matches. Each tuple has format: result, name of team_a, 
        name of team_b, score_a, score_b, date.
        
        :param club_id: id of club  
        :param numer_of_matches: how many last matches to get
        :return: list of tuples with format like ('L', 'STAL SZCZECIN', 'CHEMIK POLICE', 0, 7)
        """
        s = self.session()
        form_query = s.query(Match).filter(or_(Match.team_a_id == club_id, Match.team_b_id == club_id))\
            .order_by(desc(Match.date)).limit(numer_of_matches).all()

        form = []
        for match in form_query:
            result = ""
            if (match.score_a == match.score_b):
                result = "D"
            elif (match.score_a > match.score_b and match.team_a_id == club_id):
                result = "W"
            elif (match.score_a < match.score_b and match.team_b_id == club_id):
                result = "W"
            else:
                result = "L"

            form.append((result, match.team_a.name, match.team_b.name, match.score_a, match.score_b, match.date))

        return form

    def get_average_points_per_match(self, club_id, competition_id = ""):
        """
        Return average points per match
        
        :param club_id: 
        :return: 
        """

        s = self.session()
        if (competition_id == ""):
            matches_query = s.query(Match).filter(or_(Match.team_a_id == club_id, Match.team_b_id == club_id)).all()
        else:
            matches_query = s.query(Match).filter(Match.competition_id == competition_id)\
                .filter(or_(Match.team_a_id == club_id, Match.team_b_id == club_id)).all()

        number_of_matches = len(matches_query)

        points = 0
        # calculate points
        for match in matches_query:
            if (match.score_a == match.score_b):
                points = points + 1
            elif (match.score_a > match.score_b and match.team_a_id == club_id):
                points = points + 3
            elif (match.score_a < match.score_b and match.team_b_id == club_id):
                points = points + 3

        return points/number_of_matches

    def get_number_of_matches(self, club_id, competition_id=""):
        """
        Return number of wins, loses, draws and total matches for club in competition. 
        If competition_id is not given then calculate wins
        for all matches for team.
        :param club_id: 
        :param competition_id: 
        :return: 
        """
        s = self.session()
        if (competition_id == ""):
            matches_query = s.query(Match).filter(or_(Match.team_a_id == club_id, Match.team_b_id == club_id)).all()
        else:
            matches_query = s.query(Match).filter(Match.competition_id == competition_id) \
                .filter(or_(Match.team_a_id == club_id, Match.team_b_id == club_id)).all()

        number_of_matches = len(matches_query)

        wins = 0
        loses = 0
        draws = 0
        # calculate points
        for match in matches_query:
            print(match.team_a.name + " " + str(match.score_a) + ":" + str(match.score_b) + " " + match.team_b.name)
            if (match.score_a == match.score_b):
                draws += 1
            elif (match.score_a > match.score_b and match.team_a_id == club_id):
                wins += 1
            elif (match.score_a < match.score_b and match.team_b_id == club_id):
                wins += 1
            else:
                loses += 1

        return (wins, draws, loses, number_of_matches)

    def get_win_percentage(self, club_id, competition_id=""):
        """
        Return ratio of win to all matches
        :param club_id: 
        :param competition_id: 
        :return: 
        """
        matches = self.get_number_of_matches(club_id, competition_id)
        return matches[0] / matches[3]

    def get_draw_percentage(self, club_id, competition_id=""):
        """
        Return ratio of draws to all matches
        :param club_id: 
        :param competition_id: 
        :return: 
        """
        matches = self.get_number_of_matches(club_id, competition_id)
        return matches[1] / matches[3]

    def get_lose_percentage(self, club_id, competition_id=""):
        """
        Return ratio of loses to all matches
        :param club_id: 
        :param competition_id: 
        :return: 
        """
        matches = self.get_number_of_matches(club_id, competition_id)
        return matches[2] / matches[3]