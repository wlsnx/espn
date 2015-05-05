# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst


class EspnLoader(ItemLoader):

    default_output_processor = TakeFirst()


class Item(scrapy.Item):

    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)
        for key, value in self.fields.items():
            if key not in self and "default" in value:
                self[key] = value["default"]


class TeamItem(Item):

    name = scrapy.Field()
    name_en = scrapy.Field()
    city = scrapy.Field()
    id = scrapy.Field()
    type = scrapy.Field()
    league_id = scrapy.Field()
    espn_name = scrapy.Field()


class PlayerItem(Item):

    name = scrapy.Field()
    name_en = scrapy.Field()
    position = scrapy.Field()
    height = scrapy.Field()
    weight = scrapy.Field()
    country = scrapy.Field()
    country_en = scrapy.Field()
    birthday = scrapy.Field()
    #age = scrapy.Field()
    team_id = scrapy.Field()
    number = scrapy.Field()
    id = scrapy.Field()


class MatchItem(Item):

    date = scrapy.Field()
    id = scrapy.Field()
    finish = scrapy.Field()
    home_id = scrapy.Field()
    away_id = scrapy.Field()
    home_score = scrapy.Field()
    away_score = scrapy.Field()
    league_id = scrapy.Field()
    espn_id = scrapy.Field()
    time = scrapy.Field()

