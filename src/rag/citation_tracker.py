from dataclasses import dataclass
from typing import Optional, List, Any

@dataclass
class Citation:
    type: str  # 'policy', 'graph', 'course'
    reference: str
    content: str

class CitationTracker:
    def __init__(self):
        self.citations: list[Citation] = []
        self.citation_index: dict[str, str] = {}
    
    def register_sources_from_chunks(self, chunks: list[Any]):
        for chunk in chunks:
            meta = getattr(chunk, "metadata", {})
            sec = meta.get("section", getattr(chunk, "chunk_id", "Unknown"))
            title = meta.get("title", meta.get("name", sec))
            content = getattr(chunk, "content", "")
            self.citation_index[sec] = content
            self.add_policy_citation(sec, title, content[:120])
    
    def verify_claim(self, claim: str) -> tuple[bool, Optional[str]]:
        words = set(claim.lower().split())
        best_match = None
        best_score = 0
        for sec, text in self.citation_index.items():
            overlap = len(words.intersection(text.lower().split()))
            if overlap > best_score:
                best_score = overlap
                best_match = sec
        return (best_score >= 2, best_match)

    def add_policy_citation(self, section_id: str, section_title: str, content_snippet: str):
        self.citations.append(Citation(
            type="policy",
            reference=f"Policy {section_id}: {section_title}",
            content=content_snippet
        ))
    
    def add_graph_citation(self, description: str, path: Optional[list[str]] = None):
        ref = description
        if path:
            ref += f" ({' → '.join(path)})"
        self.citations.append(Citation(
            type="graph",
            reference=ref,
            content="Knowledge Graph Retrieval"
        ))
    
    def format_citations(self) -> str:
        if not self.citations:
            return ""
            
        lines = ["\nReferences:"]
        for i, citation in enumerate(self.citations, 1):
            lines.append(f"[{i}] {citation.reference}")
            
        return "\n".join(lines)
    
    def format_inline_citation(self, index: int) -> str:
        return f"[{index}]"
