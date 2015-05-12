# -*- coding: utf-8 -*-
import scrapy
#from scrapy.contrib.linkextractors import LinkExtractor
#from scrapy.contrib.spiders import CrawlSpider, Rule

from espn.items import MatchItem


class SeasonSpider(scrapy.Spider):
    name = 'season'
    allowed_domains = ['espnfc.com']
    #start_urls = ['http://www.espnfc.com/scores']

    custom_settings = {"CLOSESPIDER_PAGECOUNT": 366}

    statistics_url = "http://www.espnfc.com/gamecast/statistics/id/{}/statistics.html"

    #rules = (
        #Rule(LinkExtractor(allow="scores\?date=\d+"), callback="parse_season"),
    #)

    def __init__(self, date=None, **kwargs):
        super(SeasonSpider, self).__init__(**kwargs)
        if date:
            self.start_urls = ["http://www.espnfc.com/scores?date={}".format(date)]
        else:
            self.start_urls = ["http://www.espnfc.com/scores"]

    #def parse_start_request(self, response):
        #return self.parse_season(response)

    def parse(self, response):
        #match_loader = EspnLoader(MatchItem())
        leagues = response.xpath("//div[@class='score-league']")
        for league in leagues:
            league_id = league.xpath("@data-league-id").extract()[0]
            games = league.xpath(".//div[@class='score full']")
            for game in games:
                match_id = game.xpath("@data-gameid").extract()[0]
                match = MatchItem(espn_id=match_id,
                                  league_id=league_id)
                yield scrapy.Request(self.statistics_url.format(match_id),
                                     callback=self.parse_match,
                                     meta={"match": match})
        tomorrow = response.xpath("//a[@class='next']/@href").extract()[0]
        yield scrapy.Request(tomorrow)

    def parse_match(self, response):
        match = response.meta["match"]
        away_id = response.xpath("//div[@class='team away']/@id").extract()[0]
        away_id = away_id.split("-")[1]
        match["away_id"] = away_id
        home_id = response.xpath("//div[@class='team home']/@id").extract()[0]
        home_id = home_id.split("-")[1]
        match["home_id"] = home_id
        score = response.xpath("//p[@class='score']/text()").extract()[0]
        scores = score.split("-")
        if len(scores) == 2:
            match["home_score"], match["away_score"] = scores
        match["m_time"] = response.xpath("//p[@class='time']/text()").extract()[0]
        match["time"] = response.xpath("//div[@class='match-details']//script/text()").extract()[0]

        return match
