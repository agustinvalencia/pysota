from pysota.definitions import ResultPage
from pathlib import Path
from pysota.search import SearchEngine
import sys


def query(args):
    try:
        engine = SearchEngine(verbose=True)
        results: ResultPage = engine.arxiv(args.query)
        if args.save:
            results.save(Path(args.save))
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)



def entrypoint():
    import argparse

    parser = argparse.ArgumentParser(description="Run arXiv search")
    parser.add_argument("--query", help="Query string")
    parser.add_argument("--save", help="Save results to dir")
    args = parser.parse_args()
    query(args)


if __name__ == "__main__":
    entrypoint()
