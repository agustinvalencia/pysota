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

import numpy as np
import spacy
from sklearn.cluster import AgglomerativeClustering

from pysota.process import Persistence

nlp = spacy.load('en_core_web_lg')
results_dir = Path('../results/clean')

# %%
db = Persistence.load_files(results_dir)
print(len(db))

# %%
documents = [i.abstract for i in db]
doc_vectors = [nlp(doc).vector for doc in documents]
X = np.array(doc_vectors)

eps = 0.5
metric = 'euclidean'

# cluster = DBSCAN(eps=eps, min_samples=2)
# dbscan = OPTICS(min_samples=2)
cluster = AgglomerativeClustering(
    n_clusters=10,
    metric=metric,
    linkage='ward',
)
# cluster = HDBSCAN(metric='cosine',  max_cluster_size=20)
cluster.fit(X)

# Group documents by their cluster labels
clusters = {}
for idx, label in enumerate(cluster.labels_):
    clusters.setdefault(label, []).append(db[idx])

# %%
# Print the number of documents in each cluster
print(f' Number of clusters: {len(clusters)} \n\n')
for label, docs in clusters.items():
    if label == -1:
        print(f'Noise: {len(docs)} documents')
    else:
        print(f'Cluster {label}: {len(docs)} documents')

# %%
# Print the number of documents in each cluster
print(f' Number of clusters: {len(clusters)} with eps = {eps}\n\n')
for label, docs in clusters.items():
    if label == -1:
        print(f'Noise: {len(docs)} documents')
    else:
        print(f'Cluster {label}: {len(docs)} documents')
    for doc in docs:
        title = doc.title.replace('\n', ' ')
        print(f'  - {title}')
    print('\n\n ========================================================= \n\n')

# c%%
Persistence.save_clusters(clusters, Path(f'../results/clustered/{metric}'))
