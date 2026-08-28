from dataclasses import dataclass
import re
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.knowledge_graph.graph_queries import (
    get_prerequisites,
    get_prerequisite_knowledge,
    get_equivalent_courses,
)
from src.rag.vector_store import AcademicVectorStore


@dataclass
class RetrievalResult:
    graph_context: str
    policy_context: str
    course_context: str
    citations: list[dict]
    raw_chunks: list[dict]


class GraphRAGRetriever:
    """Hybrid graph + document retrieval.

    The current document index is lexical/TF-IDF style; graph traversal provides
    explicit academic relations. Responses label relationship semantics so
    prerequisite knowledge is never silently upgraded to a formal rule.
    """

    COMMON_ALIASES = {
        "ml": "Machine Learning",
        "ai": "Artificial Intelligence",
        "daa": "Design and Analysis of Algorithms",
        "dbms": "Database Management Systems",
        "os": "Operating Systems",
        "cn": "Computer Networks",
    }

    def __init__(self, kg: AcademicKnowledgeGraph, vector_store: AcademicVectorStore):
        self.kg = kg
        self.vector_store = vector_store

    def retrieve(self, query: str, student=None, top_k: int = 5) -> RetrievalResult:
        course_ids = self._extract_course_references(query)
        graph_context, graph_citations = self._get_graph_context(course_ids, student)
        vector_results = self.vector_store.search(query, n_results=top_k)

        policy_context = ""
        course_context = ""
        policy_citations = []
        course_citations = []
        raw_chunks = []

        for res in vector_results:
            raw_chunks.append(res)
            meta = res.get("metadata", {})
            if meta.get("type") == "policy":
                policy_context += f"{res['content']}\n\n"
                policy_citations.append({
                    "type": "policy",
                    "reference": f"Policy {meta.get('section_id', meta.get('section', ''))}: {meta.get('section_title', '')}".strip(),
                    "content": res["content"],
                    "source_status": meta.get("source_status", "UNVERIFIED"),
                })
            elif meta.get("type") == "course":
                course_context += f"{res['content']}\n\n"
                course_citations.append({
                    "type": "course",
                    "reference": meta.get("reference", meta.get("course_id", "Course catalog")),
                    "content": res["content"],
                    "source_status": meta.get("source_status", "CURRICULUM_DERIVED"),
                })

        return RetrievalResult(
            graph_context=graph_context.strip(),
            policy_context=policy_context.strip(),
            course_context=course_context.strip(),
            citations=graph_citations + policy_citations + course_citations,
            raw_chunks=raw_chunks,
        )

    def _normalize(self, text: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()

    def _extract_course_references(self, query: str) -> list[str]:
        q = self._normalize(query)
        padded = f" {q} "
        found = set()

        for course_id, course in self.kg.courses.items():
            candidates = [course_id, course.name, *getattr(course, "aliases", [])]
            for candidate in candidates:
                normalized = self._normalize(candidate)
                if normalized and f" {normalized} " in padded:
                    found.add(course_id)
                    break

        # Resolve common abbreviations to exact catalog course names.
        words = set(q.split())
        for alias, canonical_name in self.COMMON_ALIASES.items():
            if alias not in words:
                continue
            canonical = self._normalize(canonical_name)
            for course_id, course in self.kg.courses.items():
                if self._normalize(course.name) == canonical:
                    found.add(course_id)

        return sorted(found)

    def _get_graph_context(self, course_ids: list[str], student=None) -> tuple[str, list]:
        context_lines = []
        citations = []

        for cid in course_ids:
            course = self.kg.get_course(cid)
            if not course:
                continue

            context_lines.append(f"Knowledge Graph info for {cid} ({course.name}):")

            formal = get_prerequisites(self.kg, cid)
            if formal:
                context_lines.append(f"  - FORMAL registration prerequisites: {', '.join(formal)}")
                citations.append({
                    "type": "graph",
                    "reference": f"Formal prerequisite relationship for {cid}",
                    "content": f"{cid} has formal prerequisites: {', '.join(formal)}",
                    "source_status": "AUTHORITATIVE_RULE_REQUIRED",
                })

            knowledge = get_prerequisite_knowledge(self.kg, cid)
            if knowledge:
                context_lines.append(f"  - Curriculum prerequisite KNOWLEDGE (non-blocking by itself): {', '.join(knowledge)}")
                citations.append({
                    "type": "graph",
                    "reference": f"Curriculum prerequisite knowledge for {cid}",
                    "content": f"{cid} lists prerequisite knowledge mapped to: {', '.join(knowledge)}",
                    "source_status": "CURRICULUM_DERIVED",
                })

            equivs = get_equivalent_courses(self.kg, cid)
            if equivs:
                context_lines.append(
                    "  - Candidate related/substitution courses requiring faculty verification: " + ", ".join(equivs)
                )

        if student:
            if isinstance(student, dict):
                major = student.get("major")
                completed = student.get("completed", student.get("completed_courses", []))
            else:
                major = getattr(student, "major", None)
                completed = getattr(student, "completed_course_ids", set())
            context_lines.append("Student Profile:")
            if major:
                context_lines.append(f"  - Major: {major}")
            context_lines.append(f"  - Completed course IDs: {', '.join(sorted(completed)) if completed else 'None supplied'}")

        return "\n".join(context_lines), citations
