from functools import singledispatchmethod

import requests
from loguru import logger
from pydantic import Field
from rich import print

from pysota.core import Provider, Publication, ResultPage
from pysota.core.query import IQuery


class SemanticScholarQuery(IQuery):
    base: str = Field(default='https://api.semanticscholar.org/graph/v1/paper/search/bulk')

    def _includes(self) -> str:
        include_str = '+'.join([term for term in self.include])
        return include_str

    def _excludes(self) -> str:
        if len(self.exclude) == 0:
            return ''
        exclude_str = '-'.join(self.exclude)
        return exclude_str

    def _offset(self) -> str:
        if self.start_index == 0:
            return ''
        return f'&offset={self.start_index}'

    def _limit(self) -> str:
        if self.items_per_page == 0:
            return ''
        return f'&limit={self.items_per_page}'

    def generate_url(self) -> str:
        url = f'{self.base}?query={self._includes()}{self._excludes()}'
        url += f'{self._offset()}'
        url += '&fields=title,year,authors,abstract,url'
        url += '&sort=publicationDate:desc'
        url += '&openAccessPdf'
        return url


class SemanticScholarProvider(Provider):
    name: str = Field(default='semantic', frozen=True)

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
        query = SemanticScholarQuery(
            name=name,
            provider=self.name,
            include=include,
            exclude=exclude,
            items_per_page=num_items,
            start_index=offset,
        )
        return self.search(query)

    @search.register
    def _(self, query: SemanticScholarQuery) -> ResultPage:
        url = query.generate_url()
        logger.info(f'Generated query: {url}')
        response = requests.get(url)
        logger.info(f'response: {response}')
        return self._build_results_page(response, query)

    def extract_items(self, payload, query: IQuery) -> list[Publication]:
        papers = []
        idx = query.start_index
        data = payload.json()['data']
        for entry in data:
            try:
                authors = []
                for author in entry.get('authors', ''):
                    name = author.get('name', '')
                    authors.append(name)
                title = entry.get('title', '')
                abstract = entry.get('abstract', '')
                year = entry.get('year', 0000)

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
                logger.warning(f'Error processing data:\n{e}')
                continue
        return papers

    def search_next(self, result_page: ResultPage) -> ResultPage:
        raise NotImplementedError

    def _build_results_page(self, response, query: SemanticScholarQuery) -> ResultPage:
        total = response.json()['total']
        papers = self.extract_items(response, query)
        print(f'Found {total} matches')
        logger.info(f'Found {total} matches')
        res = ResultPage(
            query=query,
            total=total,
            items_per_page=query.items_per_page,
            start_index=query.start_index,
            items=papers,
        )
        return res
