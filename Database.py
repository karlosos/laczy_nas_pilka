import sqlite3

from sqlalchemy import Table, Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from sqlalchemy import create_engine
from sqlalchemy import exc
from sqlalchemy.sql import func

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
    team = relationship(lambda: Team, backref=backref('sqads'), uselist=True)


class Competition(Base):
    __tablename__ = 'competition'
    id = Column(String, primary_key=True)
    name = Column(String)


class Player(Base):
    __tablename__ = 'player'
    id = Column(String, primary_key=True)
    name = Column(String)
    date_of_birth = Column(Date)


class Database:
    def __init__(self, db_name):
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
            try:
                s.add(db_match)
                s.commit()
            except exc.IntegrityError:
                s.rollback()

    def add_players(self, players):
        s = self.session()
        for player in players:
            db_player = Player()
            db_player.id = player[0]
            db_player.name = player[1]
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
        for team_id, team_name in teams.items():
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
        print(squad)
