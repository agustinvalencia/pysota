from pathlib import Path

from omegaconf import OmegaConf

from pysota.core import Publication


class Persistence:
    @staticmethod
    def publication_factory(file: Path) -> Publication:
        yaml_conf = OmegaConf.load(file)
        plain_dict = OmegaConf.to_container(yaml_conf, resolve=True)
        return Publication(**plain_dict)  # type: ignore

    @staticmethod
    def load_files(path: Path, query_name: str = '') -> list[Publication]:
        files = list(path.joinpath(query_name).glob('**/*.yaml'))
        db = []
        for file in files:
            if file.name == f'{query_name}.yaml':
                continue
            try:
                db.append(Persistence.publication_factory(file))
            except Exception as e:
                print(f'[red]Caught![/red]:{file.name}\n{e}')
                continue
        return db

    @staticmethod
    def save_files(db: list[Publication], path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        for i in db:
            i.save(path)

    @staticmethod
    def save_clusters(clusters: dict[int, list[Publication]], path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        for cluster_id, publications in clusters.items():
            cluster_path = path.joinpath(f'cluster_{cluster_id}')
            cluster_path.mkdir(parents=True, exist_ok=True)
            for publication in publications:
                publication.save(cluster_path)
