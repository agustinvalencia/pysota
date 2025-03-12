from pathlib import Path

import typer
from rich import print

from pysota.core import Publication
from pysota.process import Cleaner, Persistence


def clean_db(db: list[Publication], results_dir: Path):
    db = Cleaner.remove_duplicates(db)
    db = Cleaner.remove_non_english(db)
    Persistence.save_files(db, results_dir.joinpath('clean'))
    return db


def main(
    results_dir: Path = typer.Option(Path('./results'), help='Directory to save results.'),
    query_name: str = typer.Option(help='Query name'),
    clean: bool = typer.Option(False, help='Clean database'),
):
    db = Persistence.load_files(path=results_dir, query_name=query_name)
    print(len(db))

    if clean:
        print('Cleaning database')
        db = clean_db(db, results_dir)
        print(len(db))


if __name__ == '__main__':
    typer.run(main)
