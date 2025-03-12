from pydantic import BaseModel
from rich import print

from pysota.core import Provider, ResultPage


class SearchEngine(BaseModel):
    verbose: bool
    providers: list[Provider]

    def log(self, msg: str, pre: str = '') -> None:
        if pre != '':
            pre = f'\n> ({pre}) '
        if self.verbose:
            print(f'{pre} {msg}')

    def search(
        self,
        name: str,
        include: list[str],
        exclude: list[str],
        num_items: int,
        offset: int,
        all: bool,
    ) -> dict[str, ResultPage]:
        results: dict[str, ResultPage] = {}
        for idx, provider in enumerate(self.providers):
            print(f'\n>Querying [cyan]{provider.name}[/cyan]')
            results[provider.name] = provider.search(name, include, exclude, num_items, offset, all)
        return results
