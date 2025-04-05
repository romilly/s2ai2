from typing import List, Optional, Dict, Tuple
from semantic_scholar.domain.paper import Paper
from semantic_scholar.domain.paper_id import PaperId
from semantic_scholar.domain.author import Author
from semantic_scholar.domain.wrote import Wrote

class PaperRepository:
    def __init__(self, api_client):
        self.api_client = api_client

    def search_papers(self, query: str, limit: int = 10) -> List[Paper]:
        response = self.api_client.search_papers(query, limit)
        papers = []
        paper_ids = {}
        authors_data = {}

        for paper_data in response['data']:
            # Get the corpus ID, which is required
            corpus_id = paper_data.get('corpusId')
            if corpus_id is None:
                continue  # Skip papers without a corpus ID

            # Create the Paper object
            paper = Paper(
                corpus_id=corpus_id,
                title=paper_data['title'],
                abstract=paper_data.get('abstract'),
                year=paper_data.get('year')
            )
            papers.append(paper)

            # Store the paper ID mapping
            paper_id = paper_data.get('paperId')
            if paper_id:
                if corpus_id not in paper_ids:
                    paper_ids[corpus_id] = []
                paper_ids[corpus_id].append((paper_id, True))  # Assume this is the primary ID

            # Store the author information
            if 'authors' in paper_data and paper_data['authors']:
                if corpus_id not in authors_data:
                    authors_data[corpus_id] = []

                for i, author_data in enumerate(paper_data['authors']):
                    if 'authorId' in author_data and author_data['authorId']:
                        authors_data[corpus_id].append((
                            author_data['authorId'],
                            author_data['name'],
                            i  # Position in the author list
                        ))

        # Save the papers, their IDs, and authors
        if papers:
            self.save_papers(papers, paper_ids, authors_data)

        return papers

    def save_papers(self, papers: List[Paper], paper_ids: Dict[int, List[Tuple[str, bool]]] = None,
                   authors: Dict[int, List[Tuple[str, str, int]]] = None) -> None:
        """Save a list of papers and their associated paper IDs and authors to the repository.

        Args:
            papers: List of Paper objects to save
            paper_ids: Dictionary mapping corpus_id to a list of (sha, is_primary) tuples
            authors: Dictionary mapping corpus_id to a list of (author_id, name, position) tuples

        This method should be implemented by concrete repository classes.
        The base implementation does nothing.
        """
        pass

    def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """Retrieve a paper by its paper ID (sha).

        This method should be implemented by concrete repository classes.
        The base implementation returns None.
        """
        return None

    def get_paper_by_corpus_id(self, corpus_id: int) -> Optional[Paper]:
        """Retrieve a paper by its corpus ID.

        This method should be implemented by concrete repository classes.
        The base implementation returns None.
        """
        return None

    def get_paper_ids(self, corpus_id: int) -> List[PaperId]:
        """Get all paper IDs associated with a corpus ID.

        This method should be implemented by concrete repository classes.
        The base implementation returns an empty list.
        """
        return []

    def get_authors_for_paper(self, corpus_id: int) -> List[Author]:
        """Get all authors for a paper, ordered by their position.

        This method should be implemented by concrete repository classes.
        The base implementation returns an empty list.
        """
        return []