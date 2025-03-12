import requests
from pysota.core import Provider, ResultPage, Publication
from pydantic import Field


class SemanticScholarProvider(Provider):
    """
    Provider for querying the Semantic Scholar API.

    This provider uses the free Semantic Scholar API to search for academic papers.
    The JSON response is parsed to extract key fields like title, authors, year, and abstract.
    """

    name: str = Field(default='Semantic Scholar', frozen=True)
    query_root: str = Field(
        default='https://api.semanticscholar.org/graph/v1/paper/search', frozen=True
    )

    def generate_query(self, query: str) -> str:
        """
        Return the query string directly.

        Args:
            query (str): The search query.

        Returns:
            str: The same query string.
        """
        return query

    def extract_items(self, payload) -> list[Publication]:
        """
        Extract Publication objects from the JSON payload returned by Semantic Scholar.

        Args:
            payload (dict): JSON response containing a "data" key with a list of papers.

        Returns:
            list[Publication]: A list of Publication objects.
        """
        publications = []
        for paper in payload.get('data', []):
            title = paper.get('title', 'No Title')
            authors_data = paper.get('authors', [])
            authors = [author.get('name', '') for author in authors_data]
            year = paper.get('year', 'Unknown')
            abstract = paper.get('abstract', '')
            publications.append(
                Publication(title=title, authors=authors, year=year, abstract=abstract)
            )
        return publications

    def search(self, query: str) -> ResultPage:
        """
        Perform a search using the Semantic Scholar API and return a ResultPage.

        Args:
            query (str): The search query.

        Returns:
            ResultPage: A page of results with Publication items.
        """
        self.log(f'Querying Semantic Scholar: {query}')
        params = {
            'query': query,
            'limit': 10,  # Limit the number of results
            'fields': 'title,authors,year,abstract',  # Specify fields to retrieve
        }
        response = requests.get(self.query_root, params=params)
        response.raise_for_status()
        data = response.json()
        items = self.extract_items(data)
        total = data.get('total', len(items))
        self.log(f'Found {total} results')
        return ResultPage(
            query=query,
            total=total,
            items_per_page=len(items),
            start_index=0,
            items=items,
        )
