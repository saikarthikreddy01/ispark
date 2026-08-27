from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.models.course import Semester, PrerequisiteType, PrerequisiteGroup
from src.models.pathway import Conflict, ConflictType


class PrerequisiteChecker:
    """Checks blocking registration constraints separately from readiness gaps."""

    def __init__(self, kg: AcademicKnowledgeGraph):
        self.kg = kg

    def _check_groups(
        self,
        groups: list[PrerequisiteGroup],
        completed_grades: dict[str, str] | set[str],
        concurrent_courses: set[str] | None = None,
        enforce_grade: bool = True,
    ) -> tuple[bool, list[str]]:
        concurrent_courses = concurrent_courses or set()
        if isinstance(completed_grades, set):
            completed_grades = {course_id: "A" for course_id in completed_grades}

        missing_overall: list[str] = []
        all_groups_satisfied = True

        for group in groups:
            if not group.prerequisites:
                continue

            if group.logic_type == PrerequisiteType.OR:
                group_satisfied = False
                missing = []
                for prereq in group.prerequisites:
                    p_id = prereq.course_id
                    has_course = p_id in completed_grades
                    grade_ok = has_course and (
                        not enforce_grade
                        or not prereq.min_grade
                        or self._grade_meets_min(completed_grades[p_id], prereq.min_grade)
                    )
                    concurrent_ok = prereq.can_be_concurrent and p_id in concurrent_courses
                    if grade_ok or concurrent_ok:
                        group_satisfied = True
                        break
                    missing.append(p_id)
            else:
                group_satisfied = True
                missing = []
                for prereq in group.prerequisites:
                    p_id = prereq.course_id
                    has_course = p_id in completed_grades
                    grade_ok = has_course and (
                        not enforce_grade
                        or not prereq.min_grade
                        or self._grade_meets_min(completed_grades[p_id], prereq.min_grade)
                    )
                    concurrent_ok = prereq.can_be_concurrent and p_id in concurrent_courses
                    if not (grade_ok or concurrent_ok):
                        group_satisfied = False
                        missing.append(p_id)

            if not group_satisfied:
                all_groups_satisfied = False
                missing_overall.extend(missing)

        return all_groups_satisfied, sorted(set(missing_overall))

    def check_prerequisites(
        self,
        course_id: str,
        completed_grades: dict[str, str] | set[str],
        concurrent_courses: set[str] | None = None,
    ) -> tuple[bool, list[str]]:
        """Check registration-blocking prerequisites only."""
        course = self.kg.get_course(course_id)
        if not course:
            return True, []
        return self._check_groups(
            course.formal_prerequisite_groups,
            completed_grades,
            concurrent_courses,
            enforce_grade=True,
        )

    def check_knowledge_requirements(
        self,
        course_id: str,
        completed_grades: dict[str, str] | set[str],
    ) -> tuple[bool, list[str]]:
        """Check non-blocking prerequisite knowledge/readiness."""
        course = self.kg.get_course(course_id)
        if not course:
            return True, []
        groups = [*course.prerequisite_groups, *course.knowledge_requirement_groups]
        return self._check_groups(groups, completed_grades, enforce_grade=False)

    def _grade_meets_min(self, earned_grade: str, min_grade: str) -> bool:
        from src.models.student import GRADE_POINTS
        earned_pt = GRADE_POINTS.get(earned_grade)
        min_pt = GRADE_POINTS.get(min_grade)
        if earned_pt is None or min_pt is None:
            return False
        return earned_pt >= min_pt

    def check_corequisites(self, course_id: str, semester_courses: set[str], completed: set[str]) -> tuple[bool, list[str]]:
        course = self.kg.get_course(course_id)
        if not course:
            return True, []
        missing = [c for c in course.corequisites if c not in completed and c not in semester_courses]
        return len(missing) == 0, missing

    def validate_semester_plan(self, planned_courses: list[str], completed_grades: dict[str, str], semester: Semester) -> list[Conflict]:
        conflicts: list[Conflict] = []
        planned_set = set(planned_courses)

        for course_id in planned_courses:
            course = self.kg.get_course(course_id)
            if not course:
                continue

            if course_id in completed_grades and self._grade_meets_min(completed_grades[course_id], "D"):
                conflicts.append(Conflict(
                    type=ConflictType.ALREADY_COMPLETED,
                    course_id=course_id,
                    description=f"{course_id} is already completed.",
                    severity="error",
                ))

            offered = {s.value if hasattr(s, "value") else str(s) for s in course.offered_semesters}
            if offered and semester.value not in offered:
                conflicts.append(Conflict(
                    type=ConflictType.NOT_OFFERED,
                    course_id=course_id,
                    description=f"{course_id} is not listed as offered in {semester.value}.",
                    severity="warning",
                ))

            prereqs_met, missing_prereqs = self.check_prerequisites(course_id, completed_grades, planned_set)
            if not prereqs_met:
                conflicts.append(Conflict(
                    type=ConflictType.PREREQUISITE_MISSING,
                    course_id=course_id,
                    description=f"Missing FORMAL prerequisites for {course_id}: {', '.join(missing_prereqs)}",
                    severity="error",
                ))

            ready, knowledge_gaps = self.check_knowledge_requirements(course_id, completed_grades)
            if not ready:
                # Keep readiness gaps non-blocking. ConflictType has no dedicated
                # enum in the legacy model, so use the closest existing type and
                # clearly mark severity/message as advisory.
                conflicts.append(Conflict(
                    type=ConflictType.PREREQUISITE_MISSING,
                    course_id=course_id,
                    description=(
                        f"Academic readiness warning for {course_id}: curriculum prerequisite knowledge "
                        f"not evidenced by completed courses: {', '.join(knowledge_gaps)}. "
                        "This is not treated as a registration block without a formal rule."
                    ),
                    severity="warning",
                ))

            coreqs_met, missing_coreqs = self.check_corequisites(course_id, planned_set, set(completed_grades))
            if not coreqs_met:
                conflicts.append(Conflict(
                    type=ConflictType.COREQUISITE_MISSING,
                    course_id=course_id,
                    description=f"Missing corequisites for {course_id}: {', '.join(missing_coreqs)}",
                    severity="error",
                ))

        return conflicts
