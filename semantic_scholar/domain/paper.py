from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Paper:
    paper_id: str
    title: str
    abstract: Optional[str] = None
    year: Optional[int] = None
    authors: List[str] = None