# 文章資料準備
本次使用素材為 [PIXNET 文章資料](https://github.com/pixnet/2019-pixnet-hackathon/blob/master/data/README.md#pixnet-文章資料)，預計管理作法為：

## MongoDB
1. 將壓縮檔上傳至 [Cloud Storage](https://cloud.google.com/storage/)
2. 用 [Compute Engine](https://cloud.google.com/compute/) 讀取並解壓縮
3. `mongoimport` 到 MongoDB

```shell
gsutil cp gs://articles_182k/articles_182k.gz ./
gzip -d articles_182k.gz

mongoimport --drop --host pixnet2019-shard-0/pixnet2019-shard-00-00-stuh0.gcp.mongodb.net:27017,pixnet2019-shard-00-01-stuh0.gcp.mongodb.net:27017,pixnet2019-shard-00-02-stuh0.gcp.mongodb.net:27017 --ssl --username ytu --password <PASSWORD> --authenticationDatabase admin --db articles --collection articles_182k --type json --file articles_182k
```

但由於 [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) 的免費版只有 512 MB 容量，因此考慮以 [GCP Firestore](https://cloud.google.com/firestore/) 作為替代方案。

## Firestore
實作見 [import_articles.py](import_articles.py)。

## 參考資料

### GCP
- [快速入門：使用 gsutil 工具](https://cloud.google.com/storage/docs/quickstart-gsutil)
- [Running Jupyter Notebook on Google Cloud Platform in 15 min](https://towardsdatascience.com/running-jupyter-notebook-in-google-cloud-platform-in-15-min-61e16da34d52)

### NoSQL Database
- [Install MongoDB Community Edition on Ubuntu](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)
- [Quickstart using a server client library](https://cloud.google.com/firestore/docs/quickstart-servers)