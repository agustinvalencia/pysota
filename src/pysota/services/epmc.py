import requests
from pydantic import Field

from pysota.core import Provider, Publication, ResultPage


class EuropePMCProvider(Provider):
    """
    Provider for querying Europe PMC API.

    Europe PMC provides free access to a large database of biomedical and life sciences literature.
    This provider sends a search query and parses the JSON response into Publication objects.

    Note:
        - The API is free but may have rate limits.
    """

    name: str = Field(default='EuropePMC', frozen=True)
    query_root: str = Field(
        default='https://www.ebi.ac.uk/europepmc/webservices/rest/search', frozen=True
    )

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
        Extract Publication objects from the JSON payload returned by Europe PMC.

        Args:
            payload (dict): JSON response from Europe PMC.

        Returns:
            list[Publication]: A list of Publication objects.
        """
        publications = []
        # Europe PMC returns a "resultList" containing a "result" array.
        results = payload.get('resultList', {}).get('result', [])
        for item in results:
            title = item.get('title', 'No Title')
            # Extract authors from the author string (if available)
            authors_string = item.get('authorString', '')
            authors = [a.strip() for a in authors_string.split(',')] if authors_string else []
            year = item.get('pubYear', 'Unknown')
            abstract = item.get('abstractText', '')
            publications.append(
                Publication(title=title, authors=authors, year=year, abstract=abstract)
            )
        return publications

    def search(self, query: str) -> ResultPage:
        """
        Search Europe PMC for articles matching the query and return a ResultPage.

        Args:
            query (str): The search query.

        Returns:
            ResultPage: A page of results with Publication items.
        """
        self.log(f'Query: {query}')
        params = {
            'query': query,
            'format': 'json',
            'pageSize': 10,  # Limit results for this example
        }
        response = requests.get(self.query_root, params=params)
        response.raise_for_status()
        data = response.json()
        items = self.extract_items(data)
        total = int(data.get('hitCount', len(items)))
        self.log(f'Found {total} results')
        return ResultPage(
            query=query,
            total=total,
            items_per_page=len(items),
            start_index=0,
            items=items,
        )
