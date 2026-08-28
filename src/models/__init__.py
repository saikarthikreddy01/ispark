"""Pydantic data models for the Academic Advising system."""

from src.models.course import (
    Course,
    CourseEquivalency,
    CreditCategory,
    Prerequisite,
    PrerequisiteGroup,
    PrerequisiteType,
    Semester,
)
from src.models.pathway import (
    Conflict,
    ConflictType,
    DegreePathway,
    PathwayConstraint,
    SemesterPlan,
)
from src.models.student import CompletedCourse, StudentProfile, GRADE_POINTS

__all__ = [
    "Course", "CourseEquivalency", "CreditCategory", "Prerequisite",
    "PrerequisiteGroup", "PrerequisiteType", "Semester",
    "Conflict", "ConflictType", "DegreePathway", "PathwayConstraint", "SemesterPlan",
    "CompletedCourse", "StudentProfile", "GRADE_POINTS",
]
