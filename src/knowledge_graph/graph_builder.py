import json
import networkx as nx
from src.models.course import Course, CourseEquivalency
from src.models.graph_schema import (
    NODE_COURSE, NODE_DEPARTMENT, NODE_CREDIT_CATEGORY,
    REL_REQUIRES, REL_KNOWLEDGE, REL_COREQUISITE, REL_EQUIVALENT,
    REL_BELONGS_TO, REL_SATISFIES
)


class AcademicKnowledgeGraph:
    """Academic graph with explicit provenance-aware relationship semantics."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.courses: dict[str, Course] = {}
        self.degree_requirements: dict = {}
        self.equivalencies: list[CourseEquivalency] = []

    def load_from_json(self, courses_path: str, degree_req_path: str, equivalencies_path: str = None) -> None:
        with open(courses_path, "r", encoding="utf-8") as f:
            for raw in json.load(f):
                course = Course.model_validate(raw)
                self.courses[course.id] = course

        # Add all course nodes first so relationship endpoints are stable.
        for course in self.courses.values():
            self._add_course_node(course)

        with open(degree_req_path, "r", encoding="utf-8") as f:
            self.degree_requirements = json.load(f)

        if equivalencies_path:
            with open(equivalencies_path, "r", encoding="utf-8") as f:
                self.equivalencies = [CourseEquivalency.model_validate(eq) for eq in json.load(f)]
            self._add_equivalencies()

    def _add_course_node(self, course: Course) -> None:
        self.graph.add_node(course.id, type=NODE_COURSE, data=course)

        dept_node_id = f"DEPT_{course.department}"
        if not self.graph.has_node(dept_node_id):
            self.graph.add_node(dept_node_id, type=NODE_DEPARTMENT, name=course.department)
        self.graph.add_edge(course.id, dept_node_id, type=REL_BELONGS_TO)

        for cat in course.credit_categories:
            cat_node_id = f"CAT_{cat.value}"
            if not self.graph.has_node(cat_node_id):
                self.graph.add_node(cat_node_id, type=NODE_CREDIT_CATEGORY, name=cat.value)
            self.graph.add_edge(course.id, cat_node_id, type=REL_SATISFIES)

        # Legacy prerequisite_groups came from syllabus fields labelled
        # "PREREQUISITE KNOWLEDGE". Preserve them as readiness relationships,
        # never as registration-blocking constraints.
        knowledge_groups = [*course.prerequisite_groups, *course.knowledge_requirement_groups]
        for group in knowledge_groups:
            for prereq in group.prerequisites:
                self.graph.add_edge(
                    prereq.course_id,
                    course.id,
                    type=REL_KNOWLEDGE,
                    logic_type=group.logic_type.value,
                    source_reference=prereq.source_reference or group.source_reference,
                    source_authority=prereq.source_authority or group.source_authority,
                )

        # Only explicitly sourced formal rules produce blocking prerequisite edges.
        for group in course.formal_prerequisite_groups:
            for prereq in group.prerequisites:
                self.graph.add_edge(
                    prereq.course_id,
                    course.id,
                    type=REL_REQUIRES,
                    logic_type=group.logic_type.value,
                    min_grade=prereq.min_grade,
                    can_be_concurrent=prereq.can_be_concurrent,
                    source_reference=prereq.source_reference or group.source_reference,
                    source_authority=prereq.source_authority or group.source_authority,
                )

        for coreq in course.corequisites:
            self.graph.add_edge(course.id, coreq, type=REL_COREQUISITE)

    def _add_equivalencies(self) -> None:
        for eq in self.equivalencies:
            if self.graph.has_node(eq.course_id) and self.graph.has_node(eq.equivalent_course_id):
                attrs = {
                    "type": REL_EQUIVALENT,
                    "notes": eq.notes,
                    "status": eq.status,
                    "requires_faculty_approval": eq.requires_faculty_approval,
                    "source_reference": eq.source_reference,
                }
                self.graph.add_edge(eq.course_id, eq.equivalent_course_id, **attrs)
                self.graph.add_edge(eq.equivalent_course_id, eq.course_id, **attrs)

    def get_course(self, course_id: str) -> Course | None:
        return self.courses.get(course_id)

    def get_all_courses(self) -> list[Course]:
        return list(self.courses.values())

    def get_department_courses(self, department: str) -> list[Course]:
        return [c for c in self.courses.values() if c.department == department]

    def get_course_credits(self, course_id: str) -> int:
        course = self.get_course(course_id)
        return course.credits if course else 0
