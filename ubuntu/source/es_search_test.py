#%%
from typing import Counter, List
import tensorflow_datasets as tfds
from elasticsearch import Elasticsearch
from elasticsearch import helpers

# %%
def connect_ES(host :str, port = None):
    _es = None
    _es = Elasticsearch(host)
    if _es.ping():
        print('Connection OK')
    else:
        print('Not connect!')
    return _es

es = connect_ES("elasticsearch-sudachi")

index = 'wiki40bbb'
print(es.info())
#%%
import io
terminology_list = io.open("./poli_dic/poli_terminology_list.txt").read().split("\n")
len(terminology_list)

#%%
# 単語の完全一致数の数を数える関数
def es_search_match_phrase_counter(word: str, es) -> int:
    query = {
        "query": {
            "match_phrase": {
                "text": word
            }
        }
    }
    result = es.search(size=1, index=index, body=query)
    return result["hits"]["total"]["value"]
# example
es_search_match_phrase_counter("高分子", es)

#%%
import time
# 高分子オントロジーの確認処理
terminology_count=[]
terminology_len = len(terminology_list)
start = time.time()
for num, terminology in enumerate(terminology_list, 1):
    if num % 10000 == 0:
        print(f"\r{num}/{terminology_len}", end="")
    count = es_search_match_phrase_counter(terminology, es)
    terminology_count.append([terminology, count])
elapsed_time = time.time() - start
print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
#%%
with open("poli_terminology_count.txt", mode="w") as f:
    [f.write(f"{x}\t{y}\n") for x,y in terminology_count]
# %%
# ここから下が検索処理
counter = 1

def get_doc(hits):
    global counter
    for hit in hits:
        text = hit['_source']['text']
        print(counter, text)
        counter += 1

scroll_size = 10000

query = {
    "query": {
        "match_phrase": {
            "text": "高分子"
        }
    }
}

result = response = es.search( scroll='2m',size=100, index=index, body=query)
sid = response['_scroll_id']

while True:
 # スクロールサイズ 0 だったら終了
    if scroll_size <= 0:
        break
    # 検索結果を処理
    get_doc(response['hits']['hits'])
    # スクロールから次の検索結果取得
    response = es.scroll(scroll_id=sid, scroll='10m')
    scroll_size = len(response['hits']['hits'])
    print( 'scroll_size', scroll_size)


# %%
