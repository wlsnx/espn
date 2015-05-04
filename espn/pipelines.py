# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from espn.items import TeamItem, PlayerItem
#import sys
from sports.sports_data import Team, League, TeamPlayer, Player
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import NotConfigured
#from espn.spiders.team import TeamSpider


class TeamPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, TeamItem):
            team = self.session.query(Team).filter_by(id=item["id"]).first()
            league_id = item.pop("league_id")
            if not team:
                team = Team(**item)
                self.session.add(team)
            else:
                team.update(**item)
            league = self.session.query(League).filter_by(id=league_id).first()
            if league and league not in team.league:
                team.league.append(league)
        return item

    @classmethod
    def from_settings(cls, settings):
        tp = cls()
        server = settings.get("SERVER")
        if not server:
            raise NotConfigured
        db = sa.create_engine(server)
        tp.Session = sessionmaker(db)
        tp.session = tp.Session()
        return tp

    def close_spider(self, spider):
        self.session.commit()


import re
from datetime import datetime


class PlayerPipeline(TeamPipeline):

    bracket = re.compile("\(([0-9.]+)\s?\w+\)")

    def process_item(self, item, spider):
        if isinstance(item, PlayerItem):
            item = self.tidy_item(item)
            team_id = item.pop("team_id", None)
            number = item.pop("number", None)
            team_player = TeamPlayer(team_id=team_id,
                                     number=number)
            player = self.session.query(Player).filter_by(id=item["id"]).first()
            if not player:
                player = Player(**item)
            else:
                player.update(**item)
            team_player = self.session.query(TeamPlayer).filter_by(team_id=team_id,
                                                                   player_id=player.id).first()
            if not team_player:
                team_player = TeamPlayer(number=number,
                                         team_id=team_id)
                player.team.append(team_player)
            team_player.number = number
            self.session.add(player)
        return item

    def tidy_item(self, item):
        _item = item.copy()
        if "height" in _item:
            matched = self.bracket.search(_item["height"])
            if matched:
                height =matched.group(1)
                _item["height"] = int(float(height) * 100)
        if "weight" in _item:
            matched = self.bracket.search(_item["weight"])
            if matched:
                weight = matched.group(1)
                _item["weight"] = weight
        if "birthday" in _item:
            birthday = datetime.strptime(_item["birthday"], "%B %d, %Y ")
            _item["birthday"] = birthday
        return _item

