#!/usr/bin/env python
# coding=utf-8

import os
import json

from google.cloud import firestore

def get_article_titles():
    if "title_url.json" in os.listdir():
        with open("title_url.json") as f:
            title_url_dic = json.load(f)
    else:
        db = firestore.Client()
        article_ref = db.collection("articles_182k")
        title_url_dic = {}
        # Paginating data with query cursors: https://cloud.google.com/firestore/docs/query-data/query-cursors
        # Also see https://stackoverflow.com/a/57526797/6666231
        query = article_ref.order_by("url").limit(10000)
        while True:
            old_title_url_dic_len = len(title_url_dic)
            docs = query.stream()
            for doc in docs:
                doc_dict = doc.to_dict()
                title_url_dic[doc_dict["title"]] = doc_dict["url"]
                last_url = doc_dict["url"]
                print(f"Get article: {doc_dict['title']}")
            new_title_url_dic_len = len(title_url_dic)
            if new_title_url_dic_len > old_title_url_dic_len:
                query = article_ref.order_by("url").start_after({"url": last_url}).limit(10000)
            else:
                with open("title_url.json", "w") as f:
                    json.dump(title_url_dic, f, indent=2, ensure_ascii=False)
                break

if __name__ == "__main__":
    get_article_titles()
