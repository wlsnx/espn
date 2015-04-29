# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


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

