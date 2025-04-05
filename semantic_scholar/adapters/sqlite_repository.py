import sqlite3
from typing import List, Optional
from contextlib import contextmanager
from semantic_scholar.domain.paper import Paper
from semantic_scholar.ports.paper_repository import PaperRepository

class SqlitePaperRepository(PaperRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    paper_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    abstract TEXT,
                    year INTEGER,
                    authors TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def save_papers(self, papers: List[Paper]) -> None:
        with self._get_connection() as conn:
            for paper in papers:
                conn.execute("""
                    INSERT OR REPLACE INTO papers (paper_id, title, abstract, year, authors)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    paper.paper_id,
                    paper.title,
                    paper.abstract,
                    paper.year,
                    ','.join(paper.authors) if paper.authors else None
                ))
            conn.commit()
    
    def get_paper(self, paper_id: str) -> Optional[Paper]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM papers WHERE paper_id = ?", 
                (paper_id,)
            ).fetchone()
            
            if row is None:
                return None
                
            return Paper(
                paper_id=row['paper_id'],
                title=row['title'],
                abstract=row['abstract'],
                year=row['year'],
                authors=row['authors'].split(',') if row['authors'] else []
            )