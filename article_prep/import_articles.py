#!/usr/bin/env python
# coding=utf-8

# Import articles to Google Cloud Firestore

import json
import hashlib

from google.cloud import firestore

def import_articles():
    # Two environment variables are defined
    # GOOGLE_APPLICATION_CREDENTIALS - json credentials for the service account
    # GCLOUD_PROJECT - project ID
    db = firestore.Client()
    db_collection = db.collection("articles_182k")
    f = open("articles_182k")
    l = f.readline()
    while l != "":
        article_dic = json.loads(l)
        url_hash = hashlib.sha256(article_dic["url"].encode()).hexdigest()
        db_doc = db_collection.document(url_hash)
        try:
            db_doc.set(article_dic)
        except:
            # Long content caused grpc error (too large size of string)
            article_dic["content"] = "Too long. Not stored here."
            db_doc.set(article_dic)
        print("Imported article {}".format(article_dic["url"]))
        l = f.readline()
    f.close()

if __name__ == "__main__":
    import_articles()
