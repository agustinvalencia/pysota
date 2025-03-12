from functools import singledispatchmethod

import requests
from pydantic import Field
from rich import print, print_json

from pysota.core import IQuery, Provider, ResultPage
from pysota.core.publication import Publication


class CrossrefQuery(IQuery):
    """
    CrossrefQuery class that implements the IQuery interface for querying the Crossref API.
    This class provides methods to construct and execute queries to the Crossref API,
    which is used for retrieving metadata about academic publications.
    """

    base: str = Field(default='https://api.crossref.org/works?', frozen=True)

    def _includes(self) -> str:
        include_str = '+'.join(self.include)
        return f'query.title={include_str}'

    def generate_url(self) -> str:
        if len(self.exclude) > 0:
            print(
                f'[yellow]Warning:[/yellow] Crossref does not support \
                  logical operations for excluding terms. Terms {self.exclude=} are ommited'
            )
        url = self.base + self._includes()
        url += '&filter=has-abstract:1'
        url += '&select=title,author,abstract,published'
        url += f'&rows={self.items_per_page}'
        if self.start_index > 0:
            url += f'&offset={self.start_index}'
        return url


class CrossrefProvider(Provider):
    """
    Provider for querying the Crossref REST API.

    Crossref provides metadata for scholarly articles (e.g., title, authors, publication year).
    This provider sends a query to the Crossref API and converts the response into Publication objects.
    """

    name: str = Field(default='crossref', frozen=True)
    query_root: str = Field(default='https://api.crossref.org/works', frozen=True)

    @singledispatchmethod
    def search(self) -> ResultPage:
        raise NotImplementedError

    @search.register
    def _(
        self,
        name: str,
        include: list,
        exclude: list = [],
        num_items: int = 10,
        offset: int = 0,
        all: bool = False,
    ) -> ResultPage:
        query = CrossrefQuery(
            name=name,
            provider=self.name,
            include=include,
            exclude=exclude,
            items_per_page=num_items,
            start_index=offset,
        )

        # if all:
        #     return self.search_all(query)
        return self.search(query)

    @search.register
    def _(self, query: CrossrefQuery) -> ResultPage:
        url = query.generate_url()
        print(f'Generated query: {url}')
        response = requests.get(url)
        return self._build_results_page(response, query)

    def extract_items(self, payload, query: IQuery) -> list[Publication]:
        papers = []
        idx = query.start_index + 1
        for entry in payload.json()['message']['items']:
            try:
                authors = []
                for author in entry.get('author', ''):
                    given = author.get('given', '')
                    family = author.get('family', '')
                    full_name = f'{given} {family}'.strip()
                    authors.append(full_name)

                title = entry.get('title', [])[0] if entry.get('title') else 'No Title'
                abstract = entry.get('abstract', '')
                year = entry.get('published', {}).get('date-parts', [[None]])[0][0] or -1

                pub = Publication(
                    title=title,
                    authors=authors,
                    year=year,
                    abstract=abstract,
                    internal_index=idx,
                    provider_name=self.name,
                    query_name=query.name,
                )
                papers.append(pub)
                idx += 1
            except Exception as e:
                print(f'[red]Caught![/red]{e}')
                print_json(entry)
                continue
        return papers

    def search_next(self, result_page) -> ResultPage:
        next_query = CrossrefQuery(
            name=result_page.query.name,
            provider=self.name,
            include=result_page.query.include,
            exclude=result_page.query.exclude,
            items_per_page=result_page.query.items_per_page,
            start_index=result_page.start_index + result_page.items_per_page - 1,
        )
        return self.search(next_query)

    def _build_results_page(self, response, query: CrossrefQuery) -> ResultPage:
        total = response.json()['message']['total-results']
        papers = self.extract_items(response, query)
        print(f'Found {total} matches')
        res = ResultPage(
            query=query,
            total=total,
            items_per_page=query.items_per_page,
            start_index=query.start_index,
            items=papers,
        )
        return res
