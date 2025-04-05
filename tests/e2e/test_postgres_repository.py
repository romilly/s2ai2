import pytest
import os
from dotenv import load_dotenv
from semantic_scholar.adapters.postgres_repository import PostgresPaperRepository
from semantic_scholar.domain.paper import Paper
from semantic_scholar.config import DatabaseConfig

# Load environment variables from .env file
load_dotenv()

@pytest.fixture
def db_config():
    return DatabaseConfig(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', '5432')),
        name=os.getenv('TEST_DB', 'papers_test'),  # Use TEST_DB for test database
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres')
    )

@pytest.fixture
def repository(db_config):  # Use db_config fixture directly
    repo = PostgresPaperRepository(db_config)
    yield repo
    # Cleanup after tests
    with repo._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS papers")
        conn.commit()

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

def test_search_papers(repository):
    # Arrange
    papers = [
        Paper(
            paper_id="1",
            title="Machine Learning Basics",
            abstract="A paper about ML",
            year=2023,
            authors=["Author 1"]
        ),
        Paper(
            paper_id="2",
            title="Deep Neural Networks",
            abstract="A paper about DNN",
            year=2023,
            authors=["Author 2"]
        )
    ]
    repository.save_papers(papers)
    
    # Act
    results = repository.search_papers("machine learning")
    
    # Assert
    assert len(results) == 1
    assert results[0].paper_id == "1"