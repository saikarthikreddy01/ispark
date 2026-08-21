"""Course-related Pydantic models for the Academic Advising system."""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class PrerequisiteType(str, Enum):
    """Logical operator for combining prerequisites within a group."""
    AND = "AND"
    OR = "OR"


class Semester(str, Enum):
    """Academic semesters."""
    FALL = "FALL"
    SPRING = "SPRING"
    SUMMER = "SUMMER"


class CreditCategory(str, Enum):
    """Categories of academic credits for degree requirements."""
    CORE = "CORE"
    MATH = "MATH"
    SCIENCE = "SCIENCE"
    GENERAL_ED = "GENERAL_ED"
    ELECTIVE = "ELECTIVE"
    LAB = "LAB"
    CAPSTONE = "CAPSTONE"


class Prerequisite(BaseModel):
    """A single prerequisite course requirement."""
    course_id: str
    min_grade: str = "D"
    can_be_concurrent: bool = False


class PrerequisiteGroup(BaseModel):
    """
    A group of prerequisites combined with a logical operator.
    For AND: ALL prerequisites in the group must be met.
    For OR: AT LEAST ONE prerequisite in the group must be met.
    """
    prerequisites: list[Prerequisite]
    logic_type: PrerequisiteType = PrerequisiteType.AND


class Course(BaseModel):
    """A course in the academic catalog."""
    id: str
    name: str
    department: str
    credits: int
    description: str
    prerequisite_groups: list[PrerequisiteGroup] = Field(default_factory=list)
    corequisites: list[str] = Field(default_factory=list)
    credit_categories: list[CreditCategory] = Field(default_factory=list)
    offered_semesters: list[Semester] = Field(default_factory=list)
    difficulty_level: int = Field(default=3, ge=1, le=5)


class CourseEquivalency(BaseModel):
    """Defines that two courses can substitute for each other."""
    course_id: str
    equivalent_course_id: str
    notes: str = ""
