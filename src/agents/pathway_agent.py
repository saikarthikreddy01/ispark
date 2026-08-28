from src.agents.state import AdvisorState
import re
from src.models.course import Semester
from src.models.student import CompletedCourse, Student, StudentProfile


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
            history_courses = []
            for term in student.get("academic_history", []) or []:
                for item in term.get("courses", []) if isinstance(term, dict) else []:
                    cid = item.get("course_id") or item.get("code") or item.get("id")
                    if not cid:
                        continue
                    history_courses.append(CompletedCourse(
                        course_id=cid,
                        grade=str(item.get("grade", "A")).strip().upper(),
                        credits=int(item.get("credits", 0) or 0),
                        gpa=item.get("gpa"),
                        month_year=item.get("month_year"),
                    ))
            if history_courses:
                completed = history_courses
            planned = student.get("planned_courses", student.get("planned", []))
            current_semester, current_year = self._parse_current_term(student.get("current_semester"), student.get("current_year"))
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
                career_goals=student.get("career_goals", []) or [],
                current_semester=current_semester,
                current_year=current_year,
            )
        return student

    def _parse_current_term(self, term, explicit_year=None) -> tuple[Semester, int]:
        """Convert labels such as 'III Year I Semester' to FALL/year 3."""
        if isinstance(term, Semester):
            return term, int(explicit_year or 1)
        text = str(term or "").strip().upper()
        if text in {"FALL", "SPRING", "SUMMER"}:
            return Semester(text), int(explicit_year or 1)
        roman_years = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5}
        match = re.search(r"\b(I{1,3}|IV|V)\s+YEAR\s*-?\s*(I|II)\s+SEMESTER\b", text)
        if match:
            year = roman_years.get(match.group(1), int(explicit_year or 1))
            semester = Semester.FALL if match.group(2) == "I" else Semester.SPRING
            return semester, year
        return Semester.FALL, int(explicit_year or 1)

    @staticmethod
    def _academic_term_label(semester: str, year: int) -> str:
        roman = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}.get(year, str(year))
        half = "I" if semester == Semester.FALL.value else "II" if semester == Semester.SPRING.value else "SUMMER"
        return f"{roman} Year {half} Semester"

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
                semester = p.semester.value if hasattr(p.semester, "value") else str(p.semester)
                plans.append({
                    "semester": semester,
                    "year": p.year,
                    "academic_term": self._academic_term_label(semester, p.year),
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
