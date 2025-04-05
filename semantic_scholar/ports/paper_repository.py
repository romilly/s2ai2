from typing import List, Optional
from semantic_scholar.domain.paper import Paper

class PaperRepository:
    def __init__(self, api_client):
        self.api_client = api_client

    def search_papers(self, query: str, limit: int = 10) -> List[Paper]:
        response = self.api_client.search_papers(query, limit)
        return [Paper(
            paper_id=paper['paperId'],
            title=paper['title'],
            abstract=paper.get('abstract'),
            year=paper.get('year'),
            authors=[author['name'] for author in paper.get('authors', [])]
        ) for paper in response['data']]

    def save_papers(self, papers: List[Paper]) -> None:
        """Save a list of papers to the repository.

        This method should be implemented by concrete repository classes.
        The base implementation does nothing.
        """
        pass

    def get_paper(self, paper_id: str) -> Optional[Paper]:
        """Retrieve a paper by its ID.

        This method should be implemented by concrete repository classes.
        The base implementation returns None.
        """
        return None