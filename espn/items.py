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
    m_time = scrapy.Field()

class FootballItem(Item):
    home_shot = scrapy.Field()
    away_shot = scrapy.Field()
    home_shots = scrapy.Field()
    away_shots = scrapy.Field()
    home_fouls = scrapy.Field()
    away_fouls = scrapy.Field()
    home_corner = scrapy.Field()
    away_corner = scrapy.Field()
    home_offside = scrapy.Field()
    away_offside = scrapy.Field()
    home_ball_possession = scrapy.Field()
    away_ball_possession = scrapy.Field()
    home_yellow_card = scrapy.Field()
    away_yellow_card = scrapy.Field()
    home_red_card = scrapy.Field()
    away_red_card = scrapy.Field()
    home_saving = scrapy.Field()
    away_saving = scrapy.Field()
    home_score = scrapy.Field()
    away_score = scrapy.Field()
    date = scrapy.Field()
    time = scrapy.Field()
    match_id = scrapy.Field()


class FootballDetailsItem(Item):
    match_id = scrapy.Field()
    min = scrapy.Field()
    team = scrapy.Field()
    type = scrapy.Field()
    player_a = scrapy.Field()
    player_a_id = scrapy.Field()
    player_b = scrapy.Field()
    player_b_id = scrapy.Field()


class PlayerMatchItem(Item):
    match_id = scrapy.Field()
    player_id = scrapy.Field()
    fouls_commited = scrapy.Field()
    fouls_suffered = scrapy.Field()
    red_card = scrapy.Field()
    yellow_card = scrapy.Field()
    assists = scrapy.Field()
    goals = scrapy.Field()
    shots = scrapy.Field()
    shots_goal = scrapy.Field()
    saving = scrapy.Field()
    offside = scrapy.Field()

