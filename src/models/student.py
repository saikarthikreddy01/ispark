"""Student-related Pydantic models for the Academic Advising system."""

from pydantic import BaseModel, Field, computed_field
from typing import Optional, List, Union
from src.models.course import Semester


GRADE_POINTS: dict[str, Optional[float]] = {
    # Ten-point grading support used by the student profile.  Both O and S
    # are accepted because institutions commonly use either label for the top
    # grade.  A per-subject ``gpa`` value, when supplied, remains authoritative.
    "O": 10.0, "S": 10.0, "A+": 10.0, "A": 9.0, "A-": 8.5,
    "B+": 8.0, "B": 8.0, "B-": 7.5,
    "C+": 7.0, "C": 7.0, "C-": 6.5,
    "D+": 6.0, "D": 6.0, "D-": 5.5, "E": 5.0,
    "F": 0.0, "W": None, "I": None, "P": None, "-": None,
}

# ``-`` represents a completed binary/non-graded course in the supplied
# transcript. It earns curriculum credits but is excluded from GPA.
PASSING_GRADES = {"O", "S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "E", "P", "-"}

GRADE_RANK = {
    "F": 0, "E": 1, "D-": 2, "D": 3, "D+": 4,
    "C-": 5, "C": 6, "C+": 7,
    "B-": 8, "B": 9, "B+": 10,
    "A-": 11, "A": 12, "A+": 13, "O": 14, "S": 14, "P": 3,
}


class CompletedCourse(BaseModel):
    """A course that a student has completed or attempted."""
    course_id: str
    grade: str = "A"
    semester_taken: Optional[Semester] = None
    year: Optional[int] = 2024
    credits: int = 3
    gpa: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    month_year: Optional[str] = None
    is_transfer: bool = False


class StudentProfile(BaseModel):
    """Complete student profile with academic history."""
    id: str
    name: str
    major: str
    minor: Optional[str] = None
    enrollment_year: int = 2024
    current_semester: Optional[Semester] = None
    current_year: int = 2
    completed_courses: list[CompletedCourse] = Field(default_factory=list)
    career_goals: list[str] = Field(default_factory=list)
    max_credits_per_semester: int = 18

    @computed_field
    @property
    def gpa(self) -> float:
        """Calculate cumulative GPA from completed courses."""
        graded = []
        for course in self.completed_courses:
            point = course.gpa if course.gpa is not None else GRADE_POINTS.get(course.grade.upper())
            if point is not None:
                graded.append((course.credits, point))
        if not graded:
            return 0.0
        total_points = sum(cr * gp for cr, gp in graded)
        total_credits = sum(cr for cr, gp in graded)
        return round(total_points / total_credits, 2) if total_credits > 0 else 0.0

    @computed_field
    @property
    def total_credits_earned(self) -> int:
        """Total credits from passing courses."""
        return sum(
            c.credits for c in self.completed_courses
            if c.grade in PASSING_GRADES
        )

    @property
    def completed_course_ids(self) -> set[str]:
        """Set of course IDs the student has passed."""
        return {
            c.course_id for c in self.completed_courses
            if c.grade in PASSING_GRADES
        }


class Student(BaseModel):
    """Convenience model representing student in multi-agent and constraint subsystems."""
    id: str
    name: str
    major: str = "Computer Science & Engineering"
    gpa: float = 3.5
    completed_courses: List[Union[str, CompletedCourse]] = Field(default_factory=list)
    planned_courses: List[Union[str, dict]] = Field(default_factory=list)
    standing: str = "Good Standing"
    expected_grad: str = "May 2028"
    max_credits_per_semester: int = 18
    career_goals: List[str] = Field(default_factory=list)
    current_semester: Optional[Semester] = None
    current_year: int = 1

    @property
    def completed_course_ids(self) -> set[str]:
        res = set()
        for c in self.completed_courses:
            if isinstance(c, str):
                res.add(c)
            elif isinstance(c, CompletedCourse):
                if c.grade in PASSING_GRADES:
                    res.add(c.course_id)
            elif isinstance(c, dict):
                res.add(c.get("course_id", ""))
        return res
