# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from espn.items import TeamItem
from bs4 import BeautifulSoup as bs
import re


href_pat = re.compile(r".*?/(?P<type>team|club)/(?P<name>.*?)/(?P<id>\d+)/index")


class TeamSpider(scrapy.Spider):
    name = 'team'
    allowed_domains = ['espnfc.com']
    start_urls = ['http://www.espnfc.com/api/navigation?xhr=1']

    #rules = (
        #Rule(LinkExtractor(allow=r'/index'), callback='parse_club', follow=True),
    #)

    def parse(self, response):
        import json
        from itertools import chain
        data = json.loads(response.body)
        nav = data["navigationItems"]
        league = nav[4]["html"]
        league = bs(league, ["lxml"])
        cup = nav[5]["html"]
        cup = bs(cup, ["lxml"])
        for link in chain(league.find_all("a"), cup.find_all("a")):
            href = link.get("href")
            if href.endswith("index"):
                yield scrapy.Request(href,
                                     dont_filter=True,
                                     callback=self.parse_team)

    def parse_team(self, response):
        data = bs(response.body, ["lxml"])
        teams = data.find("li", {"data-section": "clubs"})
        teams = teams.ul.find_all("li")
        league = re.match(".*?/(\d+)/index", response.url)
        if league:
            league_id = league.group(1)
        else:
            raise StopIteration
        for team in teams:
            a = team.a
            href = a.get("href")
            name_en = a.text
            matched = href_pat.match(href)
            if matched:
                group = matched.groupdict()
                type = group["type"]
                id = group["id"]
                espn_name = group["name"]
                item = TeamItem(name_en=name_en,
                                id=id,
                                espn_name=espn_name,
                                league_id=league_id,
                                type=type)
                yield item

