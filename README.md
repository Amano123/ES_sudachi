# Elasticsearch sudachi wiki-40B

## TODO
* [x] ~~ubuntu・elasticsearch・kibanaの動作環境作成~~
* [x] ~~ElasticSearchにSudachiを追加~~
* [ ] ESにWiki-40Bを格納
  * [ ] Pythonでwiki-40Bを操作する
  * [ ] ElasticSearchの操作
* [ ] 特定の語を検索する


## 構成
* ElasticSearch
  * BD
  * 全文検索を用いてアノテーションデータ作成
* Ubuntu
  * データの格納・検索
  * Tensorflow datasetsのWiki-40b
* Kibana
  * データベースの確認用

```
├── docker-compose.yml
├── elasticsearch
│   ├── dockerfile
│   ├── node_data # BDのデータ保存先
│   └── sudachi.json
└── ubuntu
    ├── dockerfile
    └── source # プログラムの保存先
```

## 参考文献
### wiki40-b
https://www.tensorflow.org/datasets/catalog/wiki40b
