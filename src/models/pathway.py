"""Pathway and constraint models for the Academic Advising system."""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from src.models.course import Semester


class ConflictType(str, Enum):
    """Types of academic conflicts that can be detected."""
    PREREQUISITE_MISSING = "PREREQUISITE_MISSING"
    COREQUISITE_MISSING = "COREQUISITE_MISSING"
    CREDIT_OVERLOAD = "CREDIT_OVERLOAD"
    SCHEDULE_CONFLICT = "SCHEDULE_CONFLICT"
    NOT_OFFERED = "NOT_OFFERED"
    ALREADY_COMPLETED = "ALREADY_COMPLETED"


class Conflict(BaseModel):
    """A detected conflict in a student's academic plan."""
    type: ConflictType
    course_id: str
    description: str
    severity: str = "error"  # "error" or "warning"
    suggested_resolution: str = ""


class SemesterPlan(BaseModel):
    """A plan for a single semester."""
    semester: Semester
    year: int
    courses: list[str] = Field(default_factory=list)
    total_credits: int = 0


class DegreePathway(BaseModel):
    """A complete semester-by-semester degree pathway."""
    student_id: str
    program: str
    semester_plans: list[SemesterPlan] = Field(default_factory=list)
    conflicts: list[Conflict] = Field(default_factory=list)
    total_credits: int = 0
    estimated_graduation: str = ""
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)


class PathwayConstraint(BaseModel):
    """Result of a constraint check on a pathway."""
    name: str
    description: str
    is_satisfied: bool
    details: str = ""
