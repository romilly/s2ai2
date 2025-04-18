import pytest
import os
from dotenv import load_dotenv
from semantic_scholar.adapters.postgres_repository import PostgresPaperRepository
from semantic_scholar.domain.paper import Paper
from semantic_scholar.domain.paper_id import PaperId
from semantic_scholar.domain.author import Author
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
    # Clean up before tests to start with a fresh state
    repo = PostgresPaperRepository(db_config)
    with repo._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS wrote")
            cur.execute("DROP TABLE IF EXISTS authors")
            cur.execute("DROP TABLE IF EXISTS paperids")
            cur.execute("DROP TABLE IF EXISTS papers")
        conn.commit()

    # Re-initialize the repository to create fresh tables
    repo = PostgresPaperRepository(db_config)

    # Return the repository for the test to use
    return repo
    # No cleanup after tests - tables are left for inspection

def test_save_and_retrieve_paper(repository):
    # Arrange
    paper = Paper(
        corpus_id=123,
        title="Test Paper",
        abstract="Test Abstract",
        year=2023
    )

    # Create paper ID mapping
    paper_ids = {123: [("paper123", True)]}

    # Create author mapping
    authors = {123: [
        ("author1", "Author One", 0),
        ("author2", "Author Two", 1)
    ]}

    # Act
    repository.save_papers([paper], paper_ids, authors)
    retrieved_paper = repository.get_paper_by_corpus_id(123)

    # Assert
    assert retrieved_paper is not None
    assert retrieved_paper.corpus_id == paper.corpus_id
    assert retrieved_paper.title == paper.title
    assert retrieved_paper.abstract == paper.abstract
    assert retrieved_paper.year == paper.year

    # Test retrieving by paper ID
    retrieved_by_id = repository.get_paper_by_id("paper123")
    assert retrieved_by_id is not None
    assert retrieved_by_id.corpus_id == paper.corpus_id

    # Test getting paper IDs
    paper_ids_list = repository.get_paper_ids(123)
    assert len(paper_ids_list) == 1
    assert paper_ids_list[0].sha == "paper123"
    assert paper_ids_list[0].corpus_id == 123
    assert paper_ids_list[0].is_primary == True

    # Test getting authors
    authors_list = repository.get_authors_for_paper(123)
    assert len(authors_list) == 2
    assert authors_list[0].author_id == "author1"
    assert authors_list[0].name == "Author One"
    assert authors_list[1].author_id == "author2"
    assert authors_list[1].name == "Author Two"

def test_search_papers(repository):
    # Arrange
    papers = [
        Paper(
            corpus_id=1,
            title="Machine Learning Basics",
            abstract="A paper about ML",
            year=2023
        ),
        Paper(
            corpus_id=2,
            title="Deep Neural Networks",
            abstract="A paper about DNN",
            year=2023
        )
    ]

    # Create paper ID mappings
    paper_ids = {
        1: [("paper1", True)],
        2: [("paper2", True)]
    }

    # Create author mappings
    authors = {
        1: [("author1", "Author One", 0)],
        2: [("author2", "Author Two", 0)]
    }

    repository.save_papers(papers, paper_ids, authors)

    # Act
    results = repository.search_papers("machine learning")

    # Assert
    assert len(results) == 1
    assert results[0].corpus_id == 1

    # Check authors
    authors_list = repository.get_authors_for_paper(1)
    assert len(authors_list) == 1
    assert authors_list[0].author_id == "author1"
    assert authors_list[0].name == "Author One"