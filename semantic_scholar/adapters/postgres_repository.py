import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from contextlib import contextmanager
from semantic_scholar.domain.paper import Paper
from semantic_scholar.ports.paper_repository import PaperRepository
from semantic_scholar.config import DatabaseConfig

class PostgresPaperRepository(PaperRepository):
    def __init__(self, config: DatabaseConfig):
        """
        Initialize with a DatabaseConfig instance
        """
        self._config = config  # Store config as instance variable
        self._init_db()
    
    @contextmanager
    def _get_connection(self):
        conn = psycopg2.connect(self._config.dsn)  # Use the stored config
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS papers (
                        paper_id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        abstract TEXT,
                        year INTEGER,
                        authors TEXT[],
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            conn.commit()
    
    def save_papers(self, papers: List[Paper]) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                for paper in papers:
                    cur.execute("""
                        INSERT INTO papers (paper_id, title, abstract, year, authors)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (paper_id) 
                        DO UPDATE SET 
                            title = EXCLUDED.title,
                            abstract = EXCLUDED.abstract,
                            year = EXCLUDED.year,
                            authors = EXCLUDED.authors
                    """, (
                        paper.paper_id,
                        paper.title,
                        paper.abstract,
                        paper.year,
                        paper.authors if paper.authors else []
                    ))
            conn.commit()
    
    def get_paper(self, paper_id: str) -> Optional[Paper]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM papers WHERE paper_id = %s",
                    (paper_id,)
                )
                row = cur.fetchone()
                
                if row is None:
                    return None
                    
                return Paper(
                    paper_id=row['paper_id'],
                    title=row['title'],
                    abstract=row['abstract'],
                    year=row['year'],
                    authors=row['authors'] if row['authors'] else []
                )

    def search_papers(self, query: str, limit: int = 10) -> List[Paper]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM papers 
                    WHERE to_tsvector('english', title || ' ' || COALESCE(abstract, '')) @@ plainto_tsquery('english', %s)
                    LIMIT %s
                """, (query, limit))
                
                return [
                    Paper(
                        paper_id=row['paper_id'],
                        title=row['title'],
                        abstract=row['abstract'],
                        year=row['year'],
                        authors=row['authors'] if row['authors'] else []
                    )
                    for row in cur.fetchall()
                ]