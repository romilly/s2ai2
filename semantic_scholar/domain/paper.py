from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Paper:
    corpus_id: int  # The unique identifier for papers (int64)
    title: str
    abstract: Optional[str] = None
    year: Optional[int] = None
    authors: List[str] = None