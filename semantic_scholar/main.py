from fastapi import FastAPI
from semantic_scholar.adapters.postgres_repository import PostgresPaperRepository
from semantic_scholar.adapters.api_client import SemanticScholarApiClient
from semantic_scholar.adapters.cached_paper_repository import CachedPaperRepository
from semantic_scholar.ports.paper_repository import PaperRepository
from semantic_scholar.config import DatabaseConfig
from semantic_scholar.adapters.web_api import create_app

class ApiRepository(PaperRepository):
    def __init__(self, api_client: SemanticScholarApiClient):
        super().__init__(api_client)

def create_application() -> FastAPI:
    # Load config from environment variables
    db_config = DatabaseConfig.from_env()
    
    # Initialize repositories
    postgres_repo = PostgresPaperRepository(db_config)
    api_client = SemanticScholarApiClient()
    api_repo = ApiRepository(api_client)
    cached_repo = CachedPaperRepository(api_repo, postgres_repo)
    
    # Create FastAPI application
    return create_app(cached_repo)

app = create_application()