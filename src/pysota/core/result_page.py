from __future__ import annotations

from pathlib import Path

from loguru import logger
from pydantic import BaseModel
from rich import print

from pysota.core import IQuery, Publication


class ResultPage(BaseModel):
    query: IQuery
    total: int
    items_per_page: int
    start_index: int
    items: list[Publication]

    def save(self, path: Path) -> None:
        if len(self.items) == 0:
            print('No items to save')
            logger.info('No items to save')
            return

        print(f'\n[cyan]{self.query.provider}[/cyan]: Files to be saved = {len(self.items)}')
        logger.info(f'{self.query.provider}: Files to be saved = {len(self.items)}')

        path.mkdir(parents=True, exist_ok=True)
        self.query.save_query(path)

        saved = 0
        error = 0
        for item in self.items:
            try:
                valid, err = item.check_validity()
                if not valid:
                    logger.warning(f'Skipping publication:{item.title} because: Invalid {err}')
                    error += 1
                    continue

                item.save(path)
                saved += 1

            except Exception:
                error += 1
                continue

        print(
            f'Finished: Saved {saved} files to [green]{path}[/green] ([red]{error}[/red] not saved)'
        )
        logger.info(f'Finished: Saved {saved} files to {path} ({error} not saved)')

    def extend(self, other: ResultPage) -> None:
        self.items.extend(other.items)

    @property
    def num_items(self) -> int:
        return len(self.items)

    def __str__(self):
        s = f'{self.query} - {self.total} results'
        for item in self.items:
            s += f'\n{item}'
        return s
