from pydantic import BaseModel, Field
from sklearn.cluster import AgglomerativeClustering
from spacy.language import Language

from pysota.core import ClustersContainer, DocsLibrary


class Clusterer(BaseModel):
    library: DocsLibrary
    lang: Language
    clusters: dict[str, int] = Field(default={})

    class Config:
        arbitrary_types_allowed = True

    def agglomerative(
        self, name: str, n_clusters: int, metric: str = 'euclidean'
    ) -> ClustersContainer:
        self.clusters = {}
        clustering = AgglomerativeClustering(n_clusters=n_clusters, metric=metric, linkage='ward')
        vectors = self.library.get_vectors(self.lang)
        ids = self.library.get_ids()
        clustering.fit(vectors)

        # The i-th label always corresponds to the i-th sample as well
        for idx, label in enumerate(clustering.labels_):
            id = ids[idx]
            self.clusters[id] = label

        return ClustersContainer(name=name, num=n_clusters, mapping=self.clusters)
