from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel
from rich import print

from pysota.core import IQuery, Publication


class ResultPage(BaseModel):
    query: IQuery
    total: int
    items_per_page: int
    start_index: int
    items: list[Publication]

    def save(self, path: Path, include_index: bool = False) -> None:
        if len(self.items) == 0:
            print('No items to save')
            return
        print(f'\n[cyan]{self.query.provider}[/cyan]: Files to be saved = {len(self.items)}')
        path.mkdir(parents=True, exist_ok=True)
        self.query.save_query(path)
        saved = 0
        for item in self.items:
            try:
                valid, err = item.check_validity()
                if not valid:
                    print(
                        f'Skipping publication:\
                            \n  [i]{item.title}[/i] \
                            \n  cause: [red]Invalid [bold]{err}[/bold][/red]'
                    )
                    continue
                item.save(path, include_index)
                saved += 1
            except Exception:
                print(f'[red]{item}[/red]')
                continue
        print(f'Finished: Saved {saved} files to [green]{path}[/green]')

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
