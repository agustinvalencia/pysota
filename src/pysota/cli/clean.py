from pathlib import Path
from typing import Annotated

import typer
from rich import print
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)

progress = Progress(
    SpinnerColumn(),
    TextColumn('[bold blue]{task.description}', justify='right'),
    BarColumn(),
    '[progress.percentage]{task.percentage:>3.1f}%',
    '•',
    TimeRemainingColumn(compact=True, elapsed_when_finished=True),
)


def _clean_lower_level_folder(folder: Path, level: int):
    files = list(folder.iterdir())
    total = len(files)
    task_id = progress.add_task(str(folder), total=total)
    for f in files:
        if f.is_dir():
            _clean_lower_level_folder(f, level + 1)
        progress.advance(task_id)
        if f.is_file():
            f.unlink()
        if f.is_dir():
            f.rmdir()
    if level > 2:
        progress.remove_task(task_id)
    folder.rmdir()


def clean_all(results_dir: Path):
    print('[red]Warning[/red] - These folders will be deleted: ')
    targets = list(results_dir.iterdir())
    for dir in targets:
        print(f' - {dir}')
    _ = typer.confirm('Are you sure to continue?', abort=True)

    total = len(targets)
    with progress:
        task_del = progress.add_task(f'[red]Cleaning {str(results_dir)}', total=total)
        for dir in targets:
            _clean_lower_level_folder(dir, level=2)
            progress.advance(task_del)
        results_dir.rmdir()


@app.command(help='Remove all the results')
def clean(
    results_dir: Annotated[Path, typer.Option(help='Results location')] = Path('./results'),
    all: Annotated[bool, typer.Option(help='Remove all results. Overrides --query')] = False,
    query: Annotated[str, typer.Option('--query', '-q', help='Query results to delete')] = '',
):
    if all:
        clean_all(results_dir)
    else:
        if query not in ['', 'db']:
            with progress:
                target = results_dir.joinpath(query)
                if target.exists():
                    _clean_lower_level_folder(target, 1)
