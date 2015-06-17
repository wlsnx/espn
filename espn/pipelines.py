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


class DictCache(dict):

    def set(self, key, value, ex=None):
        if ex is not None and key not in self:
            reactor.callLater(ex, self.delete, key)
        self[key] = value.copy()

    def equal(self, item, old_item):
        if len(item) != len(old_item):
            return False
        for key, value in item.items():
            if not (key in old_item and old_item[key] == value):
                return False
        return True

    def get(self, key):
        return super(DictCache, self).get(key, None)

    def delete(self, key):
        if key in self:
            del self[key]

    def flushall(self):
        self.clear()

    def cache(self, prefix="", fields=(), cls=None, ex=3600 * 2):
        def wrap(func):
            def process_item(pipeline, item, spider=None):
                if cls is not None and not isinstance(item, cls):
                    return item
                key = prefix
                for field in fields:
                    key += u":{}".format(item.get(field, ""))
                old_item = self.get(key)
                if old_item is not None and self.equal(item, old_item):
                    raise DropItem
                else:
                    self.set(key, item, ex)
                    return func(pipeline, item, spider)
            return process_item
        return wrap


dict_cache = DictCache()


class DatabasePipeline(object):

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
            from twisted.internet import task
            task.LoopingCall(cls.auto_commit, tp).start(AUTO_COMMIT_INTERVAL)
        return tp

    def auto_commit(self):
        self.session.commit()

    def close_spider(self, spider):
        self.session.commit()


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
        return tp


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

    status = {"FT": 2, "Postponed": 0, "Abandoned": 2}
    time_pat = re.compile("Date\((-?\d+)\)")
    m_time_pat = re.compile("(\d+)\'")
    score_pat = re.compile("(\d+)")

    @dict_cache.cache(prefix="match", fields=sorted(MatchItem.fields), cls=MatchItem)
    def process_item(self, item, spider):
        if isinstance(item, MatchItem):

            #date = item.get("date", None)
            #if isinstance(date, basestring):
                #date = datetime.strptime(date, "%b %d, %Y")
                #item["date"] = date

            time = item.get("time", None)
            if time is not None and isinstance(time, basestring):
                matched = self.time_pat.search(time)
                if matched:
                    time = datetime.fromtimestamp(int(matched.group(1))/1000)
                    item["time"] = time.time()
                    item["date"] = time.date()

            if "m_time" in item:
                m_time = item["m_time"]
                if m_time in self.status:
                    item["finish"] = self.status[m_time]
                matched = self.m_time_pat.search(m_time)
                if matched:
                    m_time = matched.group(1)
                    item["m_time"] = m_time
                    item["finish"] = 1
                else:
                    item.pop("m_time")

            finish = item.get("finish", None)
            if not isinstance(finish, int) and 0 <= finish <= 2:
                finish = self.status[finish] if finish in self.status else 0
                item["finish"] = finish

            for team in ("home_id", "away_id"):
                if team in item:
                    team_id = item[team]
                    try:
                        team_id = int(team_id)
                        _team = self.session.query(Team).filter_by(id=team_id).first()
                    except ValueError:
                        _team = self.session.query(Team).filter_by(name_en=team_id).first()
                    if _team:
                        item[team] = _team.id
                    else:
                        raise DropItem

            for score in ("home_score", "away_score"):
                if score in item:
                    team_score = item[score]
                    if "P" in team_score:
                        item.pop(score)
                        continue
                    if "(" in team_score:
                        matched = self.score_pat.search(team_score)
                        if matched:
                            team_score = matched.group(1)
                    try:
                        item[score] = int(team_score)
                    except ValueError:
                        item.pop(score)

            if "league_id" in item:
                league_id = item["league_id"]
                try:
                    league_id = int(league_id)
                    league= self.session.query(League).filter_by(id=league_id).first()
                except ValueError:
                    league= self.session.query(League).filter_by(name=league_id).first()
                if league:
                    item["league_id"] = league.id
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

    @dict_cache.cache(prefix="match_details",
                      fields=sorted(FootballDetailsItem.fields),
                      cls=FootballDetailsItem)
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

            existed = self.session.query(MatchFootballDetails).filter_by(**item).first()
            if not existed:
                football_detail = MatchFootballDetails(**item)
                self.session.add(football_detail)
            else:
                existed.update(**item)

        return item


class MatchFootballPipeline(TeamPipeline):

    shot_pat = re.compile(r"(\d+)\((\d+)\)")

    @dict_cache.cache(prefix="match_football", fields=("match_id", ), cls=FootballItem)
    def process_item(self, item, spider):
        if isinstance(item, FootballItem):
            for team in ("home", "away"):
                team_shots_key = "{}_shots".format(team)
                if team_shots_key in item:
                    team_shot_key = "{}_shot".format(team)
                    team_shots = item[team_shots_key]
                    team_shots_matched = self.shot_pat.search(team_shots)
                    if team_shots_matched:
                        item[team_shots_key] = team_shots_matched.group(2)
                        item[team_shot_key] = team_shots_matched.group(1)

                team_possession_key = "{}_ball_possession".format(team)
                if team_possession_key in item:
                    item[team_possession_key] = item[team_possession_key][:-1]

                team_score_key = "{}_score".format(team)
                if team_score_key in item:
                    try:
                        item[team_score_key] = int(item[team_score_key])
                    except ValueError:
                        item.pop(team_score_key)

            existed = self.session.query(MatchFootball).filter_by(match_id=item["match_id"]).first()
            if not existed:
                match_football = MatchFootball(**item)
                self.session.add(match_football)
            else:
                existed.update(**item)

        return item


class PlayerMatchPipeline(TeamPipeline):

    player_id_pat = re.compile(r"/player/(\d+)/.*")
    min_pat = re.compile(r"(?P<base>\d+)(?: \+ )?(?P<extra>\d+)?\\\'(?:<br />Off: )?(?P<player>.*)\'")

    @dict_cache.cache(prefix="player_match", fields=sorted(PlayerMatchItem.fields), cls=PlayerMatchItem)
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

            for key, value in item.items():
                if value == "-":
                    item.pop(key)

            appear = item["appear"]
            if isinstance(appear, basestring):
                appear_matched = self.min_pat.search(appear)
                if appear_matched:
                    appear = int(appear_matched.groupdict()["base"])
                    item["appear"] = appear

            existed = self.session.query(PlayerMatch).filter_by(player_id=item["player_id"],
                                                                match_id=item["match_id"]).first()
            if not existed:
                player_match = PlayerMatch(**item)
                self.session.add(player_match)
            else:
                existed.update(**item)

        return item

