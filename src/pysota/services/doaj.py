from pydantic import Field
import requests
from pysota.core import Provider, ResultPage, Publication


class DOAJProvider(Provider):
    """
    Provider for querying the DOAJ API.

    DOAJ provides a free API to access metadata for open-access journals and articles.
    This provider sends a search query to DOAJ and parses the JSON response into Publication objects.

    Note:
        - The API is free and does not require an API key.
    """

    name: str = Field(default='DOAJ', frozen=True)
    query_root: str = Field(default='https://doaj.org/api/v2/articles/', frozen=True)

    def generate_query(self, query: str) -> str:
        """
        Return the query string as-is.

        Args:
            query (str): The search query.

        Returns:
            str: The same query string.
        """
        return query

    def extract_items(self, payload) -> list[Publication]:
        """
        Extract Publication objects from the JSON payload returned by DOAJ.

        Args:
            payload (dict): JSON response from DOAJ.

        Returns:
            list[Publication]: A list of Publication objects.
        """
        publications = []
        # DOAJ returns a "results" list containing article metadata.
        results = payload.get('results', [])
        for item in results:
            bibjson = item.get('bibjson', {})
            title = bibjson.get('title', 'No Title')
            authors_data = bibjson.get('author', [])
            authors = [author.get('name', '') for author in authors_data]
            year = bibjson.get('year', 'Unknown')
            abstract = bibjson.get('abstract', '')
            publications.append(
                Publication(title=title, authors=authors, year=year, abstract=abstract)
            )
        return publications

    def search(self, query: str) -> ResultPage:
        """
        Search DOAJ for articles matching the query and return a ResultPage.

        Args:
            query (str): The search query.

        Returns:
            ResultPage: A page of results with Publication items.
        """
        self.log(f'Querying DOAJ: {query}')
        params = {'q': query, 'page': 1, 'pageSize': 10}
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
