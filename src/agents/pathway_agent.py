from src.agents.state import AdvisorState
from src.models.student import Student, StudentProfile


class PathwayAgent:
    """Generate candidate semester plans from the real curriculum graph.

    The agent proposes a plan; formal validation remains the responsibility of
    the constraint engine. Elective slots are reported separately rather than
    silently hard-coding a specific elective as mandatory.
    """

    def __init__(self, kg, prerequisite_checker, credit_validator, schedule_analyzer):
        self.kg = kg
        self.prerequisite_checker = prerequisite_checker
        self.credit_validator = credit_validator
        self.schedule_analyzer = schedule_analyzer

    def _coerce_student(self, student):
        if isinstance(student, (Student, StudentProfile)):
            return student
        if isinstance(student, dict):
            completed = student.get("completed_courses", student.get("completed", []))
            planned = student.get("planned_courses", student.get("planned", []))
            return Student(
                id=student.get("id", "STUDENT"),
                name=student.get("name", "Student"),
                major=student.get("major", "Computer Science & Engineering"),
                gpa=float(student.get("gpa", 0.0) or 0.0),
                completed_courses=completed,
                planned_courses=planned,
                standing=student.get("standing", "Unknown"),
                expected_grad=student.get("expected_grad", ""),
                max_credits_per_semester=int(student.get("max_credits_per_semester", 18) or 18),
            )
        return student

    def generate_pathway(self, student) -> dict:
        student_obj = self._coerce_student(student)
        completed_ids = set(getattr(student_obj, "completed_course_ids", set()))
        requirements = self.kg.degree_requirements
        remaining_required = [
            cid for cid in requirements.get("required_courses", [])
            if cid in self.kg.courses and cid not in completed_ids
        ]

        # The legacy ScheduleAnalyzer can still produce a course ordering when
        # semester metadata is available; if not, keep a source-faithful list
        # instead of fabricating dates/courses.
        plans = []
        try:
            generated = self.schedule_analyzer.suggest_semester_load(student_obj)
            for p in generated:
                plans.append({
                    "semester": p.semester.value if hasattr(p.semester, "value") else str(p.semester),
                    "year": p.year,
                    "courses": list(p.courses),
                    "credits": p.total_credits,
                })
        except Exception:
            plans = []

        choice_slots = []
        for semester in requirements.get("semesters_structure", []):
            if semester.get("choice_slots"):
                choice_slots.append({
                    "semester": semester.get("semester"),
                    "slots": semester.get("choice_slots"),
                })

        return {
            "semesters": plans,
            "remaining_required_courses": remaining_required,
            "choice_slots": choice_slots,
            "optional_tracks": requirements.get("optional_tracks", {}),
            "verification_status": "CANDIDATE_PLAN_REQUIRES_CONSTRAINT_VALIDATION",
            "note": (
                "Specific Department/Open electives are choices unless the curriculum explicitly names them. "
                "Honours/Minors are not treated as mandatory base-degree courses."
            ),
        }

    def process(self, state: AdvisorState) -> AdvisorState:
        if state.get("query_type") == "pathway" and state.get("student"):
            return {"pathway": self.generate_pathway(state["student"])}
        return {}
