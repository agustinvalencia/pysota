from pathlib import Path

from pydantic import BaseModel

from pysota.core.persistence import Persistence


class ClustersContainer(BaseModel):
    name: str
    num: int
    mapping: dict[str, int]

    @property
    def total_elements(self):
        return len(self.mapping)

    def __str___(self):
        print(
            f'Cluster: {self.name}\n- total elements: {self.total_elements}\n- n_clusters: {self.num}'
        )

    def save_clusters(self, clusters_output_path: Path, source_db: Path) -> None:
        clusters_output_path.mkdir(parents=True, exist_ok=True)
        # for cluster_id, publications in self.mapping.items():
        #     cluster_path = path.joinpath(f'cluster_{cluster_id}')
        #     cluster_path.mkdir(parents=True, exist_ok=True)
        #     print(self)
        #     for publication in publications:
        #         # publication.save(cluster_path)
        #         print(publication)
        print(f'> {clusters_output_path=}')
        for pub_name, cluster_id in self.mapping.items():
            cluster_path = clusters_output_path.joinpath(f'cluster_{cluster_id}')
            cluster_path.mkdir(parents=False, exist_ok=True)
            publ = Persistence.load_file_by_name(source_db, pub_name)
            if publ:
                publ.save(cluster_path)
