#!/usr/bin/env python
# encoding: utf-8


import requests
import json
from itertools import chain
from bs4 import BeautifulSoup as bs
import re
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sports.sports_data import Team, League
from espn import settings


db = sa.create_engine(settings.SERVER)
session = sessionmaker(db)()
href_pat = re.compile(r".*?/(?P<id>\d+)/index")


def main():
    import pudb; pudb.set_trace()  # XXX BREAKPOINT
    data = requests.get("http://www.espnfc.com/api/navigation?xhr=1")
    data = json.loads(data.content)
    nav = data["navigationItems"]
    league = bs(nav[4]["html"])
    cup = bs(nav[5]["html"])
    for link in chain(league.find_all("a"), cup.find_all("a")):
        href = link.get("href")
        if href.endswith("index"):
            name = link.text
            matched = href_pat.match(href)
            if matched:
                group = matched.groupdict()
                #type = group["type"]
                id = group["id"]
                league = session.query(League).filter_by(name=name).first()
                if league:
                    league.id = id
                    #league.type = type
                    session.add(league)
    session.commit()


if __name__ == "__main__":
    main()

