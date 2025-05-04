from pathlib import Path
from typing import Annotated

import spacy
from rich import print
from typer import Option, Typer

from pysota.core.library import DocsLibrary
from pysota.process.clustering import Clusterer

app = Typer(no_args_is_help=True, invoke_without_command=True)


@app.command()
def cluster(
    results_dir: Annotated[Path, Option('--dir')] = Path('./results'),
    db: Annotated[Path, Option('--db', help='Folder to store the DB')] = Path('./db'),
):
    library = DocsLibrary(folder=results_dir.joinpath(db))
    lang = spacy.load('en_core_web_lg')
    clst = Clusterer(library=library, lang=lang)
    clusters = clst.agglomerative(n_clusters=10)
    print(clusters)
