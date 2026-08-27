from src.agents.state import AdvisorState


class ConflictAgent:
    def __init__(self, kg, prerequisite_checker, credit_validator):
        self.kg = kg
        self.prerequisite_checker = prerequisite_checker
        self.credit_validator = credit_validator

    def _completed_ids(self, student) -> set[str]:
        if isinstance(student, dict):
            raw = student.get("completed_course_ids", student.get("completed", student.get("completed_courses", [])))
            ids = set()
            for item in raw:
                if isinstance(item, str):
                    ids.add(item)
                elif isinstance(item, dict):
                    cid = item.get("course_id") or item.get("id")
                    if cid:
                        ids.add(cid)
            return ids
        return set(getattr(student, "completed_course_ids", set()))

    def detect_conflicts(self, course_ids: list[str], student, semester=None) -> list[dict]:
        conflicts = []
        completed = self._completed_ids(student)

        for cid in course_ids:
            if cid in completed:
                conflicts.append({
                    "type": "ALREADY_COMPLETED",
                    "course": cid,
                    "severity": "error",
                    "blocking": True,
                    "message": f"{cid} is already completed."
                })
                continue

            formal_ok, missing_formal = self.prerequisite_checker.check_prerequisites(cid, completed)
            if not formal_ok:
                conflicts.append({
                    "type": "MISSING_FORMAL_PREREQUISITE",
                    "course": cid,
                    "severity": "error",
                    "blocking": True,
                    "message": f"Missing formal prerequisites for {cid}: {', '.join(missing_formal)}"
                })

            ready, knowledge_gaps = self.prerequisite_checker.check_knowledge_requirements(cid, completed)
            if not ready:
                conflicts.append({
                    "type": "PREREQUISITE_KNOWLEDGE_GAP",
                    "course": cid,
                    "severity": "warning",
                    "blocking": False,
                    "message": (
                        f"Curriculum prerequisite knowledge for {cid} is not evidenced by completed courses: "
                        f"{', '.join(knowledge_gaps)}. This is advisory unless a separate formal rule is sourced."
                    )
                })
        return conflicts

    def process(self, state: AdvisorState) -> AdvisorState:
        query = state.get("query", "")
        if not query:
            messages = state.get("messages", [])
            if messages:
                query = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])

        course_ids = []
        q_lower = str(query).lower()
        for cid, course in self.kg.courses.items():
            aliases = [cid, course.name, *getattr(course, "aliases", [])]
            if any(alias and alias.lower() in q_lower for alias in aliases):
                course_ids.append(cid)

        if course_ids and state.get("student"):
            return {"conflicts": self.detect_conflicts(sorted(set(course_ids)), state["student"])}
        return {}
