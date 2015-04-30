#!/usr/bin/env python
# encoding: utf-8


import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class League(Base):

    __tablename__ = "yt_league"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(60))
    name_cn = sa.Column(sa.String(60))
    short_name = sa.Column(sa.String(30))
    short_name_cn = sa.Column(sa.String(30))
    is_cup = sa.Column(sa.Boolean)
    espn_name = sa.Column(sa.String(60))


league_team = sa.Table("league_team",
                       Base.metadata,
                       sa.Column("team_id", sa.Integer, sa.ForeignKey("yt_team.id")),
                       sa.Column("league_id", sa.Integer, sa.ForeignKey("yt_league.id")))


class Team(Base):

    __tablename__ = "yt_team"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(60))
    name_en = sa.Column(sa.String(60))
    city = sa.Column(sa.String(100))
    type = sa.Column(sa.String(10))
    league = relationship("League", secondary=league_team, backref="team")
    ground = sa.Column(sa.String(40))
    letter = sa.Column(sa.String(10))
    espn_name = sa.Column(sa.String(60))
    #TODO:create player table
    #master = sa.Column(sa.Integer, sa.ForeignKey("yt_player.id"))

    def __init__(self, **kwargs):
        super(Team, self).__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

