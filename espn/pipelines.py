# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from espn.items import (TeamItem, PlayerItem, MatchItem, FootballDetailsItem,
                        FootballItem, PlayerMatchItem)
#import sys
from sports.sports_data import (Team, League, TeamPlayer, Player, Match,
                                MatchFootball, MatchFootballDetails, PlayerMatch)
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import NotConfigured, DropItem
from twisted.internet import reactor
#from espn.spiders.team import TeamSpider


class TeamPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, TeamItem):
            team = self.session.query(Team).filter_by(id=item["id"]).first()
            league_id = item.pop("league_id")
            if not team:
                team = Team(**item)
                self.session.add(team)
            else:
                team.update(**item)
            league = self.session.query(League).filter_by(id=league_id).first()
            if league and league not in team.league:
                team.league.append(league)
        return item

    @classmethod
    def from_settings(cls, settings):
        tp = cls()
        SERVER = settings.get("SERVER")
        if not SERVER:
            raise NotConfigured
        SESSION = settings.get("SESSION")
        if SESSION:
            tp.session = SESSION
        else:
            db = sa.create_engine(SERVER)
            tp.Session = sessionmaker(db)
            tp.session = tp.Session()
        AUTO_COMMIT_INTERVAL = settings.getint("AUTO_COMMIT_INTERVAL")
        if AUTO_COMMIT_INTERVAL:
            tp.AUTO_COMMIT_INTERVAL = AUTO_COMMIT_INTERVAL
            reactor.callLater(tp.AUTO_COMMIT_INTERVAL, tp.auto_commit)
        return tp

    def auto_commit(self):
        self.session.commit()
        reactor.callLater(self.AUTO_COMMIT_INTERVAL, self.auto_commit)

    def close_spider(self, spider):
        self.session.commit()


import re
from datetime import datetime


class PlayerPipeline(TeamPipeline):

    bracket = re.compile("\(([0-9.]+)\s?\w+\)")

    def process_item(self, item, spider):
        if isinstance(item, PlayerItem):
            item = self.tidy_item(item)
            team_id = item.pop("team_id", None)
            number = item.pop("number", None)
            team_player = TeamPlayer(team_id=team_id,
                                     number=number)
            player = self.session.query(Player).filter_by(id=item["id"]).first()
            if not player:
                player = Player(**item)
            else:
                player.update(**item)
            team_player = self.session.query(TeamPlayer).filter_by(team_id=team_id,
                                                                   player_id=player.id).first()
            if not team_player:
                team_player = TeamPlayer(number=number,
                                         team_id=team_id)
                player.team.append(team_player)
            team_player.number = number
            self.session.add(player)
        return item

    def tidy_item(self, item):
        _item = item.copy()
        if "height" in _item:
            matched = self.bracket.search(_item["height"])
            if matched:
                height =matched.group(1)
                _item["height"] = int(float(height) * 100)
        if "weight" in _item:
            matched = self.bracket.search(_item["weight"])
            if matched:
                weight = matched.group(1)
                _item["weight"] = weight
        if "birthday" in _item:
            birthday = datetime.strptime(_item["birthday"], "%B %d, %Y ")
            _item["birthday"] = birthday
        return _item


class MatchPipeline(TeamPipeline):

    status = {"FT": 2}
    time_pat = re.compile("Date\((\d+)\)")
    m_time_pat = re.compile("(\d+)\'")

    def process_item(self, item, spider):
        if isinstance(item, MatchItem):
            finish = item.get("finish", None)
            finish = self.status[finish] if finish in self.status else 0
            item["finish"] = finish

            #date = item.get("date", None)
            #if isinstance(date, basestring):
                #date = datetime.strptime(date, "%b %d, %Y")
                #item["date"] = date

            time = item.get("time", None)
            if time:
                matched = self.time_pat.search(time)
                if matched:
                    time = datetime.fromtimestamp(int(matched.group(1))/1000)
                    item["time"] = time
                    item["date"] = time

            if "m_time" in item:
                m_time = item["m_time"]
                if m_time == "FT":
                    item["finish"] = 2
                matched = self.m_time_pat.search(m_time)
                if matched:
                    m_time = matched.group(1)
                    item["m_time"] = m_time
                    item["finish"] = 1
                else:
                    item.pop("m_time")

            if "home_id" in item:
                home_id = item["home_id"]
                if isinstance(home_id, basestring) and not home_id.isdigit():
                    home = self.session.query(Team).filter_by(name_en=home_id).first()
                else:
                    home = self.session.query(Team).filter_by(id=home_id).first()
                if home:
                    item["home_id"] = home.id
                else:
                    raise DropItem

            if "away_id" in item:
                away_id = item["away_id"]
                if isinstance(home_id, basestring) and not away_id.isdigit():
                    away = self.session.query(Team).filter_by(name_en=away_id).first()
                else:
                    away = self.session.query(Team).filter_by(id=away_id).first()
                if away:
                    item["away_id"] = away.id
                else:
                    raise DropItem

            if "home_score" in item and item["home_score"].isdigit():
                item["home_score"] = int(item["home_score"])
            else:
                item.pop("home_score")

            if "away_score" in item and item["away_score"].isdigit():
                item["away_score"] = int(item["away_score"])
            else:
                item.pop("away_score")

            if "league_id" in item:
                league_id = item["league_id"]
                if not league_id.isdigit():
                    league_id = self.session.query(League).filter_by(name=league_id).first()
                else:
                    league_id = self.session.query(League).filter_by(id=league_id).first()
                if league_id:
                    item["league_id"] = league_id.id
                else:
                    item.pop("league_id")

            match = self.session.query(Match).filter_by(espn_id=item["espn_id"]).first()
            if not match:
                match = Match(**item)
                self.session.add(match)
            else:
                match.update(**item)
        return item


