from src.agents.state import AdvisorState
from src.models.student import PASSING_GRADES


class ProfileAgent:
    """Normalize student information into a predictable advising context."""

    NON_PASSING = {"F", "W", "I"}

    def _academic_history(self, student) -> list[dict]:
        if not student:
            return []
        raw = student.get("academic_history", []) if isinstance(student, dict) else getattr(student, "academic_history", [])
        courses = []
        for semester in raw or []:
            semester_title = semester.get("title") if isinstance(semester, dict) else None
            for item in (semester.get("courses", []) if isinstance(semester, dict) else []):
                if not isinstance(item, dict):
                    continue
                cid = item.get("course_id") or item.get("code") or item.get("id")
                if not cid:
                    continue
                normalized = dict(item)
                normalized["course_id"] = cid
                normalized["semester"] = semester_title
                normalized["grade"] = str(item.get("grade", "A")).strip().upper()
                courses.append(normalized)
        return courses

    def _completed(self, student) -> list[str]:
        if not student:
            return []
        history = self._academic_history(student)
        if history:
            return sorted({item["course_id"] for item in history if item.get("grade") not in self.NON_PASSING})
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
                if cid and str(grade or "A").upper() not in self.NON_PASSING:
                    result.append(cid)
            else:
                cid = getattr(item, "course_id", None)
                grade = getattr(item, "grade", None)
                if cid and str(grade or "A").upper() not in self.NON_PASSING:
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

        history = self._academic_history(student)
        completed_grades = {
            item["course_id"]: item.get("grade", "A")
            for item in history
            if item.get("grade") not in self.NON_PASSING
        }
        completed_credits = sum(
            int(item.get("credits", 0) or 0)
            for item in history
            if item.get("grade") not in self.NON_PASSING
        )
        graded_credits = sum(
            int(item.get("credits", 0) or 0)
            for item in history
            if item.get("grade") in PASSING_GRADES and item.get("grade") not in {"-", "P"}
        )

        return {
            "available": True,
            "student_id": getter("id", getter("student_id", "STUDENT")),
            "name": getter("name", "Student"),
            "major": getter("major", "Computer Science & Engineering"),
            "current_semester": getter("current_semester", getter("semester", None)),
            "current_year": getter("current_year", None),
            "completed_course_ids": self._completed(student),
            "completed_course_grades": completed_grades,
            "academic_history": history,
            "completed_credits": completed_credits,
            "graded_credits": graded_credits,
            "planned_course_ids": getter("planned", getter("planned_courses", [])) or [],
            "career_goals": goals,
            "expected_graduation": getter("expected_grad", getter("expected_graduation", None)),
            "max_credits_per_semester": getter("max_credits_per_semester", None),
            "academic_metric": getter("cgpa", getter("gpa", None)),
            "gpa_scale": getter("gpa_scale", 10),
        }

    def process(self, state: AdvisorState) -> AdvisorState:
        return {"student_profile": self.build_profile(state.get("student"))}
