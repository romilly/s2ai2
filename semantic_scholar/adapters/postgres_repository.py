import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional, Dict, Tuple
from contextlib import contextmanager
from semantic_scholar.domain.paper import Paper
from semantic_scholar.domain.paper_id import PaperId
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
                # Create papers table with corpus_id as primary key
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS papers (
                        corpus_id BIGINT PRIMARY KEY,
                        title TEXT NOT NULL,
                        abstract TEXT,
                        year INTEGER,
                        authors TEXT[],
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create paperids table to store paper ID mappings
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS paperids (
                        sha TEXT NOT NULL,
                        corpus_id BIGINT NOT NULL,
                        is_primary BOOLEAN NOT NULL,
                        CONSTRAINT paperids_pk UNIQUE (sha),
                        FOREIGN KEY (corpus_id) REFERENCES papers(corpus_id) ON DELETE CASCADE
                    )
                """)

                # Create index on corpus_id in paperids for efficient lookups
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS paperids_corpus_id_idx ON paperids (corpus_id)
                """)
            conn.commit()

    def save_papers(self, papers: List[Paper], paper_ids: Dict[int, List[Tuple[str, bool]]] = None) -> None:
        """
        Save papers and their associated paper IDs.

        Args:
            papers: List of Paper objects to save
            paper_ids: Dictionary mapping corpus_id to a list of (sha, is_primary) tuples
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                for paper in papers:
                    # Insert or update the paper
                    cur.execute("""
                        INSERT INTO papers (corpus_id, title, abstract, year, authors)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (corpus_id)
                        DO UPDATE SET
                            title = EXCLUDED.title,
                            abstract = EXCLUDED.abstract,
                            year = EXCLUDED.year,
                            authors = EXCLUDED.authors
                    """, (
                        paper.corpus_id,
                        paper.title,
                        paper.abstract,
                        paper.year,
                        paper.authors if paper.authors else []
                    ))

                    # If paper_ids are provided, save them
                    if paper_ids and paper.corpus_id in paper_ids:
                        for sha, is_primary in paper_ids[paper.corpus_id]:
                            cur.execute("""
                                INSERT INTO paperids (sha, corpus_id, is_primary)
                                VALUES (%s, %s, %s)
                                ON CONFLICT (sha)
                                DO UPDATE SET
                                    corpus_id = EXCLUDED.corpus_id,
                                    is_primary = EXCLUDED.is_primary
                            """, (sha, paper.corpus_id, is_primary))
            conn.commit()

    def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """
        Retrieve a paper by its paper ID (sha).
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # First, find the corpus_id for this paper_id
                cur.execute(
                    "SELECT corpus_id FROM paperids WHERE sha = %s",
                    (paper_id,)
                )
                paper_id_row = cur.fetchone()

                if paper_id_row is None:
                    return None

                # Then, get the paper with this corpus_id
                return self.get_paper_by_corpus_id(paper_id_row['corpus_id'])

    def get_paper_by_corpus_id(self, corpus_id: int) -> Optional[Paper]:
        """Retrieve a paper by its corpus ID."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM papers WHERE corpus_id = %s",
                    (corpus_id,)
                )
                row = cur.fetchone()

                if row is None:
                    return None

                return Paper(
                    corpus_id=row['corpus_id'],
                    title=row['title'],
                    abstract=row['abstract'],
                    year=row['year'],
                    authors=row['authors'] if row['authors'] else []
                )

    def get_paper_ids(self, corpus_id: int) -> List[PaperId]:
        """Get all paper IDs associated with a corpus ID."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM paperids WHERE corpus_id = %s",
                    (corpus_id,)
                )
                rows = cur.fetchall()

                return [
                    PaperId(
                        sha=row['sha'],
                        corpus_id=row['corpus_id'],
                        is_primary=row['is_primary']
                    ) for row in rows
                ]

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
                        corpus_id=row['corpus_id'],
                        title=row['title'],
                        abstract=row['abstract'],
                        year=row['year'],
                        authors=row['authors'] if row['authors'] else []
                    )
                    for row in cur.fetchall()
                ]