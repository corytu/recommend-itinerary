#!/usr/bin/env python
# coding: utf-8

import json
import hashlib

from google.cloud import firestore

def push_parsed_locations():
    with open("title_locations.json") as f:
        title_locations = json.load(f)
    db_collection = firestore.Client().collection("articles_182k")
    for k, v in title_locations.items():
        if v["locations"] == []:
            continue
        url_hash = hashlib.sha256(k.encode()).hexdigest()
        article_ref = db_collection.document(url_hash)
        # https://stackoverflow.com/questions/54853247/how-to-add-fields-in-google-cloud-fire-store-using-python
        article_ref.set({"segmented_locations": v["locations"]}, merge=True)
        print(f"Merged locations of {v['title']}")

if __name__ == "__main__":
    push_parsed_locations()