from dataclasses import dataclass

from sklearn.cluster import AgglomerativeClustering

from pysota.core import Publication


@dataclass
class Clusterer:
    docs: list[Publication]

    def cluster(self, n_clusters: int):
        clusters = {}
        clustering = AgglomerativeClustering(n_clusters=n_clusters)
        for idx, label in enumerate(clustering.labels_):
            clusters.setdefault(label, []).append(self.docs[idx])
        return clusters
