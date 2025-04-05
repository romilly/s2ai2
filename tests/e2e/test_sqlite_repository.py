import pytest
import os
from semantic_scholar.adapters.sqlite_repository import SqlitePaperRepository
from semantic_scholar.domain.paper import Paper

@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test.db")

@pytest.fixture
def repository(db_path):
    return SqlitePaperRepository(db_path)

def test_save_and_retrieve_paper(repository):
    # Arrange
    paper = Paper(
        paper_id="123",
        title="Test Paper",
        abstract="Test Abstract",
        year=2023,
        authors=["Author 1", "Author 2"]
    )
    
    # Act
    repository.save_papers([paper])
    retrieved_paper = repository.get_paper("123")
    
    # Assert
    assert retrieved_paper is not None
    assert retrieved_paper.paper_id == paper.paper_id
    assert retrieved_paper.title == paper.title
    assert retrieved_paper.abstract == paper.abstract
    assert retrieved_paper.year == paper.year
    assert retrieved_paper.authors == paper.authors