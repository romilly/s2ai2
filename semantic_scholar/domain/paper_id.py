from dataclasses import dataclass

@dataclass
class PaperId:
    sha: str  # The paper ID (string)
    corpus_id: int  # The corpus ID (int64)
    is_primary: bool  # Whether this is the primary paper ID for the corpus
