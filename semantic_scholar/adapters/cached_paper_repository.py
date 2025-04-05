from typing import List, Optional, Dict, Tuple
from semantic_scholar.domain.paper import Paper
from semantic_scholar.domain.paper_id import PaperId
from semantic_scholar.ports.paper_repository import PaperRepository

class CachedPaperRepository(PaperRepository):
    def __init__(self, api_repository: PaperRepository, db_repository: PaperRepository):
        self.api_repository = api_repository
        self.db_repository = db_repository

    def search_papers(self, query: str, limit: int = 10) -> List[Paper]:
        # The base PaperRepository.search_papers now handles saving papers
        return self.api_repository.search_papers(query, limit)

    def save_papers(self, papers: List[Paper], paper_ids: Dict[int, List[Tuple[str, bool]]] = None) -> None:
        self.db_repository.save_papers(papers, paper_ids)

    def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        paper = self.db_repository.get_paper_by_id(paper_id)
        if paper is None:
            # Could add API fallback here if needed
            return None
        return paper

    def get_paper_by_corpus_id(self, corpus_id: int) -> Optional[Paper]:
        paper = self.db_repository.get_paper_by_corpus_id(corpus_id)
        if paper is None:
            # Could add API fallback here if needed
            return None
        return paper

    def get_paper_ids(self, corpus_id: int) -> List[PaperId]:
        return self.db_repository.get_paper_ids(corpus_id)