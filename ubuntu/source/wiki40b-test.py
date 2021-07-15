#%%
from typing import Counter, List
import tensorflow_datasets as tfds
from elasticsearch import Elasticsearch
from elasticsearch import helpers

#%%
#マッピングの設定
mapping ={
        "settings": {
            "analysis": {
                "tokenizer": {
                    "sudachi_tokenizer": {
                        "type": "sudachi_tokenizer",
                        "discard_punctuation": True,
                        "sudachi_split":"search",
                        "resources_path": "/usr/share/elasticsearch/config/sudachi",
                        "settings_path": "/usr/share/elasticsearch/config/sudachi/sudachi.json"
                    }
                },
                "analyzer": {
                    "sudachi_analyzer": {
                        "filter": [
                        ],
                        "tokenizer": "sudachi_tokenizer",
                        "type": "custom"
                    }
                }
            }
        },
      "mappings":{
            "properties": {
                "text": {
                    "analyzer": "sudachi_analyzer",
                    "search_analyzer": "sudachi_analyzer",
                    "type": "text",
                    "fielddata": True,
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
    }}}}
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
print(es.indices.create(index=index, body=mapping))

#%%
#tf.tensorから文字列に変換
def tf_tensor_to_string(tensor):
    return tensor.numpy().decode()

# 各要素のindexを取得
def return_index(Wiki_list):
    section_index = [i for i, x in enumerate(Wiki_list) if x == '_START_SECTION_']
    patagraph_index = [i for i, x in enumerate(Wiki_list) if x == '_START_PARAGRAPH_']
    return (section_index, patagraph_index)

def paragraph_return_json_list(index, page_list, section_index,patagraph_index, wikidata_id):
    wiki_json_list = []
    sentence_count = 1
    # _START_SECTION_を保持していないデータ形式に対しての処理
    if "_START_SECTION_" not in page_list :
        for p_index in patagraph_index:
            # NEWLINEで分割処理
            split_paragrapg = page_list[p_index + 1].split("_NEWLINE_")
            for sentence in split_paragrapg:
                _index = {
                    "_index":index, 
                    "_source":{
                        "article" : page_list[0 + 1],
                        "section" : "Null",
                        "text_id" : sentence_count,
                        "text" : sentence,
                        "wikidata_id" : wikidata_id
                        }
                    }
                sentence_count += 1
                wiki_json_list.append(_index)
    else:
        for s_index, p_index in zip(section_index,patagraph_index):
            # NEWLINEで分割処理
            split_paragrapg = page_list[p_index + 1].split("_NEWLINE_")
            for sentence in split_paragrapg:
                _index = {
                    "_index":index, 
                    "_source":{
                        "article" : page_list[0 + 1],
                        "section" : page_list[s_index + 1],
                        "text_id" : sentence_count,
                        "text" : sentence,
                        "wikidata_id" : wikidata_id
                        }
                }
                sentence_count += 1
                wiki_json_list.append(_index)
    return wiki_json_list

# %%
def ES_input_Wiki40b(ds, index, es):
    dataset_len = len(ds)
    counter = 0
    bulk_json_list = []
    for num, wiki_page in enumerate(ds):
        document = tf_tensor_to_string(wiki_page['text'])
        page_list = document.split("\n")[1:]
        (
        section_index, 
        patagraph_index
        ) = return_index(page_list)
        wikidata_id = tf_tensor_to_string(wiki_page['wikidata_id'])

        wiki_json_list = paragraph_return_json_list(index ,page_list, section_index, patagraph_index, wikidata_id)
        
        bulk_json_list += wiki_json_list
        print(f"\r{num}/{dataset_len} [bulk_json_list] : {counter}", end="")
        counter += len(wiki_json_list)
        if counter > 30000:
                helpers.bulk(es, bulk_json_list, request_timeout=100)
                # print("\r\t[SUCCESS]\t\t\t\t", end="")
                counter = 0
                bulk_json_list = []
    helpers.bulk(es, bulk_json_list, request_timeout=100)
    return None

# %%
ds= tfds.load(
    'wiki40b/ja',
    split="test"
    )
# ES_input_Wiki40b(ds,index,es)
#%%
ds= tfds.load(
    'wiki40b/ja',
    split="train"
    )
# ES_input_Wiki40b(ds,index,es)
#%%
ds= tfds.load(
    'wiki40b/ja',
    split="validation"
    )
# ES_input_Wiki40b(ds,index,es)