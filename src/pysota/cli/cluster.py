from pathlib import Path
from typing import Annotated

import spacy
from typer import Option, Typer

from pysota.core.library import DocsLibrary
from pysota.process.clustering import Clusterer
from pysota.process.persistence import Persistence

app = Typer(no_args_is_help=True, invoke_without_command=True)


@app.command(help='Build clusters from a results database')
def cluster(
    db: Annotated[Path, Option('--db', help='Folder of the DB to cluster')],
):
    library = DocsLibrary(folder=db)
    lang = spacy.load('en_core_web_lg')
    clst = Clusterer(library=library, lang=lang)
    clusters = clst.agglomerative(n_clusters=10)
    Persistence.save_clusters(clusters, Path(f'../results/clustered/{metric}'))
