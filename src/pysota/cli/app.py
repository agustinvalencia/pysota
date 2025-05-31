from typing import Annotated

import debugpy
import typer
from loguru import logger

from . import clean, cluster, db, search, topic, version

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

app = typer.Typer(no_args_is_help=True, invoke_without_command=True, pretty_exceptions_enable=False)
app.add_typer(search.app, help='Search things')
app.add_typer(clean.app)
app.add_typer(db.app, help='DB Management')
app.add_typer(cluster.app)
app.add_typer(topic.app)
app.add_typer(version.app)

DebugOption = Annotated[bool, typer.Option('--debug', help='Enable debug mode (requires debugpy)')]


@app.callback(invoke_without_command=True)
def debug_callback(ctx: typer.Context, debug: DebugOption = False):
    if debug:
        logger.debug('Enabling debug mode')
        debugpy.listen(('localhost', 5678))
        logger.debug('Waiting for debugger to attach on port 5678…')
        debugpy.wait_for_client()


def main():
    logger.info('\n\n\n------------ Starting new session of PySOTA ------------ \n\n\n')
    app()
