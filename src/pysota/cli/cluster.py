from pathlib import Path
from typing import Annotated

import spacy
from typer import Option, Typer

from pysota.core import ClustersContainer, DocsLibrary
from pysota.process import Clusterer

app = Typer(no_args_is_help=True, invoke_without_command=True)


@app.command(help='Build clusters from a results database')
def cluster(
    db: Annotated[Path, Option('--db', help='Folder of the DB to cluster')],
    n: Annotated[int, Option('-n', '--num-clusters', help='Number of clusters')] = 10,
    metric: Annotated[str, Option('-m', '--metric', help='Distance metric')] = 'euclidean',
):
    library = DocsLibrary(folder=db)
    lang = spacy.load('en_core_web_lg')
    clst = Clusterer(library=library, lang=lang)
    clusters: ClustersContainer = clst.agglomerative(name='test', n_clusters=n, metric=metric)
    clusters.save_clusters(Path(f'../results/clustered/{metric}'))
