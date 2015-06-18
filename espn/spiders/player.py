# -*- coding: utf-8 -*-
#import scrapy
#from scrapy.contrib.linkextractors import LinkExtractor
#from scrapy.contrib.spiders import CrawlSpider, Rule

from scrapy import Request, Spider
from espn.items import PlayerItem
from bs4 import BeautifulSoup as bs
import re


class PlayerSpider(Spider):
    name = 'player'
    allowed_domains = ['espnfc.com']
    #start_urls = ['http://www.espnfc.com/']

    #rules = (
        #Rule(LinkExtractor(allow=r'player/\d+/.*'), callback='parse_player', follow=True),
    #)

    URL = "http://www.espnfc.com/{type}/team_name/{id}/squad?league=all"
    player_pat = re.compile("/(\d+)/")

    def start_requests(self):
        SERVER = self.settings.get("SERVER")
        if SERVER:
            import dataset
            db = dataset.connect(SERVER)
            teams = db.query("select id, type from yt_team")
            for team in teams:
                url = self.URL.format(**team)
                yield Request(url,
                              meta={"team_id": team["id"]})

    def parse_player(self, response):
        player = response.meta["player"]
        response = bs(response.body, ["lxml"])
        athlete = response.find("div", attrs={"id": "athlete-page"})
        dl1, dl2 = athlete.find_all("dl")
        dd1 = [dd.text for dd in dl1.find_all("dd")]
        if len(dd1) == 3:
            player["weight"] = dd1.pop()
        if len(dd1) == 2:
            player["height"] = dd1.pop()
        dd2 = [dd.text for dd in dl2.find_all("dd")]
        if len(dd2) == 3:
            player["country_en"] = dd2.pop()
        if len(dd2) == 2:
            player["birthday"] = dd2.pop()
        return player

    def parse(self, response):
        team_id = response.meta["team_id"]
        response = bs(response.body, ["lxml"])
        tables = response.find_all("div", attrs={"class": "responsive-table-content"})
        trs = [tr for table in tables for tr in table.find_all("tr") if not tr.has_attr("class")]
        for tr in trs:
            pos = tr.find("td", attrs={"class": "pos"}).text
            no = tr.find("td", attrs={"class": "no"}).text
            #age = tr.find("td", attrs={"class": "age"}).text
            pla = tr.find("td", attrs={"class": "pla"})
            name = pla.get("data-value")
            a = pla.a
            if a:
                href = a.get("href")
                matched = self.player_pat.search(href)
                if matched:
                    id = matched.group(1)
                    player = PlayerItem(position=pos,
                                        number=no,
                                        id=id,
                                        #age=age,
                                        team_id=team_id,
                                        name_en=name)
                    yield Request(href,
                                meta={"player": player},
                                callback=self.parse_player)

