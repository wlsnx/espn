# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from espn.items import TeamItem
#import sys
from sports.sports_data import Team
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import NotConfigured


class TeamPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, TeamItem):
            session = self.session()
            if not session.query(Team).filter_by(**item):
                team = Team(**item)
                session.add(team)
                session.commit()
        return item

    @classmethod
    def from_settings(cls, settings):
        tp = cls()
        server = settings.get("SERVER")
        if not server:
            raise NotConfigured
        db = sa.create_engine(server)
        tp.session = sessionmaker(db)
        return tp

