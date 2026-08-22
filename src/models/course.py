"""Course-related Pydantic models for the Academic Advising system."""

from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any


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
    PROFESSIONAL_CORE = "PROFESSIONAL_CORE"
    BASIC_SCIENCES = "BASIC_SCIENCES"
    BASIC_ENGINEERING = "BASIC_ENGINEERING"
    HUMANITIES = "HUMANITIES"
    DEPARTMENT_ELECTIVE = "DEPARTMENT_ELECTIVE"
    OPEN_ELECTIVE = "OPEN_ELECTIVE"
    PROJECT = "PROJECT"
    HONOURS = "HONOURS"
    MINORS = "MINORS"
    BINARY_GRADE = "BINARY_GRADE"
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
    model_config = ConfigDict(extra="allow")


class PrerequisiteGroup(BaseModel):
    """
    A group of prerequisites combined with a logical operator.
    For AND: ALL prerequisites in the group must be met.
    For OR: AT LEAST ONE prerequisite in the group must be met.
    """
    prerequisites: list[Prerequisite]
    logic_type: PrerequisiteType = PrerequisiteType.AND
    model_config = ConfigDict(extra="allow")


class Course(BaseModel):
    """A course in the academic catalog."""
    id: str
    name: str
    department: str
    credits: int
    description: str
    ltpc: Optional[str] = None
    prerequisite_groups: list[PrerequisiteGroup] = Field(default_factory=list)
    corequisites: list[str] = Field(default_factory=list)
    credit_categories: list[CreditCategory] = Field(default_factory=list)
    offered_semesters: list[str] = Field(default_factory=list)
    difficulty_level: int = Field(default=3, ge=1, le=5)
    sem: Optional[int] = None
    category: Optional[str] = None
    modules: Optional[List[Dict[str, Any]]] = None
    practices: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    course_outcomes: Optional[List[Dict[str, Any]]] = None
    textbooks: Optional[List[str]] = None
    reference_books: Optional[List[str]] = None
    
    model_config = ConfigDict(extra="allow")


class CourseEquivalency(BaseModel):
    """Defines that two courses can substitute for each other."""
    course_id: str
    equivalent_course_id: str
    notes: str = ""
    model_config = ConfigDict(extra="allow")
