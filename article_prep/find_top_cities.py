#!/usr/bin/env python
# coding: utf-8

import json
import re

import pandas as pd

if __name__ == "__main__":
    with open("title_locations.json") as f:
        title_locations = json.load(f)

    all_locations = []
    for v in title_locations.values():
        all_locations.extend(v["locations"])

    print(pd.Series(all_locations).value_counts().head(30))
