import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def clean():
    print('Cleaning')
