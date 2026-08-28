from src.agents.state import AdvisorState
import re


class ConflictAgent:
    def __init__(self, kg, prerequisite_checker, credit_validator):
        self.kg = kg
        self.prerequisite_checker = prerequisite_checker
        self.credit_validator = credit_validator

    def _completed_grades(self, student) -> dict[str, str]:
        if isinstance(student, dict):
            history = student.get("academic_history", []) or []
            grades = {}
            for semester in history:
                for item in semester.get("courses", []) if isinstance(semester, dict) else []:
                    cid = item.get("course_id") or item.get("code") or item.get("id")
                    grade = str(item.get("grade", "A")).strip().upper()
                    if cid and grade not in {"F", "W", "I"}:
                        grades[cid] = grade
            if grades:
                return grades
            raw = student.get("completed_course_ids", student.get("completed", student.get("completed_courses", [])))
            grades = {}
            for item in raw:
                if isinstance(item, str):
                    grades[item] = "A"
                elif isinstance(item, dict):
                    cid = item.get("course_id") or item.get("id")
                    if cid:
                        grades[cid] = str(item.get("grade", "A")).upper()
            return grades
        raw = getattr(student, "completed_courses", [])
        grades = {}
        for item in raw:
            if isinstance(item, str):
                grades[item] = "A"
            else:
                cid = getattr(item, "course_id", None)
                grade = str(getattr(item, "grade", "A")).upper()
                if cid and grade not in {"F", "W", "I"}:
                    grades[cid] = grade
        return grades

    def detect_conflicts(self, course_ids: list[str], student, semester=None) -> list[dict]:
        conflicts = []
        completed_grades = self._completed_grades(student)
        completed = set(completed_grades)

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

            formal_ok, missing_formal = self.prerequisite_checker.check_prerequisites(cid, completed_grades)
            if not formal_ok:
                conflicts.append({
                    "type": "MISSING_FORMAL_PREREQUISITE",
                    "course": cid,
                    "severity": "error",
                    "blocking": True,
                    "message": f"Missing formal prerequisites for {cid}: {', '.join(missing_formal)}"
                })

            ready, knowledge_gaps = self.prerequisite_checker.check_knowledge_requirements(cid, completed_grades)
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

        referenced_codes = {
            token.upper()
            for token in re.findall(r"\b(?:\d{2}[A-Za-z]{2,4}\d{3}|[A-Za-z]{2,8}\d{3,5})\b", str(query))
        }
        unknown_codes = sorted(code for code in referenced_codes if code not in self.kg.courses)
        unknown_conflicts = [
            {
                "type": "UNKNOWN_COURSE",
                "course": code,
                "severity": "error",
                "blocking": True,
                "message": f"{code} is not present in the loaded curriculum catalog. Academic eligibility cannot be verified.",
            }
            for code in unknown_codes
        ]

        if course_ids and state.get("student"):
            return {"conflicts": unknown_conflicts + self.detect_conflicts(sorted(set(course_ids)), state["student"])}
        if unknown_conflicts:
            return {"conflicts": unknown_conflicts}
        return {}
