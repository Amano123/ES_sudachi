# Wiki40の前処理について

## 中身について
次のプログラムで、1記事のみ表示できる。
```python
import tensorflow_datasets as tfds
ds= tfds.load('wiki40b/ja', split="test") # split="train"で変更可
for wiki_page in ds:
    print(wiki_page)
    break
```
表示結果
```python
{'text': <tf.Tensor: shape=(), dtype=string, numpy=b'\n_START_ARTICLE_\n\xe3\x83\x93\xe3\x83\xbc\xe3\x83\x88\xe3\x81\x9f\xe3\x81\x91\xe3\x81\x97\xe3\x81\xae\xe6\x95\x99\xe7\xa7\x91\xe6\x9b\xb8\xe3\x81\xab\xe8\xbc\x89\xe3\x82\x89\xe3\x81\xaa\xe3\x81\x84\xe6\x97\xa5\xe6\x9c\xac\xe4\xba\xba\xe3\x81\xae\xe8\xac\x8e\n_START_SECTION_\n\xe6\xa6\x82\xe8\xa6\x81\n_START_PARAGRAPH_\n\xe3\x80\x8c\xe6\x95\x99\xe7\xa7\x91\xe6\x9b\xb8\xe3\x81\xab\xe3\x81\xaf\xe6\xb1\xba\xe3\x81\x97\xe3\x81\xa6\xe8\xbc\x89\xe3\x82\x89\xe3\x81\xaa\xe3\x81\x84\xe3\x80\x8d\xe6\x97\xa5\xe6\x9c\xac\xe4\xba\xba\xe3\x81\xae\xe8\xac\x8e\xe3\x82\x84\xe3\x81\x97\xe3\x81\x8d\xe3\x81\x9f\xe3\x82\x8a\xe3\x82\x92\xe5\xa4\x9a\xe8\xa7\x92\xe7\x9a\x84\xe3\x81\xab\xe6\xa4\x9c\xe8\xa8\xbc\xe3\x81\x97\xe3\x80\x81\xe6\x97\xa5\xe6\x9c\xac\xe4\xba\xba\xe3\x81\xaeDNA\xe3\x82\x92\xe8\xa7\xa3\xe6\x98\x8e\xe3\x81\x99\xe3\x82\x8b\xe3\x80\x82_NEWLINE_\xe6\x96\xb0\xe6\x98\xa5\xe7\x95\xaa\xe7\xb5\x84\xe3\x81\xa8\xe3\x81\x97\xe3\x81\xa6\xe5\xae\x9a\xe6\x9c\x9f\xe7\x9a\x84\xe3\x81\xab\xe6\x94\xbe\xe9\x80\x81\xe3\x81\x95\xe3\x82\x8c\xe3\x81\xa6\xe3\x81\x8a\xe3\x82\x8a\xe3\x80\x81\xe5\xb9\xb4\xe6\x9c\xab\xe3\x81\xae\xe5\x8d\x88\xe5\x89\x8d\xe4\xb8\xad\xe3\x81\xab\xe5\x86\x8d\xe6\x94\xbe\xe9\x80\x81\xe3\x81\x95\xe3\x82\x8c\xe3\x82\x8b\xe3\x81\xae\xe3\x81\x8c\xe6\x81\x92\xe4\xbe\x8b\xe3\x81\xa8\xe3\x81\xaa\xe3\x81\xa3\xe3\x81\xa6\xe3\x81\x84\xe3\x82\x8b\xe3\x80\x82'>,'version_id': <tf.Tensor: shape=(), dtype=string,numpy=b'1848243370795951995'>, 'wikidata_id': <tf.Tensor: shape=(), dtype=string, numpy=b'Q11331136'>}
```

JSON形式で`text`、`version_id`、`wikidata_id`が記述されている。
* text
  * wikipediaを整形したデータ
* version_id
  * よくわからん
* wikidata_id
  * Wikidataと関連するノードID

このままでは、encodeされている状態なので、decodeする。  
tf.tensorを入力したら、decodeする関数を書いた
```python
def tf_tensor_to_string(tensor):
    return tensor.numpy().decode()
```

各要素毎に入力する。
```python
for wiki_page in ds:
    text = tf_tensor_to_string(wiki_page['text'])
    version_id = tf_tensor_to_string(wiki_page['version_id'])
    wikidata_id = tf_tensor_to_string(wiki_page['wikidata_id'])
    break
```
結果は以下のようになる
```python
text : '\n_START_ARTICLE_\nビートたけしの教科書に載らない日本人の謎\n_START_SECTION_\n概要\n_START_PARAGRAPH_\n「教科書には決して載らない」日本人の謎やしきたりを多角的に検証し、日本人のDNAを解明する。_NEWLINE_新春番組として定期的に放送されており、年末の午前中に再放送されるのが恒例となっている。'
version_id : '1848243370795951995'
wikidata_id : 'Q11331136'
```

## `text`について
wiki-40bのtextをそのまま使用するのは難しいのでもうひと手間を加える。
### 問題リスト
- [x] ~~先頭に`\n`~~
- [ ] 文字列を特殊文字で区切ってる
- [ ] `_START_SECTION_`と`_START_PARAGRAPH_`が複数回出現
- [ ] `_START_SECTION_`を保持してないデータがある。

以上の問題を解決していく

### 先頭に`\n`
以下のように、改行`\n`で分割しリストとして扱うことにする
ブサイクな方法だが、先行に空の要素が入ってしまうためスライスを使って排除
```python
Wiki_list = text.split("\n")[1:]
```
### 文字列を特殊文字で区切ってる
特殊文字の種類としては
* `_START_ARTICLE_` : ページタイトル
* `_START_SECTION_` : 節のタイトル
* `_START_PARAGRAPH_`  : 節内の文章
  * `_NEWLINE_` ： 文章の改行
  
以上の種類がある。
その中でも`_START_SECTION_`と`_START_PARAGRAPH_`は複数出現する。
リストにしているので各特殊文字のindexが分かれば、`index + 1`で特殊文字の要素が抽出できる。

indexの取得方法は、`リスト.index`で取得できるが複数出現するものに対しては、先頭のindexのみ抽出される。
そのため、内包記述をする必要がある。

```python 
([i for i, x in enumerate(Wiki_list) if x == '_START_PARAGRAPH_'])
```
こうすることで、複数回出現する特殊文字(上の場合は`_START_PARAGRAPH_`)のindexを取得することができる。