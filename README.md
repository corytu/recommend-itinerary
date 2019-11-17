# recommend-itinerary
Backend and models for our project in 2019 PIXNET hackathon

本專案為「我想下班」隊伍參與 [2019 6th PIXNET hackathon](https://pixnethackathon2019.events.pixnet.net) 之作品，Triple，其中用到的資料後端與機器學習架構。Triple 為一 iOS app，旨在依使用者興趣取向協助規劃行程，並支援多人出遊時協作。

## 文章類別預測之展示

由於 numpy 版本不同會導致載入 Word2Vec 模型時出錯（[RaRe-Technologies/gensim#2602](https://github.com/RaRe-Technologies/gensim/issues/2602)），本專案使用 [pipenv](https://github.com/pypa/pipenv) 管理工作空間。

```bash
pipenv install --deploy
pipenv run python3 -Wi demo.py
```

上面指令將會隨機選出一篇未知類別的遊記文章，給出各分類之預測機率值，並預測其分類。

## 資料處理及訓練

處理完[文章資料存儲](article_prep/README.md)後，本次目的是需要把所有遊記分為四大類：人文藝術、娛樂購物、自然景觀、其它，以配合使用者在 app 上選擇的興趣取向依權重給予景點建議。

訓練材料為每篇遊記由 tf-idf 所得之前十關鍵字，以及這些關鍵字的 tf-idf 值。

1. 在 [EDA](article_classification/preliminary_explore.ipynb) 中，發現：
    1. 文章資料庫中四大類分布不均。
    2. 某些關鍵字如「景點」、「打卡」、「小朋友」等，在四大類中重複出現，會造成雜訊，應排除。
    3. 關鍵字中可能含有地名如「台中」，對文章分類沒有貢獻，應排除。
2. 由前步驟留下的關鍵字建立 Word2Vec 模型。由於關鍵字間並沒有上下文之語意連貫關係，而僅出現一次的關鍵字意義可能不大或造成未來 over-fitting，故參數設為 `min_count=2, sg=1, window=1`。
3. 將 194 篇已手動標記類別的文章，以 train : test = 0.75 : 0.25 的比例做[分類模型訓練](article_classification/train.ipynb)。面對類別 unbalanced 的問題，本次均以在 classifier 中調整權重的方式解決（權重為該類別於 training data set 中出現頻率之反比）。分別以 XGBoost 以及 random forest 進行分類後，亦嘗試將兩者回傳之類別機率值各自平均，以機率值最高之類別作為最終預測結果。最終之 subset accuracy 可達約 64.6%。
4. [預測](article_classification/predict.py)資料庫內其它文章之類別並將結果推回雲端資料庫。
