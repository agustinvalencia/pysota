import xml.etree.ElementTree as ET
from functools import singledispatchmethod

import requests
from pydantic import Field
from rich import print, print_json

from pysota.core import IQuery, Provider, Publication, ResultPage


class ArxivQuery(IQuery):
    """
    Query object for ArXiv.

    This class extends the IQuery class and provides a method to generate a query URL
    for the ArXiv API.
    """

    base: str = Field(default='http://export.arxiv.org/api/query?', frozen=True)

    def _includes(self) -> str:
        include = [f'all:{term}' for term in self.include]
        include_str = '+OR+'.join(include)
        include_str = include_str.replace(' ', '_')
        return f'search_query={include_str}'

    def _excludes(self) -> str:
        if len(self.exclude) == 0:
            return ''
        exclude = [f'all:{term}' for term in self.exclude]
        exclude_str = '+OR+'.join(exclude)
        exclude_str = exclude_str.replace(' ', '_')
        return f'+ANDNOT+%28{exclude_str}%29'

    def _max_results(self) -> str:
        return f'max_results={self.items_per_page}'

    def _start_index(self) -> str:
        return f'start={self.start_index}'

    def _sort_by(self) -> str:
        return 'sortBy=relevance&sortOrder=descending'

    def generate_url(self) -> str:
        """
        Generate a URL for the ArXiv API.

        Returns:
            str: A URL to query the ArXiv API.
        """
        url = self.base + self._includes() + self._excludes()
        url += f'&{self._max_results()}&{self._start_index()}&{self._sort_by()}'
        return url

    def __str__(self) -> str:
        return self.model_dump_json()


class ArxivProvider(Provider):
    """
    Provider for querying the ArXiv API.

    This provider constructs a query URL for ArXiv, sends an HTTP GET request, and parses the
    returned Atom XML response into Publication objects.
    """

    name: str = Field(default='arxiv', frozen=True)

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
        """Search ArXiv for papers matching the include and exclude lists."""
        query = ArxivQuery(
            name=name,
            provider=self.name,
            include=include,
            exclude=exclude,
            items_per_page=num_items,
            start_index=offset,
        )
        if all:
            return self.search_all(query)
        return self.search(query)

    @search.register
    def _(self, query: IQuery) -> ResultPage:
        url = query.generate_url()
        print(f'Generated query: {url}')
        response = requests.get(url)
        data = response.text
        root = ET.fromstring(data)
        return self._build_results_page(root, query)

    def search_next(self, result_page: ResultPage) -> ResultPage:
        """
        Search the next page of results on ArXiv.

        This method constructs a new URL for the next page of results based on the query and the
        start index of the current result page. It then calls the search method with the new URL.   "
        """
        next_query = ArxivQuery(
            name=result_page.query.name,
            provider=self.name,
            include=result_page.query.include,
            exclude=result_page.query.exclude,
            items_per_page=result_page.query.items_per_page,
            start_index=result_page.start_index + result_page.items_per_page - 1,
        )
        return self.search(next_query)

    def search_all(self, query: IQuery) -> ResultPage:
        self.log('Searching all results')
        first = self.search(query)
        print_json(first.model_dump_json())
        index = first.start_index + 1
        results = first
        print(f'{index=} < {first.total=} = {index < first.total}')
        while index < first.total:
            print(f'Fetching next page of results starting at index {index}')
            new = self.search_next(results)
            results.extend(new)
            index += new.num_items
        print(f'Downloaded [green]{results.num_items}[/green] results')
        return results

    # fmt: on
    def extract_items(self, payload, query: IQuery) -> list[Publication]:
        """
        Parse the Atom XML payload from ArXiv and extract Publication objects.

        Args:
            payload: An ElementTree object representing the XML response.

        Returns:
            list[Publication]: A list of Publication objects with title, authors, year, and abstract.
        """
        papers = []
        # Iterate over each <entry> element which represents a paper
        idx = query.start_index
        for entry in payload.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            # Extract authors from each <author> element
            authors = [
                author.find('{http://www.w3.org/2005/Atom}name').text
                for author in entry.findall('{http://www.w3.org/2005/Atom}author')
            ]
            # Get the publication year from the <published> element (first 4 characters)
            year = entry.find('{http://www.w3.org/2005/Atom}published').text[:4]
            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text

            pub = Publication(
                title=title,
                authors=authors,
                year=year,
                abstract=summary,
                internal_index=idx,
                provider_name=self.name,
                query_name=query.name,
            )
            papers.append(pub)
            idx += 1
        return papers

    def _build_results_page(self, root: ET.Element, query: IQuery) -> ResultPage:
        """
        Build a ResultPage object from the XML root element.

        Args: root (ET.Element): The root element of the XML response.

        Returns:
            ResultPage: A ResultPage object with Publication items.
        """
        # Extract pagination information using OpenSearch tags
        total = root.find('{http://a9.com/-/spec/opensearch/1.1/}totalResults').text  # type: ignore
        start_index = root.find('{http://a9.com/-/spec/opensearch/1.1/}startIndex').text  # type: ignore
        items_per_page = root.find('{http://a9.com/-/spec/opensearch/1.1/}itemsPerPage').text  # type: ignore
        papers = self.extract_items(root, query)

        # Convert pagination strings to integers (defaulting to -1 if conversion fails)
        total = int(total) if total is not None else -1
        items_per_page = int(items_per_page) if items_per_page is not None else -1
        start_index = int(start_index) if start_index is not None else -1

        print(f'Found {total} matches')
        results = ResultPage(
            query=query,
            total=total,
            items_per_page=items_per_page,
            start_index=start_index,
            items=papers,
        )
        return results
