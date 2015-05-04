# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule



class PlayerSpider(CrawlSpider):
    name = 'player'
    allowed_domains = ['espnfc.com']
    #start_urls = ['http://www.espnfc.com/']

    rules = (
        Rule(LinkExtractor(allow=r'player/\d+/.*'), callback='parse_player', follow=True),
    )

    def parse_item(self, response):
        #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        #i['name'] = response.xpath('//div[@id="name"]').extract()
        #i['description'] = response.xpath('//div[@id="description"]').extract()
        pass
