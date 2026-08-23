from dataclasses import dataclass
import re
from typing import Optional
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.knowledge_graph.graph_queries import get_prerequisites, get_equivalent_courses
from src.rag.vector_store import AcademicVectorStore

@dataclass
class RetrievalResult:
    graph_context: str
    policy_context: str
    course_context: str
    citations: list[dict]
    raw_chunks: list[dict]

class GraphRAGRetriever:
    def __init__(self, kg: AcademicKnowledgeGraph, vector_store: AcademicVectorStore):
        self.kg = kg
        self.vector_store = vector_store
    
    def retrieve(self, query: str, student=None, top_k: int = 5) -> RetrievalResult:
        course_ids = self._extract_course_references(query)
        
        # 1. Graph retrieval
        graph_context, graph_citations = self._get_graph_context(course_ids, student)
        
        # 2. Vector retrieval
        vector_results = self.vector_store.search(query, n_results=top_k)
        
        policy_context = ""
        course_context = ""
        policy_citations = []
        raw_chunks = []
        
        for res in vector_results:
            raw_chunks.append(res)
            meta = res.get("metadata", {})
            if meta.get("type") == "policy":
                policy_context += f"{res['content']}\n\n"
                policy_citations.append({
                    "type": "policy",
                    "reference": f"Policy {meta.get('section_id', '')}: {meta.get('section_title', '')}",
                    "content": res['content']
                })
            elif meta.get("type") == "course":
                course_context += f"{res['content']}\n\n"
        
        citations = graph_citations + policy_citations
        
        return RetrievalResult(
            graph_context=graph_context.strip(),
            policy_context=policy_context.strip(),
            course_context=course_context.strip(),
            citations=citations,
            raw_chunks=raw_chunks
        )
    
    def _extract_course_references(self, query: str) -> list[str]:
        found = []
        for course_id in self.kg.courses.keys():
            if course_id.lower() in query.lower() or course_id.replace(" ", "").lower() in query.replace(" ", "").lower():
                found.append(course_id)
        return list(set(found))
    
    def _get_graph_context(self, course_ids: list[str], student=None) -> tuple[str, list]:
        context_lines = []
        citations = []
        
        for cid in course_ids:
            course = self.kg.get_course(cid)
            if not course:
                continue
                
            context_lines.append(f"Knowledge Graph info for {cid} ({course.name}):")
            
            prereqs = get_prerequisites(self.kg, cid)
            if prereqs:
                context_lines.append(f"  - Prerequisites: {', '.join(prereqs)}")
                citations.append({
                    "type": "graph",
                    "reference": f"Prerequisite requirement for {cid}",
                    "content": f"{cid} requires {', '.join(prereqs)}"
                })
            
            equivs = get_equivalent_courses(self.kg, cid)
            if equivs:
                context_lines.append(f"  - Equivalent courses: {', '.join(equivs)}")
                
        if student:
            context_lines.append(f"\nStudent Profile:")
            if hasattr(student, 'major'):
                context_lines.append(f"  - Major: {student.major}")
            if hasattr(student, 'completed_courses'):
                completed_credits = 0
                for c in student.completed_courses:
                    if hasattr(c, 'credits'):
                        completed_credits += getattr(c, 'credits', 0)
                    elif isinstance(c, str) and c in self.kg.courses:
                        completed_credits += self.kg.courses[c].credits
                context_lines.append(f"  - Completed Credits: {completed_credits}")
            
        return "\n".join(context_lines), citations