class MatchDetailsPipeline(TeamPipeline):

    min_pat = re.compile(r"(?P<base>\d+)(?: \+ )?(?P<extra>\d+)?\\\'(?:<br />Off: )?(?P<player>.*)\'")
    player_id_pat = re.compile(r"/player/(\d+)/.*")

    def process_item(self, item, spider):
        if isinstance(item, FootballDetailsItem):
            min = item["min"]
            min_matched = self.min_pat.search(min)
            if min_matched:
                base_min = int(min_matched.groupdict()["base"])
                extra_min = min_matched.groupdict()["extra"]
                if extra_min:
                    base_min += int(extra_min)
                item["min"] = base_min
            else:
                raise DropItem

            player_a_id = item["player_a_id"]
            player_matched = self.player_id_pat.search(player_a_id)
            if player_matched:
                item["player_a_id"] = player_matched.group(1)
                player_a = self.session.query(Player).filter_by(id=item["player_a_id"]).count()
                if not player_a:
                    raise DropItem
                if item["type"] == 4:
                    item["player_b"] = item["player_a"]
                    item["player_b_id"] = item["player_a_id"]
                    item["player_a"] = min_matched.groupdict()["player"]
                    player_a_id = self.session.query(Player).filter_by(name_en=item["player_a"]).first()
                    if player_a_id:
                        item["player_a_id"] = player_a_id.id
                    else:
                        raise DropItem
            football_detail = MatchFootballDetails(**item)
            self.session.add(football_detail)

        return item


class MatchFootballPipeline(TeamPipeline):

    shot_pat = re.compile(r"(\d+)\((\d+)\)")

    def process_item(self, item, spider):
        if isinstance(item, FootballItem):
            if "home_shots" in item:
                home_shots = item["home_shots"]
                home_shots_matched = self.shot_pat.search(home_shots)
                item["home_shots"] = home_shots_matched.group(2)
                item["home_shot"] = home_shots_matched.group(1)

            if "away_shots" in item:
                away_shots = item["away_shots"]
                away_shots_matched = self.shot_pat.search(away_shots)
                item["away_shots"] = away_shots_matched.group(2)
                item["away_shot"] = away_shots_matched.group(1)

            if "home_ball_possession" in item:
                item["home_ball_possession"] = item["home_ball_possession"][:-1]
            if "away_ball_possession" in item:
                item["away_ball_possession"] = item["away_ball_possession"][:-1]

            if "home_score" in item:
                item["home_score"] = int(item["home_score"])
            if "away_score" in item:
                item["away_score"] = int(item["away_score"])

            match_football = MatchFootball(**item)
            self.session.add(match_football)

        return item


class PlayerMatchPipeline(TeamPipeline):

    player_id_pat = re.compile(r"/player/(\d+)/.*")

    def process_item(self, item, spider):
        if isinstance(item, PlayerMatchItem):
            player_id = item["player_id"]
            matched = self.player_id_pat.search(player_id)
            if matched:
                item["player_id"] = matched.group(1)
                player = self.session.query(Player).filter_by(id=item["player_id"]).count()
                if not player:
                    raise DropItem
            for key, value in item.items():
                if isinstance(value, basestring):
                    item[key] = re.sub("\s", "", value)

            player_match = PlayerMatch(**item)
            self.session.add(player_match)

        return item

