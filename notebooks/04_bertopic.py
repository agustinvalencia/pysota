# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: python3
# ---

# %%
from pathlib import Path
from pysota.core import Publication
from pysota.process import Persistence
from gensim import corpora
from gensim.models import LdaModel
import pandas as pd
import spacy
from gensim.models import CoherenceModel

nlp = spacy.load('en_core_web_lg')

# %%
from bertopic import BERTopic

# %%
exclude = [
    "representation", 
    "learning", 
    "learn", 
    "training", 
    "train", 
    "supervision",
    "supervised",
    "supervise",
    "method", 
    "model", 
    "datum", 
    "self" ,
    "task", 
]


# %%
def preprocess(text, exclude=exclude):
    doc = nlp(text.lower())
    tokens = [
        token.lemma_ for token in doc
        if not token.is_stop and not token.is_punct and token.is_alpha and token.lemma_ not in exclude and token.lemma_ != 'ADV'
    ]
    return ' '.join(tokens)


# %%
cluster = 0

# %%
db: list[Publication] = Persistence.load_files(path=Path('../results/clean'), query_name="")

# %%
ds = [preprocess(i.abstract) for i in db]

# %%
from umap import UMAP
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer

from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired
from bertopic.vectorizers import ClassTfidfTransformer


# Step 1 - Extract embeddings
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Step 2 - Reduce dimensionality
umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine')

# Step 3 - Cluster reduced embeddings
hdbscan_model = HDBSCAN(min_cluster_size=3, metric='euclidean', cluster_selection_method='eom', prediction_data=True)

# Step 4 - Tokenize topics
vectorizer_model = CountVectorizer(stop_words="english")

# Step 5 - Create topic representation
ctfidf_model = ClassTfidfTransformer()

# Step 6 - (Optional) Fine-tune topic representations with 
# a `bertopic.representation` model
representation_model = KeyBERTInspired()




# %%
# All steps together
model = BERTopic(
  embedding_model=embedding_model,          # Step 1 - Extract embeddings
  umap_model=umap_model,                    # Step 2 - Reduce dimensionality
  hdbscan_model=hdbscan_model,              # Step 3 - Cluster reduced embeddings
  vectorizer_model=vectorizer_model,        # Step 4 - Tokenize topics
  ctfidf_model=ctfidf_model,                # Step 5 - Extract topic words
  representation_model=representation_model # Step 6 - (Optional) Fine-tune topic representations
)

# %%

topics, probs = model.fit_transform(ds)

# %%
model.get_topic_info()

# %%
for topic in model.get_topic_info().Representation:
    print(topic)

# %%
model.visualize_topics()


