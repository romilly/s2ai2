from typing import List, Optional
from semantic_scholar.domain.paper import Paper
from semantic_scholar.ports.paper_repository import PaperRepository

class CachedPaperRepository(PaperRepository):
    def __init__(self, api_repository: PaperRepository, db_repository: PaperRepository):
        self.api_repository = api_repository
        self.db_repository = db_repository
    
    def search_papers(self, query: str, limit: int = 10) -> List[Paper]:
        papers = self.api_repository.search_papers(query, limit)
        self.db_repository.save_papers(papers)
        return papers
    
    def save_papers(self, papers: List[Paper]) -> None:
        self.db_repository.save_papers(papers)
    
    def get_paper(self, paper_id: str) -> Optional[Paper]:
        paper = self.db_repository.get_paper(paper_id)
        if paper is None:
            # Could add API fallback here if needed
            return None
        return paper