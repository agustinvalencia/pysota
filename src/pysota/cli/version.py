import typer

app = typer.Typer(no_args_is_help=True)
version_no = '0.1.0'


@app.command()
def version():
    print(f'\n PySOTA version {version_no}')


if __name__ == '__main__':
    app()
