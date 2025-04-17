from typing import Annotated

import typer
from rich import print

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)


@app.command()
def hello(name: Annotated[str, typer.Option()] = ''):
    print(f'hello {name}')
