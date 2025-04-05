import requests
import time
from typing import Dict, Any

class SemanticScholarApiClient:
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    def __init__(self, max_retries: int = 3, initial_delay: float = 1.0):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        
    def search_papers(self, query: str, limit: int = 10) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "paperId,title,abstract,year,authors"
        }
        
        return self._make_request("GET", endpoint, params)
    
    def _make_request(self, method: str, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        delay = self.initial_delay
        
        for attempt in range(self.max_retries):
            try:
                response = requests.request(method, url, params=params)
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit exceeded
                    if attempt == self.max_retries - 1:
                        raise
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    raise