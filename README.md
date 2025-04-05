# Semantic Scholar API Integration

A Python application that integrates with the [Semantic Scholar API](https://www.semanticscholar.org/product/api) to search, retrieve, and store academic papers. This project provides a clean architecture implementation with repository pattern for data access and a FastAPI web interface.

## Features

- Search for academic papers using the Semantic Scholar API
- Store paper data in PostgreSQL database
- Support for both paperId (string) and corpusId (int64) identifiers
- Caching mechanism to reduce API calls
- RESTful API built with FastAPI
- Clean architecture with domain-driven design principles

## Architecture

The project follows a clean architecture approach with the following components:

- **Domain Layer**: Core business logic and entities
  - `Paper`: Data class representing an academic paper

- **Ports Layer**: Interfaces that define how the application interacts with external systems
  - `PaperRepository`: Abstract interface for paper data access

- **Adapters Layer**: Implementations of the interfaces defined in the ports layer
  - `SemanticScholarApiClient`: Client for the Semantic Scholar API
  - `PostgresPaperRepository`: PostgreSQL implementation of the paper repository
  - `CachedPaperRepository`: Caching decorator for paper repositories

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/semantic-scholar.git
   cd semantic-scholar
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env with your database credentials
   ```

## Paper Identifiers

The Semantic Scholar API uses two different identifiers for papers:

- **paperId** (string): The primary way to identify papers when using the Semantic Scholar website or API
- **corpusId** (int64): A second way to identify papers, commonly used in datasets

This application uses a data model where:

- Each paper is uniquely identified by its `corpusId`
- Multiple `paperId`s can map to a single `corpusId` (many-to-one relationship)
- The application stores papers in a `papers` table with `corpus_id` as the primary key
- Paper IDs are stored in a separate `paperids` table with a foreign key to the papers table
- The application provides methods to retrieve papers by either identifier

## Usage

### Running the API Server

```bash
uvicorn semantic_scholar.main:app --reload
```

The API will be available at http://localhost:8000

### Using as a Library

```python
from semantic_scholar.adapters.api_client import SemanticScholarApiClient
from semantic_scholar.ports.paper_repository import PaperRepository

# Create a repository
api_client = SemanticScholarApiClient()
repository = PaperRepository(api_client)

# Search for papers
papers = repository.search_papers("machine learning", limit=5)

# Print results
for paper in papers:
    print(f"Title: {paper.title}")
    print(f"Corpus ID: {paper.corpus_id}")
    print(f"Authors: {', '.join(paper.authors)}")
    print(f"Year: {paper.year}")
    print(f"Abstract: {paper.abstract}")
    print("---")

# Get a paper by its paper ID (sha)
paper = repository.get_paper_by_id("1234567890")

# Get a paper by its corpus ID
paper = repository.get_paper_by_corpus_id(12345678)

# Get all paper IDs for a corpus ID
paper_ids = repository.get_paper_ids(12345678)
for paper_id in paper_ids:
    print(f"SHA: {paper_id.sha}, Primary: {paper_id.is_primary}")
```

## Database Setup

### PostgreSQL

1. Create a PostgreSQL database:
   ```
   createdb papers
   ```

2. Configure the connection in your `.env` file:
   ```
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=papers
   POSTGRES_USER=your_username
   POSTGRES_PASSWORD=your_password
   ```

## Testing

1. Make sure your `.env` file includes the test database configuration:
   ```
   TEST_DB=papers_test
   ```

2. Run the tests with pytest:
   ```bash
   python -m pytest
   ```

   For specific test files:
   ```bash
   python -m pytest tests/e2e/test_paper_search.py
   python -m pytest tests/e2e/test_postgres_repository.py
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Romilly Cocking

## Resources

- [Semantic Scholar API Documentation](https://api.semanticscholar.org/api-docs/)
- [Semantic Scholar Graph API](https://www.semanticscholar.org/product/api)
