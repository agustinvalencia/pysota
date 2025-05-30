from pathlib import Path

from omegaconf import OmegaConf
from rich import print

from pysota.core import Publication


class Persistence:
    @staticmethod
    def publication_factory(file: Path) -> Publication:
        yaml_conf = OmegaConf.load(file)
        plain_dict = OmegaConf.to_container(yaml_conf, resolve=True)
        return Publication(**plain_dict)  # type: ignore

    @staticmethod
    def load_files(path: Path, query_name: str = '') -> list[Publication]:
        print(f'Analysing {path=} + {query_name=}')
        files = list(path.joinpath(query_name).glob('**/*.yaml'))
        print(f'Got [green]{len(files)}[/green] hits')
        db = []
        for file in files:
            if file.name == '_index.yaml':
                print(f'[yellow]skipping:[/yellow] {file.name}')
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
        index = {}
        for i in db:
            i.save(path)
            index[i.id] = i.title
        index_dump = OmegaConf.create(index)
        index_path = path.joinpath('_index.yaml')
        index_path.touch()
        with index_path as f:
            OmegaConf.save(index_dump, f)

    @staticmethod
    def load_file_by_name(db_path: Path, file_name: str) -> Publication | None:
        file_path = db_path.joinpath(f'{file_name}.yaml')
        if not file_path.exists():
            print(f'Target file not found: [red]{file_path}[/red]')
            return None
        return Persistence.publication_factory(file_path)
