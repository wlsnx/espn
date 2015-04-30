# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from espn.items import TeamItem
#import sys
from sports.sports_data import Team, League
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import NotConfigured
from espn.spiders.team import TeamSpider


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
        tp.session = sessionmaker(db)()
        return tp

    def close_spider(self, spider):
        if isinstance(spider, TeamSpider):
            self.session.commit()

