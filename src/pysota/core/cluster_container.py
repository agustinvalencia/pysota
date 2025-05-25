from pathlib import Path

from pydantic import BaseModel


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

    def save_clusters(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        for cluster_id, publications in self.mapping.items():
            cluster_path = path.joinpath(f'cluster_{cluster_id}')
            cluster_path.mkdir(parents=True, exist_ok=True)
            for publication in publications:
                # publication.save(cluster_path)
                print(publication)
