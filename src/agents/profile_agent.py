from src.agents.state import AdvisorState


class ProfileAgent:
    """Normalize student information into a predictable advising context."""

    def _completed(self, student) -> list[str]:
        if not student:
            return []
        if isinstance(student, dict):
            raw = student.get("completed", student.get("completed_courses", []))
        else:
            raw = getattr(student, "completed_courses", [])

        result = []
        for item in raw:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                cid = item.get("course_id") or item.get("id")
                grade = item.get("grade")
                if cid and grade not in {"F", "W", "I"}:
                    result.append(cid)
            else:
                cid = getattr(item, "course_id", None)
                grade = getattr(item, "grade", None)
                if cid and grade not in {"F", "W", "I"}:
                    result.append(cid)
        return sorted(set(result))

    def build_profile(self, student) -> dict:
        if not student:
            return {"available": False, "completed_course_ids": []}

        if isinstance(student, dict):
            getter = student.get
        else:
            getter = lambda key, default=None: getattr(student, key, default)

        goals = getter("career_goals", []) or []
        if isinstance(goals, str):
            goals = [goals]
        single_goal = getter("career_goal", None)
        if single_goal and single_goal not in goals:
            goals.append(single_goal)

        return {
            "available": True,
            "student_id": getter("id", getter("student_id", "STUDENT")),
            "name": getter("name", "Student"),
            "major": getter("major", "Computer Science & Engineering"),
            "current_semester": getter("current_semester", getter("semester", None)),
            "current_year": getter("current_year", None),
            "completed_course_ids": self._completed(student),
            "planned_course_ids": getter("planned", getter("planned_courses", [])) or [],
            "career_goals": goals,
            "expected_graduation": getter("expected_grad", getter("expected_graduation", None)),
            "max_credits_per_semester": getter("max_credits_per_semester", None),
            "academic_metric": getter("cgpa", getter("gpa", None)),
        }

    def process(self, state: AdvisorState) -> AdvisorState:
        return {"student_profile": self.build_profile(state.get("student"))}
