#%%
from typing import Counter, List
from elasticsearch import Elasticsearch

from tqdm import tqdm
import gensim
from gensim import corpora
from collections import defaultdict

import matplotlib
matplotlib.use('Agg') 
import matplotlib.pylab as plt
# font = {'family': 'TakaoGothic'}
# matplotlib.rc('font', **font)

import numpy as np

import time
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
print(es.info())
index = 'wiki40bbb'
# %%
class Analyzer:
    """Analyzer"""
    def __init__(self, es, index: str, analyze: str="sudachi_analyzer"):
        self.es = es
        self.index = index
        self.analyze = analyze

    def __call__(self, text):
        if not text:
            return []
        data = self.es.indices.analyze(
            index = self.index,
            body= {
                "analyzer": self.analyze ,
                "text": text
            }
        )
        tokens = []
        for token in data.get("tokens"):
            tokens.append(token.get("token"))
        return tokens #[token.get("token") for token in data.get("tokens")]

# %%
analyzer = Analyzer(es=es, index=index, analyze="sudachi_analyzer")
# %%
with open ("./poli_text.txt", mode="r") as f:
    texts = f.read().split("\n")

test_list = []
for text in texts:
    test_list.append(analyzer(text))
#%%
start = time.time()
dictionary = corpora.Dictionary(test_list)

# vocab size
print('vocab size: ', len(dictionary))
#save dictionary
dictionary.save_as_text("dictionary.txt")
    
elapsed_time = time.time() - start
print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")

# %%
corpus = [dictionary.doc2bow(t) for t in test_list]

# %%
corpus
# %%
tfidf = gensim.models.TfidfModel(corpus)

#%%
corpus_tfidf = tfidf[corpus]
# %%
#Metrics for Topic Models
start = 2
limit = 100
step = 1

coherence_vals = []
perplexity_vals = []

for n_topic in tqdm(range(start, limit, step)):
    lda_model = gensim.models.ldamodel.LdaModel(
        corpus=corpus, 
        id2word=dictionary, 
        num_topics=n_topic, 
        random_state=0
    )
    perplexity_vals.append(np.exp2(-lda_model.log_perplexity(corpus)))
    coherence_model_lda = gensim.models.CoherenceModel(
        model=lda_model, 
        texts=test_list, 
        dictionary=dictionary, 
        coherence='c_v'
    )
    coherence_vals.append(coherence_model_lda.get_coherence())

# %%
# evaluation
x = range(start, limit, step)

fig, ax1 = plt.subplots(figsize=(15,5))

# coherence
c1 = 'darkturquoise'
ax1.plot(x, coherence_vals, 'x-', color=c1)
ax1.set_xlabel('Num Topics')
ax1.set_ylabel('Coherence', color=c1); ax1.tick_params('y', colors=c1)

# perplexity
c2 = 'slategray'
ax2 = ax1.twinx()
ax2.plot(x, perplexity_vals, 'o-', color=c2)
ax2.set_ylabel('Perplexity', color=c2); ax2.tick_params('y', colors=c2)

# Vis
ax1.set_xticks(x)
fig.tight_layout()
ax1.tick_params(axis='x', labelrotation=90)
ax1.grid(which="major",alpha=0.6)
ax1.grid(which="minor",alpha=0.3)
plt.show()

# save as png
plt.savefig('metrics.pdf')

# %%
# LDA Model
# (format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=6, random_state=0)

# save model
lda_model.save('lda.model')
# %%
from pprint import pprint
for i, t in enumerate(range(lda_model.num_topics)):
    x = dict(lda_model.show_topic(t, 30))
    print(f"topic {i + 1}:")
    pprint(x)
# %%
