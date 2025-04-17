from scholarly import scholarly
from pysota.core import Provider, ResultPage, Publication
from pydantic import Field


class ScholarlyProvider(Provider):
    """
    Provider for querying Google Scholar using the 'scholarly' package.

    This provider uses scholarly.search_pubs() to get publication results and then
    enriches each result with additional details using scholarly.fill(). Note that
    this approach relies on web scraping, so care must be taken not to exceed rate limits.
    """

    name: str = Field(default='GoogleScholar', frozen=True)
    query_root: str = Field(
        default='', frozen=True
    )  # Not used because scholarly accepts the query directly.

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
        Extract Publication objects from the list of publication dictionaries returned by scholarly.

        Args:
            payload: A list of publication dictionaries from scholarly.search_pubs().

        Returns:
            list[Publication]: A list of Publication objects containing title, authors, year, and abstract.
        """
        publications = []
        for pub in payload:
            # Enrich the publication details by fetching full data
            filled_pub = scholarly.fill(pub)
            bib = filled_pub.get('bib', {})
            title = bib.get('title', 'No Title')
            # Authors are returned as a single string; split into a list if present
            authors = bib.get('author', '')
            authors_list = authors.split(', ') if authors else []
            year = bib.get('pub_year', 'Unknown')
            abstract = bib.get('abstract', '')
            publications.append(
                Publication(title=title, authors=authors_list, year=year, abstract=abstract)
            )
        return publications

    def search(self, query: str) -> ResultPage:
        """
        Perform a search on Google Scholar using scholarly and return a ResultPage.

        Args:
            query (str): The search query.

        Returns:
            ResultPage: A page of results with Publication items.
        """
        self.log(f'Querying Google Scholar (Scholarly): {query}')
        # Get an iterator for publication results
        pub_iterator = scholarly.search_pubs(query)
        # Convert the iterator to a list (beware of potential delays/rate limits)
        pub_list = list(pub_iterator)
        items = self.extract_items(pub_list)
        total = len(items)
        self.log(f'Found {total} results')
        return ResultPage(
            query=query,
            total=total,
            items_per_page=total,
            start_index=0,
            items=items,
        )
