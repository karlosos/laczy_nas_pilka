from sqlalchemy import Table, Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationships, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Match(Base):
    __tablename__ = 'match'
    id = Column(String, primary_key=True)
    team_a_id = Column(String, ForeignKey('team.id'))
    team_b_id = Column(String, ForeignKey('team.id'))
    score_a = Column(Integer)
    score_b = Column(Integer)
    competition_id = Column(String, ForeignKey('competition.id'))
    # team a team b score a score b competition_id

class Team(Base):
    __tablename__ = 'team'
    id = Column(String, primary_key=True)
    name = Column(String)

class Event(Base):
    __tablename__ = 'event'
    id = Column(String, primary_key=True)
    type = Column(String, primary_key=True)
    time = Column(Integer, primary_key=True)
    player = Column(String, ForeignKey('player.id'), primary_key=True)
    team = Column(String, ForeignKey('team.id'))

Squad = Table('squad',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('player_id', String, ForeignKey('player.id')),
    Column('match_id', String, ForeignKey('match.id')),
    Column('number', Integer),
    Column('time_played', Integer),
    Column('is_first_eleven', Integer),
    Column('team_id', String, ForeignKey('team.id')))

class Competition(Base):
    __tablename__ = 'competition'
    id = Column(String, primary_key=True)
    name = Column(String)

class Player(Base):
    __tablename__ = 'player'
    id = Column(String, primary_key=True)
    name = Column(String)
    date_of_birht = Column(Date)

from sqlalchemy import create_engine
engine = create_engine('sqlite:///new.db')

from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)
