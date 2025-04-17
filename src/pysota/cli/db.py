import typer

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)


@app.command()
def clean():
    print('Cleaning')
