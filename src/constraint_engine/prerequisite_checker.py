from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.models.course import Semester, PrerequisiteType
from src.models.pathway import Conflict, ConflictType

class PrerequisiteChecker:
    def __init__(self, kg: AcademicKnowledgeGraph):
        self.kg = kg
    
    def check_prerequisites(self, course_id: str, completed: set[str]) -> tuple[bool, list[str]]:
        """
        Checks if prerequisites for a course are satisfied.
        Returns (is_satisfied, list_of_missing_course_ids).
        """
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
                    if prereq.course_id in completed:
                        group_satisfied = True
                        break
                    else:
                        missing_in_group.append(prereq.course_id)
            else: # AND
                # Need all satisfied
                group_satisfied = True
                for prereq in group.prerequisites:
                    if prereq.course_id not in completed:
                        group_satisfied = False
                        missing_in_group.append(prereq.course_id)
                        
            if not group_satisfied:
                all_groups_satisfied = False
                missing_overall.extend(missing_in_group)
                
        return all_groups_satisfied, list(set(missing_overall))
    
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
    
    def validate_semester_plan(self, planned_courses: list[str], completed: set[str], semester: Semester) -> list[Conflict]:
        """
        Validates all courses in a proposed semester plan.
        """
        conflicts = []
        planned_set = set(planned_courses)
        
        for course_id in planned_courses:
            course = self.kg.get_course(course_id)
            if not course:
                continue
                
            # 4. Already completed?
            if course_id in completed:
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
            prereqs_met, missing_prereqs = self.check_prerequisites(course_id, completed)
            if not prereqs_met:
                # Check if any can be taken concurrently and are in planned_set
                still_missing = []
                for p_id in missing_prereqs:
                    can_concurrent = False
                    for group in course.prerequisite_groups:
                        for p in group.prerequisites:
                            if p.course_id == p_id and p.can_be_concurrent:
                                can_concurrent = True
                    
                    if not (can_concurrent and p_id in planned_set):
                        still_missing.append(p_id)
                        
                if still_missing:
                    conflicts.append(Conflict(
                        type=ConflictType.PREREQUISITE_MISSING,
                        course_id=course_id,
                        description=f"Missing prerequisites for {course_id}: {', '.join(still_missing)}",
                        severity="error"
                    ))
                    
            # 2. Corequisites met?
            coreqs_met, missing_coreqs = self.check_corequisites(course_id, planned_set, completed)
            if not coreqs_met:
                conflicts.append(Conflict(
                    type=ConflictType.COREQUISITE_MISSING,
                    course_id=course_id,
                    description=f"Missing corequisites for {course_id}: {', '.join(missing_coreqs)}",
                    severity="error"
                ))
                
        return conflicts
