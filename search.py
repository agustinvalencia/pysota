from pathlib import Path
from typing import Annotated, List

import typer
from rich import print

from pysota.core import ResultPage
from pysota.services import ArxivProvider, CrossrefProvider, SearchEngine

engine = SearchEngine(
    verbose=True,
    providers=[
        ArxivProvider(),
        CrossrefProvider(),
    ],
)


def run_query(
    name: str,
    include: List[str],
    exclude: List[str],
    save: bool = False,
    results_dir: Path | None = None,
    num_items: int = 10,
    offset: int = 0,
    all: bool = False,
):
    # fmt: off
    results: dict[str, ResultPage] = engine.search(
        name=name, 
        include=include, 
        exclude=exclude, 
        num_items=num_items, 
        offset=offset,
        all=all
    )
    if save and results_dir:
        print(f'\n>[bold]Saving results to [/bold][i green]{results_dir}[/i green]')

        for provider, result in results.items():
            result.save(
                Path(results_dir)
                .joinpath(name)
                .joinpath(provider), 
            )
            # fmt: on


# def main(
#     name: Annotated[str, typer.Option(help='Name of the query.')],
#     include: Annotated[
#         List[str], typer.Option(help='List of keywords to include in the search query.')
#     ],
#     exclude: Annotated[
#         List[str], typer.Option(help='List of keywords to exclude from the search')
#     ] = [],
#     save: Annotated[bool, typer.Option(help='Whether to dump results as yaml files')] = False,
#     results_dir: Annotated[Path, typer.Option(help='Directory to save results.')] = Path(
#         './results'
#     ),
#     num_items: Annotated[int, typer.Option(help='Number of items to download')] = 10,
#     all: Annotated[bool, typer.Option(help='Fetch all paginated results')] = False,
# ):
#     print(f'[bold]Searching for : [/bold][i green]\n{include=}\n{exclude=}[/i green]')
#     run_query(name, include, exclude, save, results_dir, num_items, all)


def main(
    include: Annotated[List[str], typer.Argument()],
    name: Annotated[str, typer.Option()],
    exclude: Annotated[List[str], typer.Option()] = [],
    save: Annotated[bool, typer.Option()] = False,
    results_dir: Annotated[Path, typer.Option()] = Path('./results'),
    num_items: Annotated[int, typer.Option()] = 10,
    offset: Annotated[int, typer.Option()] = 0,
    all: Annotated[bool, typer.Option()] = False,
):
    print(f'[bold]Searching for : [/bold][i green]\n{include=}\n{exclude=}[/i green]')
    run_query(name, include, exclude, save, results_dir, num_items, offset, all)


if __name__ == '__main__':
    typer.run(main)
