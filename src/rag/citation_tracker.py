from dataclasses import dataclass
from typing import Optional

@dataclass
class Citation:
    type: str  # 'policy', 'graph', 'course'
    reference: str
    content: str

class CitationTracker:
    def __init__(self):
        self.citations: list[Citation] = []
    
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
