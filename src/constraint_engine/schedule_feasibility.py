import math
import networkx as nx
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.knowledge_graph.graph_queries import get_bottleneck_courses
from src.models.course import Semester
from src.models.student import StudentProfile
from src.models.pathway import SemesterPlan
from src.constraint_engine.prerequisite_checker import PrerequisiteChecker
from src.models.graph_schema import REL_REQUIRES


class ScheduleAnalyzer:
    """Deterministic candidate-schedule generator.

    This module does not claim to predict graduation. It sequences source-defined
    required courses using verified FORMAL prerequisites and reports uncertainty
    when official credit/registration rules are absent.
    """

    def __init__(self, kg: AcademicKnowledgeGraph):
        self.kg = kg
        self.prereq_checker = PrerequisiteChecker(kg)

    def check_course_availability(self, course_id: str, semester: Semester) -> bool:
        course = self.kg.get_course(course_id)
        if not course:
            return False
        offered = {s.value if hasattr(s, "value") else str(s) for s in course.offered_semesters}
        return not offered or semester.value in offered

    def _extract_grades(self, student) -> dict[str, str]:
        grades = {}
        completed = student.get("completed", student.get("completed_courses", [])) if isinstance(student, dict) else getattr(student, "completed_courses", [])
        for item in completed:
            if isinstance(item, str):
                grades[item] = "A"
            elif isinstance(item, dict):
                cid = item.get("course_id") or item.get("id")
                if cid:
                    grades[cid] = item.get("grade", "A")
            elif hasattr(item, "course_id"):
                grades[item.course_id] = getattr(item, "grade", "A")
        return grades

    def _formal_graph(self) -> nx.DiGraph:
        g = nx.DiGraph()
        for u, v, data in self.kg.graph.edges(data=True):
            if data.get("type") == REL_REQUIRES:
                g.add_edge(u, v)
        return g

    def analyze_graduation_feasibility(self, student: StudentProfile) -> dict:
        completed_grades = self._extract_grades(student)
        completed_ids = set(completed_grades)
        required = [cid for cid in self.kg.degree_requirements.get("required_courses", []) if cid in self.kg.courses]
        remaining = [cid for cid in required if cid not in completed_ids]

        formal_graph = self._formal_graph()
        remaining_subgraph = formal_graph.subgraph(set(remaining) | set(completed_ids)).copy()

        longest_formal_chain = 0
        if remaining_subgraph.nodes and nx.is_directed_acyclic_graph(remaining_subgraph):
            for target in remaining:
                if not remaining_subgraph.has_node(target):
                    continue
                ancestors = nx.ancestors(remaining_subgraph, target)
                unresolved = ancestors - completed_ids
                if unresolved:
                    sub = remaining_subgraph.subgraph(unresolved | {target}).copy()
                    try:
                        longest_formal_chain = max(longest_formal_chain, nx.dag_longest_path_length(sub))
                    except Exception:
                        pass

        max_credits = getattr(student, "max_credits_per_semester", 18) if not isinstance(student, dict) else student.get("max_credits_per_semester", 18)
        remaining_credits = sum(self.kg.get_course_credits(cid) for cid in remaining)
        credit_packing_floor = math.ceil(remaining_credits / max(1, max_credits)) if remaining_credits else 0
        dependency_floor = longest_formal_chain + (1 if remaining else 0)
        earliest_semesters = max(credit_packing_floor, dependency_floor)

        bottleneck_rank = get_bottleneck_courses(self.kg, top_n=20)
        bottlenecks = [{"course_id": cid, "score": score} for cid, score in bottleneck_rank if cid in remaining and score > 0][:10]

        credit_target_status = self.kg.degree_requirements.get("total_credits_required_status", "UNVERIFIED")
        return {
            "remaining_required_courses": remaining,
            "remaining_required_course_credits": remaining_credits,
            "earliest_candidate_semesters": earliest_semesters,
            "semesters_remaining": earliest_semesters,
            "formal_dependency_floor": dependency_floor,
            "credit_packing_floor": credit_packing_floor,
            "bottleneck_courses": bottlenecks,
            "credit_target_status": credit_target_status,
            "can_graduate_on_time": None,
            "risk_score": None,
            "reason": (
                "A yes/no on-time graduation claim is withheld because the supplied source set does not verify all graduation, offering, and credit-load rules."
            ),
        }

    def suggest_semester_load(self, student: StudentProfile, target_graduation: str = None, max_difficulty_score: int = 14) -> list[SemesterPlan]:
        completed_grades = self._extract_grades(student)
        required = [cid for cid in self.kg.degree_requirements.get("required_courses", []) if cid in self.kg.courses]
        remaining = [cid for cid in required if cid not in completed_grades]

        current_semester = getattr(student, "current_semester", None) or Semester.FALL
        current_year = getattr(student, "current_year", 1)
        max_credits = getattr(student, "max_credits_per_semester", 18)

        def next_semester(sem, year):
            # Summer is not assumed unless explicitly requested; alternate Fall/Spring.
            if sem == Semester.FALL:
                return Semester.SPRING, year
            return Semester.FALL, year + 1

        plans: list[SemesterPlan] = []
        current_grades = dict(completed_grades)
        unscheduled = list(remaining)
        safety = 0

        while unscheduled and safety < 12:
            safety += 1
            candidates = []
            for cid in unscheduled:
                course = self.kg.get_course(cid)
                if not course or not self.check_course_availability(cid, current_semester):
                    continue
                formal_ok, _ = self.prereq_checker.check_prerequisites(cid, current_grades)
                if formal_ok:
                    candidates.append(course)

            # Prefer lower semester index, then high downstream impact, then difficulty.
            bottleneck_scores = dict(get_bottleneck_courses(self.kg, top_n=len(self.kg.courses)))
            candidates.sort(key=lambda c: (c.sem or 99, -bottleneck_scores.get(c.id, 0), c.difficulty_level, c.id))

            chosen = []
            credits = 0
            difficulty = 0
            for course in candidates:
                if credits + course.credits > max_credits:
                    continue
                if difficulty + course.difficulty_level > max_difficulty_score:
                    continue
                chosen.append(course.id)
                credits += course.credits
                difficulty += course.difficulty_level

            if chosen:
                plans.append(SemesterPlan(
                    semester=current_semester,
                    year=current_year,
                    courses=chosen,
                    total_credits=credits,
                ))
                for cid in chosen:
                    current_grades[cid] = "A"
                    unscheduled.remove(cid)

            current_semester, current_year = next_semester(current_semester, current_year)

            # If two consecutive terms cannot schedule anything, stop instead of
            # fabricating a path around unresolved constraints/offering data.
            if not chosen and safety >= 2:
                break

        return plans

    def identify_critical_path(self, remaining_courses: list[str]) -> list[str]:
        g = self._formal_graph()
        targets = [c for c in remaining_courses if g.has_node(c)]
        if not targets or not nx.is_directed_acyclic_graph(g):
            return []

        best: list[str] = []
        for target in targets:
            for source in g.nodes:
                if g.in_degree(source) == 0 and nx.has_path(g, source, target):
                    for path in nx.all_simple_paths(g, source, target):
                        if len(path) > len(best):
                            best = path
        return best
