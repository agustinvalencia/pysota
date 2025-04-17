from loguru import logger
from pydantic import BaseModel
from rich import print
from rich.progress import Progress, TaskID

from pysota.core import Provider, ResultPage


class SearchEngine(BaseModel):
    verbose: bool
    providers: list[Provider]

    def search(
        self,
        name: str,
        include: list[str],
        exclude: list[str],
        num_items: int,
        offset: int,
        all: bool,
        task_id: TaskID,
        progress: Progress,
    ) -> dict[str, ResultPage]:
        results: dict[str, ResultPage] = {}
        for provider in self.providers:
            print(f'\n>Querying [cyan]{provider.name}[/cyan]')
            logger.info(f'Querying: {provider.name}')
            results[provider.name] = provider.search(name, include, exclude, num_items, offset, all)
            progress.advance(task_id)
        return results
