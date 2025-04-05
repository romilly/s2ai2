from dataclasses import dataclass

@dataclass
class Wrote:
    author_id: str  # The author's ID
    corpus_id: int  # The paper's corpus ID
    position: int = 0  # The author's position in the author list (0-based)
