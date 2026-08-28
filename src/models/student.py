"""Student-related Pydantic models for the Academic Advising system."""

from pydantic import BaseModel, Field, computed_field
from typing import Optional, List, Union
from src.models.course import Semester


GRADE_POINTS: dict[str, Optional[float]] = {
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "D-": 0.7,
    "F": 0.0, "W": None, "I": None, "P": None,
}

PASSING_GRADES = {"A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "P"}


class CompletedCourse(BaseModel):
    """A course that a student has completed or attempted."""
    course_id: str
    grade: str = "A"
    semester_taken: Optional[Semester] = None
    year: Optional[int] = 2024
    credits: int = 3
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
        graded = [
            (c.credits, GRADE_POINTS.get(c.grade))
            for c in self.completed_courses
            if GRADE_POINTS.get(c.grade) is not None
        ]
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
