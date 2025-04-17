import urllib.parse

import requests
from pydantic import Field

from pysota.core import Provider, Publication, ResultPage


class PubMedProvider(Provider):
    """
    Provider for querying PubMed using NCBI's free E-utilities API.

    This provider performs a two-step search:
      1. It calls the ESearch endpoint to get a list of PubMed IDs matching the query.
      2. It calls the ESummary endpoint to retrieve detailed metadata (e.g., title, authors, publication date)
         for the retrieved IDs.

    Note:
      - The PubMed API is free but subject to rate limits and usage guidelines.
      - The abstract is typically not provided by ESummary, so it is left empty.
    """

    name: str = Field(default='PubMed', frozen=True)
    # Base URLs for the ESearch and ESummary endpoints.
    query_root: str = Field(
        default='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi', frozen=True
    )
    summary_root: str = Field(
        default='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi', frozen=True
    )

    def generate_query(self, query: str) -> str:
        """
        URL-encode the search query for use in the E-utilities endpoints.

        Args:
            query (str): The search query.

        Returns:
            str: The URL-encoded query string.
        """
        return urllib.parse.quote(query)

    def extract_items(self, payload) -> list[Publication]:
        """
        Extract Publication objects from the JSON payload returned by the ESummary endpoint.

        Args:
            payload (dict): JSON response from the ESummary endpoint.

        Returns:
            list[Publication]: A list of Publication objects with title, authors, year, and abstract.
        """
        publications = []
        # ESummary JSON contains a "result" key with article data, and a "uids" list with PubMed IDs.
        result = payload.get('result', {})
        uids = result.get('uids', [])
        for uid in uids:
            item = result.get(uid, {})
            title = item.get('title', 'No Title')
            # Authors is a list of dictionaries; extract each author's name.
            authors_list = [author.get('name', '') for author in item.get('authors', [])]
            # Extract the publication date and derive the year (split by space if necessary)
            pub_date = item.get('pubdate', '')
            year = pub_date.split(' ')[0] if pub_date else -1
            # Abstract is not provided in ESummary; leave as empty string.
            abstract = ''
            publications.append(
                Publication(title=title, authors=authors_list, year=year, abstract=abstract)
            )
        return publications

    def search(self, query: str) -> ResultPage:
        """
        Search PubMed for articles matching the query and return a ResultPage containing Publication items.

        This method first uses the ESearch endpoint to get PubMed IDs, then retrieves detailed metadata via ESummary.

        Args:
            query (str): The search query.

        Returns:
            ResultPage: A page of results with Publication items.
        """
        self.log(f'Query: {query}')
        # URL-encode the query
        encoded_query = self.generate_query(query)
        # Call the ESearch endpoint to obtain a list of PubMed IDs
        esearch_params = {
            'db': 'pubmed',
            'term': encoded_query,
            'retmode': 'json',
            'retmax': 10,  # Limit to 10 results for this example
        }
        esearch_response = requests.get(self.query_root, params=esearch_params)
        esearch_response.raise_for_status()
        esearch_data = esearch_response.json()
        # Extract the list of PubMed IDs from the JSON response
        id_list = esearch_data.get('esearchresult', {}).get('idlist', [])

        if not id_list:
            # If no IDs are found, return an empty result page.
            return ResultPage(query=query, total=0, items_per_page=0, start_index=0, items=[])

        # Join the list of IDs into a comma-separated string for the ESummary query.
        ids = ','.join(id_list)
        esummary_params = {'db': 'pubmed', 'id': ids, 'retmode': 'json'}
        esummary_response = requests.get(self.summary_root, params=esummary_params)
        esummary_response.raise_for_status()
        esummary_data = esummary_response.json()

        # Convert the ESummary JSON response into a list of Publication objects.
        items = self.extract_items(esummary_data)
        total = len(items)

        self.log(f'Found {total} results')
        return ResultPage(
            query=query,
            total=total,
            items_per_page=total,
            start_index=0,
            items=items,
        )
