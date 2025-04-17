import typer
from loguru import logger

from . import clean, db, search, version

logger.remove()
logger.add(
    'logs/{time:YYYY-MM-DD}_info.log',
    format='({time:HH:mm:ss})-{level} - {message} - {file}:{line}',
    level='DEBUG',
    backtrace=True,
    diagnose=True,
    filter=lambda record: record['level'].name in ('DEBUG', 'INFO'),
)

logger.add(
    'logs/{time:YYYY-MM-DD}_errors.log',
    format='({time:HH:mm:ss})-{level} - {message} - {file}:{line}\n',
    level='WARNING',
    backtrace=True,
    diagnose=True,
    filter=lambda record: record['level'].name in ('WARNING', 'ERROR'),
)

app = typer.Typer(no_args_is_help=True)
app.add_typer(search.app)
app.add_typer(clean.app)
app.add_typer(db.app, name='db')
app.add_typer(version.app)


def main():
    logger.info('starting')
    app()
