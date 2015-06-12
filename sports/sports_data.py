#!/usr/bin/env python
# encoding: utf-8


import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Item(object):

    def __init__(self, **kwargs):
        super(Team, self).__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class League(Base):

    __tablename__ = "yt_league"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(60))
    name_cn = sa.Column(sa.String(60))
    short_name = sa.Column(sa.String(30))
    short_name_cn = sa.Column(sa.String(30))
    is_cup = sa.Column(sa.Boolean)
    #espn_name = sa.Column(sa.String(60))


league_team = sa.Table("league_team",
                       Base.metadata,
                       sa.Column("team_id", sa.Integer, sa.ForeignKey("yt_team.id")),
                       sa.Column("league_id", sa.Integer, sa.ForeignKey("yt_league.id")))


#class LeagueTeam(Base):

    #__tablename__ = "league_team"

    #team_id = sa.Column(sa.Integer, default=0, sa.ForeignKey("yt_team.id"))
    #league_id = sa.Column(sa.Integer, default=0, sa.ForeignKey("yt_league.id"))

    #__table_args__ = (sa.PrimaryKeyConstraint(team_id, league_id), )


class Team(Base, Item):

    __tablename__ = "yt_team"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(60))
    name_en = sa.Column(sa.String(60))
    city = sa.Column(sa.String(100))
    type = sa.Column(sa.String(10))
    league = relationship("League", secondary=league_team, backref="team")
    ground = sa.Column(sa.String(40))
    letter = sa.Column(sa.String(10))
    #espn_name = sa.Column(sa.String(60))
    player = relationship("TeamPlayer")
    #TODO:create player table
    #master = sa.Column(sa.Integer, default=0, sa.ForeignKey("yt_manager.id"))


#player_number = sa.Table("player_number",
                         #Base.metadata,
                         #sa.Column("player_id", sa.Integer, default=0, sa.ForeignKey("yt_player.id")),
                         #sa.Column("team_id", sa.Integer, default=0, sa.ForeignKey("yt_team.id")),
                         #sa.Column("number", sa.SmallInteger, default=0))


class TeamPlayer(Base):

    __tablename__ = "team_player"

    #id = sa.Column(sa.Integer, default=0)
    player_id = sa.Column(sa.Integer, sa.ForeignKey("yt_player.id"))
    team_id = sa.Column(sa.Integer, sa.ForeignKey("yt_team.id"))
    number = sa.Column(sa.SmallInteger, default=0)

    __table_args__ = (sa.PrimaryKeyConstraint(player_id, team_id), )


class Player(Base, Item):

    __tablename__ = "yt_player"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(30))
    name_en = sa.Column(sa.String(30))
    position = sa.Column(sa.String(10))
    #number = sa.Column(sa.SmallInteger, default=0)
    height = sa.Column(sa.Float())
    weight = sa.Column(sa.Float())
    country = sa.Column(sa.String(30))
    country_en = sa.Column(sa.String(30))
    birthday = sa.Column(sa.Date())
    #age = sa.Column(sa.SmallInteger, default=0)
    team = relationship("TeamPlayer")
    letter = sa.Column(sa.String(10), default="")


class Match(Base, Item):

    __tablename__ = "yt_match"

    id = sa.Column(sa.Integer, primary_key=True)
    espn_id = sa.Column(sa.Integer, default=0)
    league_id = sa.Column(sa.Integer, sa.ForeignKey("yt_league.id"))
    finish = sa.Column(sa.SmallInteger, default=0)
    home_score = sa.Column(sa.SmallInteger, default=-1)
    away_score = sa.Column(sa.SmallInteger, default=-1)
    home_id = sa.Column(sa.Integer, sa.ForeignKey("yt_team.id"))
    away_id = sa.Column(sa.Integer, sa.ForeignKey("yt_team.id"))
    date = sa.Column(sa.Date)
    time = sa.Column(sa.Time)
    m_time = sa.Column(sa.SmallInteger, default=0)


class MatchFootball(Base, Item):

    __tablename__ = "match_football"

    id = sa.Column(sa.Integer, primary_key=True)
    match_id = sa.Column(sa.Integer, sa.ForeignKey("yt_match.id"))
    home_score = sa.Column(sa.SmallInteger, default=0)
    away_score = sa.Column(sa.SmallInteger, default=0)
    home_shot = sa.Column(sa.SmallInteger, default=0)
    away_shot = sa.Column(sa.SmallInteger, default=0)
    home_shots = sa.Column(sa.SmallInteger, default=0)
    away_shots = sa.Column(sa.SmallInteger, default=0)
    home_fouls = sa.Column(sa.SmallInteger, default=0)
    away_fouls = sa.Column(sa.SmallInteger, default=0)
    home_corner = sa.Column(sa.SmallInteger, default=0)
    away_corner = sa.Column(sa.SmallInteger, default=0)
    home_offside = sa.Column(sa.SmallInteger, default=0)
    away_offside = sa.Column(sa.SmallInteger, default=0)
    home_ball_possession = sa.Column(sa.SmallInteger, default=0)
    away_ball_possession = sa.Column(sa.SmallInteger, default=0)
    home_yellow_card = sa.Column(sa.SmallInteger, default=0)
    away_yellow_card = sa.Column(sa.SmallInteger, default=0)
    home_red_card = sa.Column(sa.SmallInteger, default=0)
    away_red_card = sa.Column(sa.SmallInteger, default=0)
    home_saving = sa.Column(sa.SmallInteger, default=0)
    away_saving = sa.Column(sa.SmallInteger, default=0)
    #date = sa.Column(sa.Date)
    #time = sa.Column(sa.Time)


class MatchFootballDetails(Base, Item):

    __tablename__ = "match_football_details"

    id = sa.Column(sa.Integer, primary_key=True)
    match_id = sa.Column(sa.Integer, sa.ForeignKey("yt_match.id"))
    min = sa.Column(sa.SmallInteger, default=0)
    team = sa.Column(sa.SmallInteger, default=0)
    type = sa.Column(sa.SmallInteger, default=0)
    player_a = sa.Column(sa.String(30))
    player_a_id = sa.Column(sa.Integer, sa.ForeignKey("yt_player.id"))
    player_b = sa.Column(sa.String(30))
    player_b_id = sa.Column(sa.Integer, sa.ForeignKey("yt_player.id"))


class PlayerMatch(Base, Item):

    __tablename__ = "player_match"

    id = sa.Column(sa.Integer, primary_key=True)
    match_id = sa.Column(sa.Integer, sa.ForeignKey("yt_match.id"))
    player_id = sa.Column(sa.Integer, sa.ForeignKey("yt_player.id"))
    fouls_commited = sa.Column(sa.SmallInteger, default=0)
    fouls_suffered = sa.Column(sa.SmallInteger, default=0)
    red_card = sa.Column(sa.SmallInteger, default=0)
    yellow_card = sa.Column(sa.SmallInteger, default=0)
    assists = sa.Column(sa.SmallInteger, default=0)
    goals = sa.Column(sa.SmallInteger, default=0)
    shots = sa.Column(sa.SmallInteger, default=0)
    shots_goal = sa.Column(sa.SmallInteger, default=0)
    offside = sa.Column(sa.SmallInteger, default=0)
    saving = sa.Column(sa.SmallInteger, default=0)
    appear = sa.Column(sa.SmallInteger, default=0)

