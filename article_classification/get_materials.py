#!/usr/bin/env python
# coding: utf-8

import json

import pandas as pd
from google.cloud import firestore

def get_materials():
    with open("../articles_prep/title_locations.json") as f:
        title_locations = json.load(f)
    filtered_title_locations = {
        k: v for k, v in title_locations.items()
        if "懶人包" not in v["title"] and "整理" not in v["title"] and v["locations"] != []
    }
    db_collection = firestore.Client().collection("articles_182k")
    for k, v in filtered_title_locations.items():
        query = db_collection.where("url", "==", k)
        docs = query.stream()
        for doc in docs:
            doc_dict = doc.to_dict()
            if doc_dict.get("entity_address") is not None and doc_dict["entity_address"] != []:
                v.update({"entity_address": doc_dict["entity_address"]})
            if doc_dict.get("keyword_top10") is not None and doc_dict["keyword_top10"] != []:
                v.update({"keyword_top10": doc_dict["keyword_top10"]})
            print(f"Processed article {v['title']}")
    final_title_locations = {
        k: v for k, v in filtered_title_locations.items()
        if v.get("entity_address") is not None and v.get("keyword_top10") is not None
    }
    df = pd.DataFrame.from_dict(final_title_locations, orient="index").reset_index().rename(columns={"index": "url"})
    df["sentences"] = [[keyword["word"] for keyword in keywords] for keywords in df["keyword_top10"]]
    df.to_csv("classification_articles.csv", index=False)
    # model = Word2Vec(df.loc[~df["sentences"].isna(), "sentences"].tolist())
    # print(model["營地"])

if __name__ == "__main__":
    get_materials()