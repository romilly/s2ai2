# Semantic Scholar API Integration

A Python application that integrates with the Semantic Scholar API to search, retrieve, and store academic papers. This project provides a clean architecture implementation with repository pattern for data access and a FastAPI web interface.

## Features

- Search for academic papers using the Semantic Scholar API
- Store paper data in PostgreSQL or SQLite databases
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
  - `SqlitePaperRepository`: SQLite implementation of the paper repository
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
    print(f"Authors: {', '.join(paper.authors)}")
    print(f"Year: {paper.year}")
    print(f"Abstract: {paper.abstract}")
    print("---")
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

### SQLite

For SQLite, simply specify a file path when creating the repository:

```python
from semantic_scholar.adapters.sqlite_repository import SqlitePaperRepository

repository = SqlitePaperRepository("papers.db")
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
   python -m pytest tests/e2e/test_sqlite_repository.py
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Romilly Cocking
