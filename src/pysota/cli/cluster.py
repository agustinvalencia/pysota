from pathlib import Path
from typing import Annotated

import spacy
from rich import print
from typer import Option, Typer

from pysota.core.library import DocsLibrary
from pysota.process.clustering import Clusterer

app = Typer(no_args_is_help=True, invoke_without_command=True)


@app.command(help='Build clusters from a results database')
def cluster(
    db: Annotated[Path, Option('--db', help='Folder to store the DB')],
    results_dir: Annotated[Path, Option('--dir')] = Path('./results/clusters'),
):
    library = DocsLibrary(folder=results_dir.joinpath(db))
    lang = spacy.load('en_core_web_lg')
    clst = Clusterer(library=library, lang=lang)
    clusters = clst.agglomerative(n_clusters=10)
    print(clusters)
