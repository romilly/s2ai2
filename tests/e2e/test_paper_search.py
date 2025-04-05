import pytest
from datetime import datetime
import time
from unittest.mock import patch

from semantic_scholar.adapters.api_client import SemanticScholarApiClient
from semantic_scholar.domain.paper import Paper
from semantic_scholar.ports.paper_repository import PaperRepository

class TestPaperSearch:
    def test_search_papers_with_backoff(self):
        # Arrange
        repository = PaperRepository(SemanticScholarApiClient())
        query = "machine learning"
        
        # Act
        papers = repository.search_papers(query, limit=3)
        
        # Assert
        assert len(papers) > 0
        for paper in papers:
            assert isinstance(paper, Paper)
            assert hasattr(paper, 'paper_id')
            assert hasattr(paper, 'title')
            assert isinstance(paper.title, str)