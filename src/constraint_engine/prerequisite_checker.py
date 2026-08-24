from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.models.course import Semester, PrerequisiteType
from src.models.pathway import Conflict, ConflictType

class PrerequisiteChecker:
    def __init__(self, kg: AcademicKnowledgeGraph):
        self.kg = kg
    
    def check_prerequisites(self, course_id: str, completed_grades: dict[str, str] | set[str], concurrent_courses: set[str] = None) -> tuple[bool, list[str]]:
        """
        Checks if prerequisites for a course are satisfied based on grades.
        completed_grades: dict mapping course_id to earned letter grade, or a
        set of course IDs that are assumed to have passing grades.
        concurrent_courses: set of course IDs taken in the same semester.
        Returns (is_satisfied, list_of_missing_course_ids).
        """
        if concurrent_courses is None:
            concurrent_courses = set()

        if isinstance(completed_grades, set):
            completed_grades = {course_id: "A" for course_id in completed_grades}
            
        course = self.kg.get_course(course_id)
        if not course:
            return True, []
            
        missing_overall = []
        all_groups_satisfied = True
        
        for group in course.prerequisite_groups:
            if not group.prerequisites:
                continue
                
            group_satisfied = False
            missing_in_group = []
            
            if group.logic_type == PrerequisiteType.OR:
                # Need at least one satisfied
                for prereq in group.prerequisites:
                    p_id = prereq.course_id
                    has_passing_grade = p_id in completed_grades and self._grade_meets_min(completed_grades[p_id], prereq.min_grade)
                    can_take_concurrently = prereq.can_be_concurrent and p_id in concurrent_courses
                    
                    if has_passing_grade or can_take_concurrently:
                        group_satisfied = True
                        break
                    else:
                        missing_in_group.append(p_id)
            else: # AND
                # Need all satisfied
                group_satisfied = True
                for prereq in group.prerequisites:
                    p_id = prereq.course_id
                    has_passing_grade = p_id in completed_grades and self._grade_meets_min(completed_grades[p_id], prereq.min_grade)
                    can_take_concurrently = prereq.can_be_concurrent and p_id in concurrent_courses
                    
                    if not (has_passing_grade or can_take_concurrently):
                        group_satisfied = False
                        missing_in_group.append(p_id)
                        
            if not group_satisfied:
                all_groups_satisfied = False
                missing_overall.extend(missing_in_group)
                
        return all_groups_satisfied, list(set(missing_overall))
        
    def _grade_meets_min(self, earned_grade: str, min_grade: str) -> bool:
        """Helper to compare letter grades."""
        from src.models.student import GRADE_POINTS
        earned_pt = GRADE_POINTS.get(earned_grade, 0.0)
        min_pt = GRADE_POINTS.get(min_grade, 0.0)
        if earned_pt is None or min_pt is None:
            return False
        return earned_pt >= min_pt
    
    def check_corequisites(self, course_id: str, semester_courses: set[str], completed: set[str]) -> tuple[bool, list[str]]:
        """
        Checks if corequisites are satisfied (either previously completed or taken concurrently).
        """
        course = self.kg.get_course(course_id)
        if not course:
            return True, []
            
        missing_coreqs = []
        for coreq in course.corequisites:
            if coreq not in completed and coreq not in semester_courses:
                missing_coreqs.append(coreq)
                
        return len(missing_coreqs) == 0, missing_coreqs
    
    def validate_semester_plan(self, planned_courses: list[str], completed_grades: dict[str, str], semester: Semester) -> list[Conflict]:
        """
        Validates all courses in a proposed semester plan.
        completed_grades: dict mapping course_id to earned letter grade.
        """
        conflicts = []
        planned_set = set(planned_courses)
        
        for course_id in planned_courses:
            course = self.kg.get_course(course_id)
            if not course:
                continue
                
            # 4. Already completed?
            if course_id in completed_grades and self._grade_meets_min(completed_grades[course_id], "D"):
                conflicts.append(Conflict(
                    type=ConflictType.ALREADY_COMPLETED,
                    course_id=course_id,
                    description=f"{course_id} is already completed.",
                    severity="error"
                ))
                
            # 3. Course offered this semester?
            if semester not in course.offered_semesters:
                conflicts.append(Conflict(
                    type=ConflictType.NOT_OFFERED,
                    course_id=course_id,
                    description=f"{course_id} is not typically offered in {semester.value}.",
                    severity="warning"
                ))
                
            # 1. Prerequisites met?
            prereqs_met, missing_prereqs = self.check_prerequisites(course_id, completed_grades, concurrent_courses=planned_set)
            if not prereqs_met:
                conflicts.append(Conflict(
                    type=ConflictType.PREREQUISITE_MISSING,
                    course_id=course_id,
                    description=f"Missing prerequisites for {course_id}: {', '.join(missing_prereqs)}",
                    severity="error"
                ))
                    
            # 2. Corequisites met?
            completed_set = set(completed_grades.keys())
            coreqs_met, missing_coreqs = self.check_corequisites(course_id, planned_set, completed_set)
            if not coreqs_met:
                conflicts.append(Conflict(
                    type=ConflictType.COREQUISITE_MISSING,
                    course_id=course_id,
                    description=f"Missing corequisites for {course_id}: {', '.join(missing_coreqs)}",
                    severity="error"
                ))
                
        return conflicts
