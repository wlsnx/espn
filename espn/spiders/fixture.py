# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup as bs
import re
from espn.items import MatchItem


class FixtureSpider(scrapy.Spider):
    name = "fixture"
    allowed_domains = ["espnfc.com"]
    #start_urls = (
        #'http://www.espnfc.com/',
    #)

    season = 2015
    FIXTURE_URL = "http://www.espnfc.com/{type}/{espn_name}/{id}/fixtures?leagueId=0&season={season}"
    team_pat = re.compile("teamlogos/soccer/\d+/(\d+).png")

    def start_requests(self):
        import dataset
        SERVER = self.settings.get("SERVER")
        if SERVER:
            db = dataset.connect(SERVER)
            teams = db.query("select id, espn_name, type from yt_team")
            for team in teams:
                url = self.FIXTURE_URL.format(season=self.season, **team)
                yield scrapy.Request(url,
                                     meta={"team": team})

    def parse(self, response):
        for item in self.parse_fixture(response):
            yield item
        team = response.meta["team"]
        seasons = response.xpath(".//*[@id='club-season-dropdown']/select/option/@value").extract()
        for season in seasons:
            url = self.FIXTURE_URL.format(season=season, **team)
            yield scrapy.Request(url,
                                 meta={"team": team})

    def parse_fixture(self, response):
        #team = response.meta["team"]
        response = bs(response.body)
        fixtures = response.find_all("a", attrs={"class": "score-list"})
        for fixture in fixtures:
            espn_id = fixture.get("data-gameid")
            date = fixture.find("div", attrs={"class": "headline"}).text
            finish = fixture.find("div", attrs={"class": "status"})
            if not finish:
                finish = 2
            else:
                finish = finish.text

            home_logo = fixture.find("div", attrs={"class": "score-home-team"}).find("img")
            matched = self.team_pat.search(home_logo.get("src"))
            if matched:
                home_id = matched.group(1)
            else:
                home_id = home_logo.get("alt")

            result = fixture.find("div", attrs={"class": "result"})
            home_score = result.find("span", attrs={"class": "home-score"}).text
            away_score = result.find("span", attrs={"class": "away-score"}).text

            away_logo = fixture.find("div", attrs={"class": "score-away-team"}).find("img")
            matched = self.team_pat.search(away_logo.get("src"))
            if matched:
                away_id = matched.group(1)
            else:
                away_id = away_logo.get("alt")

            league_id = fixture.find("div", attrs={"class": "score-competition"}).get("title")

            match = MatchItem(home_id=home_id,
                              away_id=away_id,
                              date=date,
                              league_id=league_id,
                              home_score=home_score,
                              away_score=away_score,
                              finish=finish,
                              espn_id=espn_id)
            yield match

