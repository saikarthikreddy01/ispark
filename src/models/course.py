"""Course-related Pydantic models for the Academic Advising system.

Academic-integrity rule:
- ``formal_prerequisite_groups`` are registration-blocking rules and must come
  from an authoritative regulation/registration source.
- ``knowledge_requirement_groups`` are readiness/background recommendations.
- legacy ``prerequisite_groups`` is retained for backward compatibility and is
  interpreted as prerequisite KNOWLEDGE, not a formal registration block.
"""

from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Optional, List, Dict, Any


class PrerequisiteType(str, Enum):
    AND = "AND"
    OR = "OR"


class Semester(str, Enum):
    FALL = "FALL"
    SPRING = "SPRING"
    SUMMER = "SUMMER"


class CreditCategory(str, Enum):
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
    course_id: str
    min_grade: Optional[str] = None
    can_be_concurrent: bool = False
    source_reference: Optional[str] = None
    source_authority: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class PrerequisiteGroup(BaseModel):
    prerequisites: list[Prerequisite]
    logic_type: PrerequisiteType = PrerequisiteType.AND
    source_reference: Optional[str] = None
    source_authority: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class Course(BaseModel):
    id: str
    name: str
    department: str
    credits: int
    description: str
    ltpc: Optional[str] = None

    # Legacy field from the initial dataset. The curriculum labels these as
    # "PREREQUISITE KNOWLEDGE", so they are NOT blocking by default.
    prerequisite_groups: list[PrerequisiteGroup] = Field(default_factory=list)
    knowledge_requirement_groups: list[PrerequisiteGroup] = Field(default_factory=list)

    # Only authoritative registration rules belong here.
    formal_prerequisite_groups: list[PrerequisiteGroup] = Field(default_factory=list)

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
    textbooks: Optional[List[Any]] = None
    reference_books: Optional[List[Any]] = None
    aliases: list[str] = Field(default_factory=list)
    source_reference: Optional[str] = None
    source_authority: Optional[str] = None
    source_status: str = "CURRICULUM_DERIVED"

    model_config = ConfigDict(extra="allow")

    @computed_field
    @property
    def prerequisites(self) -> list[str]:
        """Formal, registration-blocking prerequisite IDs only."""
        result: list[str] = []
        for group in self.formal_prerequisite_groups:
            for prereq in group.prerequisites:
                if prereq.course_id not in result:
                    result.append(prereq.course_id)
        return result

    @computed_field
    @property
    def prerequisite_knowledge(self) -> list[str]:
        """Non-blocking background/readiness course IDs."""
        result: list[str] = []
        for group in [*self.prerequisite_groups, *self.knowledge_requirement_groups]:
            for prereq in group.prerequisites:
                if prereq.course_id not in result:
                    result.append(prereq.course_id)
        return result


class CourseEquivalency(BaseModel):
    course_id: str
    equivalent_course_id: str
    notes: str = ""
    status: str = "CANDIDATE"
    requires_faculty_approval: bool = True
    source_reference: Optional[str] = None
    model_config = ConfigDict(extra="allow")
