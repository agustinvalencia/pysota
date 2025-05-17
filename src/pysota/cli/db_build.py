from pathlib import Path
from typing import Annotated

from loguru import logger
from rich import print
from typer import Option, Typer

from pysota.process import Cleaner, Persistence

app = Typer(no_args_is_help=True, invoke_without_command=True)


@app.command(help='Build a database from a query results')
def db_build(
    query: Annotated[str, Option('--query', '-q', help='Query name')],
    results_dir: Annotated[Path, Option('--results-dir', help='Location of results')] = Path(
        './results/raw'
    ),
    name: Annotated[
        str, Option('--name', help='Folder to store the DB. Defaults to query name')
    ] = '',
):
    db = Persistence.load_files(path=results_dir, query_name=query)
    logger.info(f'Filling database with {len(db)} total results')
    print(f'Filling database with [bold]{len(db)}[/bold] total results')

    db = Cleaner.remove_duplicates(db)
    logger.info(f'Removed duplicates: {len(db)} total results')
    print(f'Removed duplicates: [bold]{len(db)}[/bold] total results')

    db = Cleaner.remove_non_english(db)
    logger.info(f'Removed non-english: {len(db)} total results')
    print(f'Removed non-english: [bold]{len(db)}[/bold] total results')

    if name == '':
        name = query

    db_path = results_dir.joinpath(name)
    Persistence.save_files(db, db_path)
    logger.info(f'Saved database to {db_path}')
    print(f'Saved database to {db_path}')
