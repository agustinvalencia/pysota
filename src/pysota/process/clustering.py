from pydantic import BaseModel, Field
from sklearn.cluster import AgglomerativeClustering
from spacy.language import Language

from pysota.core.library import DocsLibrary
from pysota.core.publication import Publication


class Clusterer(BaseModel):
    library: DocsLibrary
    lang: Language
    clusters: dict[str, int] = Field(default={})

    class Config:
        arbitrary_types_allowed = True

    def agglomerative(
        self, n_clusters: int, metric: str = 'euclidean'
    ) -> dict[int, list[Publication]]:
        self.clusters = {}
        clustering = AgglomerativeClustering(n_clusters=n_clusters, metric=metric, linkage='ward')
        vectors = self.library.get_vectors(self.lang)
        print(f'{vectors.shape=}')
        ids = self.library.get_ids()
        clustering.fit(vectors)

        # The i-th label always corresponds to the i-th sample as well
        for idx, label in enumerate(clustering.labels_):
            id = ids[idx]
            self.clusters[id] = label

        return self.clusters
