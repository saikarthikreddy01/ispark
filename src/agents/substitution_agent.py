from src.agents.state import AdvisorState


class SubstitutionAgent:
    def __init__(self, kg, retriever):
        self.kg = kg
        self.retriever = retriever

    def find_substitutions(self, course_id: str, student=None) -> list[dict]:
        substitutions = []
        for eq in getattr(self.kg, "equivalencies", []):
            if eq.course_id == course_id:
                other = eq.equivalent_course_id
            elif eq.equivalent_course_id == course_id:
                other = eq.course_id
            else:
                continue

            course = self.kg.courses.get(other)
            status = getattr(eq, "status", "CANDIDATE")
            substitutions.append({
                "course_id": other,
                "name": course.name if course else "Unknown",
                "status": status,
                "reason": eq.notes,
                "needs_approval": getattr(eq, "requires_faculty_approval", True) or status != "APPROVED",
                "source_reference": getattr(eq, "source_reference", None),
                "advice": (
                    "Approved substitution" if status == "APPROVED"
                    else "Candidate substitution/related course; faculty approval required before it can satisfy a degree requirement."
                ),
            })
        return substitutions

    def process(self, state: AdvisorState) -> AdvisorState:
        if state.get("query_type") != "substitution":
            return {}

        query = state.get("query", "")
        if not query:
            messages = state.get("messages", [])
            if messages:
                query = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])

        target_course = None
        q_lower = str(query).lower()
        for cid, course in self.kg.courses.items():
            candidates = [cid, course.name, *getattr(course, "aliases", [])]
            if any(c and c.lower() in q_lower for c in candidates):
                target_course = cid
                break

        if not target_course:
            return {}

        subs = self.find_substitutions(target_course, state.get("student"))
        text = f"\nSubstitution candidates for {target_course}: {subs}"
        return {
            "retrieved_context": state.get("retrieved_context", "") + text,
            "needs_faculty_approval": any(s["needs_approval"] for s in subs),
        }
