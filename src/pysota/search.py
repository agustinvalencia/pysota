import xml.etree.ElementTree as ET

import requests
from pydantic import BaseModel

from pysota.definitions import Publication, ResultPage


class SearchEngine(BaseModel):
    verbose: bool

    def log(self, msg) -> None:
        if self.verbose:
            print(f"[SearchEngine] - {msg}")

    def arxiv(self, query: str) -> ResultPage:
        """
        Search ArXiv for papers containing the query in the title.

        See https://arxiv.org/help/api/user-manual for more information about the ArXiv API.
        """

        url = f"http://export.arxiv.org/api/query?search_query=all:{query}"
        self.log(f"Querying ArXiv : {query}")
        response = requests.get(url)
        data = response.text
        # The ArXiv API uses Atom XML
        root = ET.fromstring(data)
        total = root.find("{http://a9.com/-/spec/opensearch/1.1/}totalResults").text
        start_index = root.find(
            "{http://a9.com/-/spec/opensearch/1.1/}totalResults"
        ).text
        items_per_page = root.find(
            "{http://a9.com/-/spec/opensearch/1.1/}itemsPerPage"
        ).text
        papers = []
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            # Extract the relevant information from the XML entry
            title = entry.find("{http://www.w3.org/2005/Atom}title").text
            authors = [
                author.find("{http://www.w3.org/2005/Atom}name").text
                for author in entry.findall("{http://www.w3.org/2005/Atom}author")
            ]
            year = entry.find("{http://www.w3.org/2005/Atom}published").text[:4]
            summary = entry.find("{http://www.w3.org/2005/Atom}summary").text
            papers.append(
                Publication(title=title, authors=authors, year=year, abstract=summary)
            )
        results = ResultPage(
            query=query,
            total=total,
            items_per_page=items_per_page,
            start_index=start_index,
            items=papers,
        )
        return results
