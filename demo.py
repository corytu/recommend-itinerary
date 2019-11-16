#!/usr/bin/env python
# coding: utf-8

import pickle

import pandas as pd
import numpy as np
from gensim.models.word2vec import Word2Vec

# Load data and models
df = pd.read_json("article_classification/preprocessed_data.json")
wv_model = Word2Vec.load("article_classification/word2vec.model")
with open("article_classification/xgboost.pickle", "rb") as f:
    xgbc = pickle.load(f)
with open("article_classification/rf.pickle", "rb") as f:
    rfc = pickle.load(f)

def sample_data(random_state=None):
    # Randomly pick one article
    df_sample = df.loc[df["self_defined_category"].isna()].sample(n=1, random_state=random_state)
    print("Sample data:")
    print(f"URL: {df_sample['url'].iloc[0]}")
    print(f"Title: {df_sample['title'].iloc[0]}")
    word_vectors = []
    tf_idfs = []
    words = []
    for row in df_sample.itertuples(index=False):
        for keyword in row.keyword_top10:
            word = keyword["word"]
            tf_idf = keyword["tfidf"]
            try:
                word_vectors.append(wv_model[word])
            except KeyError:
                continue
            tf_idfs.append(tf_idf)
            words.append(word)
    df_word_vectors = pd.DataFrame(np.vstack(word_vectors))
    df_word_vectors.columns = [f"wv_d{i}" for i in range(1, 251)]
    df_tf_idf = pd.DataFrame(tf_idfs).rename(columns={0: "tf_idf"})
    df_word = pd.DataFrame(words).rename(columns={0: "word"})
    data = pd.concat([df_word_vectors, df_tf_idf, df_word], axis=1)
    print("\nData for prediction:")
    print(data)
    return data

def predict_with_xgboost_and_rf(data):
    labels = sorted(["人文藝術", "其它", "娛樂購物", "自然景觀"])
    probs_xgbc = xgbc.predict_proba(data[[c for c in data.columns if c != "word"]])
    probs_rfc = rfc.predict_proba(data[[c for c in data.columns if c != "word"]])
    xgbc_list = [{label: p for label, p in zip(labels, prob)} for prob in probs_xgbc]
    print("\nWith XGBoost:")
    for w, ps in zip(data["word"], xgbc_list):
        print(w, ps)
    rfc_list = [{label: p for label, p in zip(labels, prob)} for prob in probs_rfc]
    print("\nWith random forest:")
    for w, ps in zip(data["word"], rfc_list):
        print(w, ps)
    final_list = xgbc_list
    final_list.extend(rfc_list)
    print("\nAveraged probabilities:")
    print(pd.DataFrame(final_list).mean())
    print("\nPredicted category:")
    print(pd.DataFrame(final_list).mean().idxmax())

if __name__ == "__main__":
    data = sample_data()
    predict_with_xgboost_and_rf(data)
