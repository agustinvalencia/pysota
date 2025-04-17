from pathlib import Path
from typing import Annotated, List

import typer
from loguru import logger
from rich import print
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)

from pysota.core import ResultPage
from pysota.services import ArxivProvider, CrossrefProvider, SearchEngine, SemanticScholarProvider

app = typer.Typer(no_args_is_help=True)

console = Console(stderr=True)
progress = Progress(
    SpinnerColumn(),
    TextColumn('[bold blue]{task.description}', justify='right'),
    BarColumn(),
    '[progress.percentage]{task.percentage:>3.1f}%',
    '•',
    TimeRemainingColumn(compact=True, elapsed_when_finished=True),
)

engine = SearchEngine(
    verbose=True,
    providers=[
        ArxivProvider(),
        CrossrefProvider(),
        SemanticScholarProvider(),
    ],
)


@app.command()
def search(
    include: Annotated[List[str], typer.Argument()],
    name: Annotated[str, typer.Option()],
    exclude: Annotated[List[str], typer.Option('--exclude', '-x')] = [],
    save: Annotated[bool, typer.Option('--save', '-s')] = False,
    results_dir: Annotated[Path, typer.Option('--dir')] = Path('./results'),
    num_items: Annotated[int, typer.Option('--num-items', '-n')] = 10,
    offset: Annotated[int, typer.Option()] = 0,
    all: Annotated[bool, typer.Option()] = False,
):
    print(f'[bold]Searching for : [/bold][i green]\n{include=}\n{exclude=}[/i green]')
    logger.info(f'Searching for : {include=} - {exclude=}')
    total = len(engine.providers) * 2 if save else len(engine.providers)

    with progress:
        task_id = progress.add_task('Searching ...', total=total)
        # fmt: off
        results: dict[str, ResultPage] = engine.search(
            name=name, 
            include=include, 
            exclude=exclude, 
            num_items=num_items, 
            offset=offset, 
            all=all,
            task_id=task_id,
            progress=progress
        )
        # fmt: on
        if save and results_dir:
            print(f'\n>[bold]Saving results to [/bold][i green]{results_dir}[/i green]')
            logger.info(f'Saving results to {results_dir}')

            for provider, result in results.items():
                result.save(Path(results_dir).joinpath(name).joinpath(provider), include_index=True)
                progress.advance(task_id)


if __name__ == '__main__':
    app()
