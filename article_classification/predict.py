#!/usr/bin/env python
# coding: utf-8

import pickle
import re
import hashlib

import pandas as pd
import numpy as np
from gensim.models.word2vec import Word2Vec
from google.cloud import firestore

# Load data and models
df = pd.read_json("preprocessed_data.json")
wv_model = Word2Vec.load("word2vec.model")
with open("xgboost.pickle", "rb") as f:
    xgbc = pickle.load(f)
with open("rf.pickle", "rb") as f:
    rfc = pickle.load(f)

def predict_with_xgboost_and_rf(data):
    labels = sorted(["人文藝術", "其它", "娛樂購物", "自然景觀"])
    probs_xgbc = xgbc.predict_proba(data[[c for c in data.columns if c != "url"]])
    probs_rfc = rfc.predict_proba(data[[c for c in data.columns if c != "url"]])
    xgbc_list = [{label: p for label, p in zip(labels, prob)} for prob in probs_xgbc]
    rfc_list = [{label: p for label, p in zip(labels, prob)} for prob in probs_rfc]
    final_list = xgbc_list
    final_list.extend(rfc_list)
    return pd.DataFrame(final_list).mean().idxmax()

def predict():
    # Prepare data for predictions
    word_vectors = []
    tf_idfs = []
    urls = []
    for row in df.itertuples(index=False):
        for keyword in row.keyword_top10:
            word = keyword["word"]
            tf_idf = keyword["tfidf"]
            try:
                word_vectors.append(wv_model[word])
            except KeyError:
                continue
            tf_idfs.append(tf_idf)
            urls.append(row.url)
    df_word_vectors = pd.DataFrame(np.vstack(word_vectors))
    df_word_vectors.columns = [f"wv_d{i}" for i in range(1, 251)]
    df_tf_idf = pd.DataFrame(tf_idfs).rename(columns={0: "tf_idf"})
    df_url = pd.DataFrame(urls).rename(columns={0: "url"})
    data = pd.concat([df_url, df_word_vectors, df_tf_idf], axis=1)
    # Do predictions
    predicted_categories = []
    for url in data["url"].unique():
        sub_data = data.loc[data["url"] == url]
        prediction = predict_with_xgboost_and_rf(sub_data)
        predicted_categories.append({"url": url, "predicted_category": prediction})
    df_predicted = (
        df.merge(pd.DataFrame(predicted_categories), on="url", how="right")
            .rename(columns={"locations": "segmented_locations"})
    )
    return df_predicted

def push_predictions(df_predicted):
    db = firestore.Client()
    original_collection = db.collection("articles_182k")
    new_collection = db.collection("articles_for_app")
    for row in df_predicted.itertuples(index=False):
        # Seek top 12 cities
        for location in row.segmented_locations:
            found_city = re.match(r"(台中|宜蘭|台北|台南|桃園|新竹|高雄|新北|苗栗|嘉義|南投|花蓮).+", location)
            if found_city:
                found_city_name = found_city.group(1)
                if found_city_name not in row.segmented_locations:
                    row.segmented_locations.append(found_city_name)
                    print(f"{found_city_name} is appended to segmented locations")
        # Get needed raw article info
        query = original_collection.where("url", "==", row.url)
        docs = query.stream()
        for doc in docs:
            doc_dict = doc.to_dict()
            image_links = doc_dict.get("image_links")
            hits = doc_dict.get("hits")
            author = doc_dict.get("author")
        # Set data
        url_hash = hashlib.sha256(row.url.encode()).hexdigest()
        app_doc = new_collection.document(url_hash)
        app_doc.set({
            "url": row.url,
            "title": row.title,
            "author": author,
            "hits": hits,
            "segmented_locations": row.segmented_locations,
            "entity_address": row.entity_address,
            "image_links": image_links,
            "keyword_top10": row.keyword_top10,
            "sentences": row.sentences,
            "self_defined_category": row.self_defined_category,
            "predicted_category": row.predicted_category
        })
        print(f"Uploaded {row.url}")

if __name__ == "__main__":
    df_predicted = predict()
    push_predictions(df_predicted)
