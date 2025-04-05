import os
from dotenv import load_dotenv
from semantic_scholar.adapters.api_client import SemanticScholarApiClient
from semantic_scholar.adapters.postgres_repository import PostgresPaperRepository
from semantic_scholar.config import DatabaseConfig
from semantic_scholar.ports.paper_repository import PaperRepository

# Load environment variables
load_dotenv()

# Create API client
api_client = SemanticScholarApiClient()

# Create database config
db_config = DatabaseConfig(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    name=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD')
)

# Create repositories
db_repo = PostgresPaperRepository(db_config)
api_repo = PaperRepository(api_client)

# Search for papers
query = 'phonological loop'
papers = api_repo.search_papers(query, limit=10)

print(f'Found {len(papers)} papers from API')
for i, paper in enumerate(papers):
    print(f'{i+1}. {paper.title} (Corpus ID: {paper.corpus_id})')

# Explicitly save the papers to the database
print("\nSaving papers to the database...")
db_repo.save_papers(papers)

# Now check if they were saved to the database
db_papers = db_repo.search_papers(query, limit=10)
print(f'\nFound {len(db_papers)} papers in the database')
for i, paper in enumerate(db_papers):
    print(f'{i+1}. {paper.title} (Corpus ID: {paper.corpus_id})')

    # Get authors for this paper
    authors = db_repo.get_authors_for_paper(paper.corpus_id)
    if authors:
        author_names = [author.name for author in authors]
        print(f'   Authors: {", ".join(author_names)}')
    else:
        print('   No authors found')
