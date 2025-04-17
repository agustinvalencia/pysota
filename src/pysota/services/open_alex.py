import requests
from pysota.core import Provider, ResultPage, Publication
from pydantic import Field


class OpenAlexProvider(Provider):
    """
    Provider for querying the OpenAlex API.

    OpenAlex is a free, open catalog of scholarly works. This provider sends a search query
    to OpenAlex and converts the JSON response into a list of Publication objects.
    """

    name: str = Field(default='OpenAlex', frozen=True)
    query_root: str = Field(default='https://api.openalex.org/works', frozen=True)

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
        Extract Publication objects from the JSON payload returned by OpenAlex.

        Args:
            payload (dict): JSON response containing a "results" key with a list of works.

        Returns:
            list[Publication]: A list of Publication objects.
        """
        publications = []
        for work in payload.get('results', []):
            title = work.get('display_name', 'No Title')
            authorships = work.get('authorships', [])
            authors = [auth.get('author', {}).get('display_name', '') for auth in authorships]
            year = work.get('publication_year', 'Unknown')
            abstract = work.get('abstract', '')
            publications.append(
                Publication(title=title, authors=authors, year=year, abstract=abstract)
            )
        return publications

    def search(self, query: str) -> ResultPage:
        """
        Perform a search using the OpenAlex API and return a ResultPage.

        Args:
            query (str): The search query.

        Returns:
            ResultPage: A page of results with Publication items.
        """
        self.log(f'Querying OpenAlex: {query}')
        params = {
            'search': query,
            'per_page': 10,  # Number of results per page
        }
        response = requests.get(self.query_root, params=params)
        response.raise_for_status()
        data = response.json()
        items = self.extract_items(data)
        total = data.get('meta', {}).get('count', len(items))
        self.log(f'Found {total} results')
        return ResultPage(
            query=query,
            total=total,
            items_per_page=len(items),
            start_index=0,
            items=items,
        )
