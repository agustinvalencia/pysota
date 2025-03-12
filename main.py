import sys
from pathlib import Path

from pysota.core import ResultPage
from pysota.db.session import DBConfig, DBManager
from pysota.search import (
    ArxivProvider,
    CrossrefProvider,
    # DOAJProvider,
    EuropePMCProvider,
    PubMedProvider,
    # ScholarlyProvider,
    # SemanticScholarProvider,
    SearchEngine,
)

engine = SearchEngine(
    verbose=True,
    providers=[
        ArxivProvider(),
        CrossrefProvider(),
        EuropePMCProvider(),
        PubMedProvider(),
    ],
)


def query(query: str, save: bool = False, results_dir: Path | None = None):
    try:
        results: dict[str, ResultPage] = engine.search(query)
        if save and results_dir:
            for provider, result in results.items():
                print(f'\n\n>> Saving results for {provider}')
                result.save(Path(results_dir) / f'{provider}')
    except Exception as e:
        print(f'An error occurred: {e}', file=sys.stderr)


def create_db(results_dir: Path):
    db = DBManager(config=DBConfig())
    db.create_database_from_folder(results_dir)


def entrypoint():
    import argparse

    parser = argparse.ArgumentParser(description='Run arXiv search')
    parser.add_argument('--query', help='Query string')
    parser.add_argument('--save', action='store_true', help='Save results to dir')
    parser.add_argument('--results-dir', help='Save results to dir')
    parser.add_argument('--create-db', action='store_true', help='Create database from results')
    args = parser.parse_args()
    if args.query:
        query(args.query, args.save, args.results_dir)
    if args.create_db:
        create_db(Path(args.results_dir))


if __name__ == '__main__':
    entrypoint()
