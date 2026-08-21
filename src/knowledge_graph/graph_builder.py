import json
import networkx as nx
from pathlib import Path
from src.models.course import Course, CourseEquivalency, CreditCategory
from src.models.graph_schema import (
    NODE_COURSE, NODE_DEPARTMENT, NODE_DEGREE_PROGRAM, NODE_CREDIT_CATEGORY,
    REL_REQUIRES, REL_COREQUISITE, REL_EQUIVALENT, REL_BELONGS_TO,
    REL_SATISFIES, REL_PART_OF
)

class AcademicKnowledgeGraph:
    """
    Manages the academic knowledge graph using NetworkX.
    Nodes represent courses, departments, categories, etc.
    Edges represent prerequisites, corequisites, etc.
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.courses: dict[str, Course] = {}
        self.degree_requirements: dict = {}
        self.equivalencies: list[CourseEquivalency] = []
    
    def load_from_json(self, courses_path: str, degree_req_path: str, equivalencies_path: str = None) -> None:
        """Loads data from JSON files and builds the graph."""
        with open(courses_path, 'r', encoding='utf-8') as f:
            courses_data = json.load(f)
            for cd in courses_data:
                course = Course.model_validate(cd)
                self.courses[course.id] = course
                self._add_course_node(course)
        
        with open(degree_req_path, 'r', encoding='utf-8') as f:
            self.degree_requirements = json.load(f)
            
        if equivalencies_path:
            with open(equivalencies_path, 'r', encoding='utf-8') as f:
                equiv_data = json.load(f)
                self.equivalencies = [CourseEquivalency.model_validate(eq) for eq in equiv_data]
                self._add_equivalencies()
                
    def _add_course_node(self, course: Course) -> None:
        """Adds a course node and its relationships to the graph."""
        self.graph.add_node(course.id, type=NODE_COURSE, data=course)
        
        # Department node and edge
        dept_node_id = f"DEPT_{course.department}"
        if not self.graph.has_node(dept_node_id):
            self.graph.add_node(dept_node_id, type=NODE_DEPARTMENT, name=course.department)
        self.graph.add_edge(course.id, dept_node_id, type=REL_BELONGS_TO)
        
        # Credit Categories
        for cat in course.credit_categories:
            cat_node_id = f"CAT_{cat.value}"
            if not self.graph.has_node(cat_node_id):
                self.graph.add_node(cat_node_id, type=NODE_CREDIT_CATEGORY, name=cat.value)
            self.graph.add_edge(course.id, cat_node_id, type=REL_SATISFIES)
            
        # Prerequisites
        for group in course.prerequisite_groups:
            for prereq in group.prerequisites:
                self.graph.add_edge(
                    prereq.course_id, 
                    course.id, 
                    type=REL_REQUIRES,
                    logic_type=group.logic_type.value,
                    min_grade=prereq.min_grade,
                    can_be_concurrent=prereq.can_be_concurrent
                )
                
        # Corequisites
        for coreq in course.corequisites:
            self.graph.add_edge(course.id, coreq, type=REL_COREQUISITE)
            
    def _add_equivalencies(self) -> None:
        """Adds equivalency edges between courses."""
        for eq in self.equivalencies:
            if self.graph.has_node(eq.course_id) and self.graph.has_node(eq.equivalent_course_id):
                self.graph.add_edge(eq.course_id, eq.equivalent_course_id, type=REL_EQUIVALENT, notes=eq.notes)
                self.graph.add_edge(eq.equivalent_course_id, eq.course_id, type=REL_EQUIVALENT, notes=eq.notes)

    def get_course(self, course_id: str) -> Course | None:
        """Retrieves a course by ID."""
        return self.courses.get(course_id)
        
    def get_all_courses(self) -> list[Course]:
        """Retrieves all courses."""
        return list(self.courses.values())
        
    def get_department_courses(self, department: str) -> list[Course]:
        """Retrieves all courses for a specific department."""
        return [c for c in self.courses.values() if c.department == department]
        
    def get_course_credits(self, course_id: str) -> int:
        """Gets the credit count for a course."""
        course = self.get_course(course_id)
        return course.credits if course else 0
