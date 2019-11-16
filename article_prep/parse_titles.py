#!/usr/bin/env python
# coding: utf-8

import os
import json
import re
from datetime import datetime

import pandas as pd
# Articut API forked from https://github.com/Droidtown/ArticutAPI
from ArticutAPI.ArticutAPI import Articut

from get_article_titles import get_article_titles

def parse_titles(use_public_quota=True):
    if "title_locations.json" in os.listdir():
        with open("title_locations.json") as f:
            title_locations = json.load(f)
    else:
        if use_public_quota:
            articut = Articut()
        else:
            articut = Articut(username=os.environ["username"], apikey=os.environ["apikey"])
        url_title = get_article_titles()
        # Select articles having relatively higher hits
        articles = []
        for k, v in url_title.items():
            article = v
            article.update({"url": k})
            articles.append(article)
        _df = pd.DataFrame(articles)
        # The data get public on 2019-07-04
        _df["posted_ago"] = _df["posted_at"].apply(lambda x: (datetime(2019, 7, 4) - datetime.fromisoformat(x)).total_seconds()/(24*60*60))
        _df["hits_per_day"] = _df["hits"]/_df["posted_ago"]
        _df = _df.sort_values("hits_per_day", ascending=False)
        # Dropout articles with the same title
        _df.loc[~_df["title"].duplicated()]
        title_locations = {}
        # Hits per day > 5
        for row in _df.loc[_df["hits_per_day"] > 5].itertuples(index=False):
            results = articut.parse(inputSTR=row.title, openDataPlaceAccessBOOL=True)
            locations = []
            try:
                for p in results["result_pos"]:
                    # Non-greedy match: https://stackoverflow.com/a/22449/6666231
                    # Multiple matches (find globally): https://stackoverflow.com/a/11686930/6666231
                    for match in re.finditer(r"<LOCATION>(.+?)</LOCATION>", p):
                        found_location = match.group(1)
                        if found_location not in locations:
                            locations.append(found_location)
                    for match in re.finditer(r"<KNOWLEDGE_place>(.+?)</KNOWLEDGE_place>", p):
                        found_location = match.group(1)
                        if found_location not in locations:
                            locations.append(found_location)
                title_locations[row.url] = {"title": row.title, "locations": locations}
                print(row.title, locations)
            except KeyError:
                # Running out of quota
                print("Hit quota limit before finishing the task!")
                break
        with open("title_locations.json", "w") as f:
            json.dump(title_locations, f, indent=2, ensure_ascii=False)
    return title_locations

if __name__ == "__main__":
    parse_titles(use_public_quota=False)
