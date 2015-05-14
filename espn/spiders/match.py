# -*- coding: utf-8 -*-
import scrapy
from twisted.internet import reactor
from cs import SoccerSpider, MatchFinished
from espn.items import MatchItem, FootballItem, FootballDetailsItem, PlayerMatchItem
from bs4 import BeautifulSoup as bs


class MatchSpider(SoccerSpider):
    name = "match"
    allowed_domains = ["espnfc.com"]
    #start_urls = (
        #'http://www.espnfc.com/',
    #)

    finished = ("FT", "Postponed")

    sql = "select id, espn_id, date, time from yt_match where date=date(now()) and finish <> 2"
    LIVE = "http://www.espnfc.com/gamecast/statistics/id/{}/statistics.html"

    stats = {"shots": "shots",
             "fouls": "fouls",
             "corner": "corner-kicks",
             "offside": "offsides",
             "ball_possession": "possession",
             "yellow_card": "yellow-cards",
             "red_card": "red-cards",
             "saving": "saves"}

    soccer_icons = {"soccer-icons-goal": 1,
                    "soccer-icons-yellowcard": 2,
                    "soccer-icons-redcard": 3,
                    "soccer-icons-subinout": 4,
                    "soccer-icons-owngoal": 5}

    player_match_cols = ("shots", "shots_goal", "goals", "assists", "offside", "fouls_suffered",
                         "fouls_commited", "saving", "yellow_card", "red_card")

    def __init__(self, sql=None, where=None, id=None, espn_id=None, **kwargs):
        super(MatchSpider, self).__init__(**kwargs)
        if sql:
            self.sql = sql
        elif where:
            self.sql = "select id, espn_id, date, time from yt_match where {}".format(where)
        elif id:
            self.sql = "select id, espn_id, date, time from yt_match where id={}".format(id)
        elif espn_id:
            self.sql = "select id, espn_id, date, time from yt_match where espn_id={}".format(espn_id)

    def generate_requests(self):
        for match in self.matches:
            self.fetch(match, match["espn_id"])
        yield

    def parse_match(self, response):
        match = response.meta["match"]
        response = bs(response.body, ["lxml"])

        #goals = response.find_all("div", attrs={"class": "span-3"})
        #if len(goals) == 2:
            #for team, tr in enumerate(goals, 1):
                #for goal in tr.find_all("td"):
                    #min = goal.text
                    #player_a = goal.a.get("title")
                    #player_a_id = goal.a.get("href")
                    #yield FootballDetailsItem(min=min,
                                              #player_a=player_a,
                                              #team=team,
                                              #type=1,
                                              #match_id=match["id"],
                                              #player_a_id=player_a_id)

        from itertools import chain
        player_stats = response.find_all("table", attrs={"class": "stat-table"})
        for team, table in enumerate(player_stats, 1):
            for tr in chain(table.find_all("tr", attrs={"class": "odd"}),
                            table.find_all("tr", attrs={"class": ""})):
                player_info = tr.find_all("td")
                if len(player_info) == 13:
                    name = player_info[2]
                    a = name.a
                    player_a_id = a.get("href") if a else None
                    player_a_name = a.get("title")

                    player_match = PlayerMatchItem(match_id=match["id"],
                                                   player_id=player_a_id)

                    for index, stat in enumerate(self.player_match_cols, 3):
                        player_match[stat] = player_info[index].text

                    yield player_match

                    events = name.find_all("div", attrs={"class": "soccer-icons"})
                    for event in events:
                        min = event.get("onmouseover")
                        for k, v in self.soccer_icons.items():
                            if k in event.get("class"):
                                yield FootballDetailsItem(min=min,
                                                          player_a=player_a_name,
                                                          team=team,
                                                          type=v,
                                                          match_id=match["id"],
                                                          player_a_id=player_a_id)
                                break

        match_detail = response.find("div", attrs={"class": "match-details"})
        if match_detail and match_detail.script:
            match["time"] = match_detail.script.text
        score_time = response.find("div", attrs={"class": "score-time"})
        if score_time:
            score= score_time.find("p", attrs={"class": "score"}).text.split("-")
            if len(score) == 2:
                match["home_score"], match["away_score"] = score
            match["m_time"] = score_time.find("p", attrs={"class": "time"}).text
        yield MatchItem(**match)

        match_football_item = FootballItem(match_id=match["id"])
        if "home_score" in match:
            match_football_item["home_score"] = match["home_score"]
            match_football_item["away_score"] = match["away_score"]
                                           #home_score=match["home_score"],
                                           #away_score=match["away_score"])
        for team in ("home", "away"):
            for item_key, html_key in self.stats.items():
                item_key = "{}_{}".format(team, item_key)
                html_key = "{}-{}".format(team, html_key)
                team_info = response.find("td", attrs={"id": html_key})
                if team_info:
                    match_football_item[item_key] = team_info.text
        yield match_football_item

        if "m_time" not in match or match["m_time"] in self.finished:
            raise MatchFinished()

