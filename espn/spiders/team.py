# -*- coding: utf-8 -*-
import scrapy
from espn.items import TeamItem


class TeamSpider(scrapy.Spider):
    name = "team"
    allowed_domains = ["espnfc.com"]
    start_urls = (
        'http://www.espnfc.com/api/navigation?xhr=1',
    )

    def parse(self, response):
        import json
        nav = json.loads(response.body)
        nations = nav["navigationItems"][3]["html"]
        nations = nations.replace("\\", "")
        from bs4 import BeautifulSoup as bs
        nations = bs(nations)
        #ul_filters = nations.find("ul", attrs={"class": "desktop-nav-filters"})
        #filters = [f.text for f in ul_filters.find_all("li")]
        image_list = nations.find_all("img", {"width": 20})
        import re
        href_pat = re.compile(r"http://www\.espnfc\.com/(?P<type>team|club)/.*?/(?P<id>\d+)/index")
        for image in image_list:
            name_en = image.parent.text
            href = image.parent.parent.get("href")
            matched = href_pat.match(href)
            if matched:
                group = matched.groupdict()
                id = group["id"]
                type = group["type"]
                team = TeamItem(id=id,
                            type=type,
                            name_en=name_en)
                yield team

