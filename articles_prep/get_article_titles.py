#!/usr/bin/env python
# coding=utf-8

import os
import json
from datetime import datetime

from google.cloud import firestore

def get_article_titles():
    if "url_title.json" in os.listdir():
        with open("url_title.json") as f:
            url_title_dic = json.load(f)
    else:
        db = firestore.Client()
        article_ref = db.collection("articles_182k")
        url_title_dic = {}
        # Paginating data with query cursors: https://cloud.google.com/firestore/docs/query-data/query-cursors
        # Also see https://stackoverflow.com/a/57526797/6666231
        for site_category in ["國內旅遊", "國外旅遊"]:
            query = article_ref.where("site_category", "==", site_category).order_by("url").limit(10000)
            while True:
                old_url_title_dic_len = len(url_title_dic)
                docs = query.stream()
                for doc in docs:
                    doc_dict = doc.to_dict()
                    url_title_dic[doc_dict["url"]] = {
                        "title": doc_dict["title"],
                        "hits": doc_dict["hits"],
                        "posted_at": datetime.fromtimestamp(doc_dict["post_at"]).isoformat()
                    }
                    last_url = doc_dict["url"]
                    print("Get article: {}".format(doc_dict["title"]))
                new_url_title_dic_len = len(url_title_dic)
                if new_url_title_dic_len > old_url_title_dic_len:
                    query = article_ref.where("site_category", "==", site_category).order_by("url").start_after({"url": last_url}).limit(10000)
                else:
                    break
        with open("url_title.json", "w") as f:
            json.dump(url_title_dic, f, indent=2, ensure_ascii=False)
    return url_title_dic

if __name__ == "__main__":
    get_article_titles()
