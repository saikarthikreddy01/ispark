from dataclasses import dataclass
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.models.pathway import DegreePathway, PathwayConstraint


@dataclass
class CreditSummary:
    total_completed: int = 0
    total_in_progress: int = 0
    total_required: int | None = None
    remaining: int | None = None
    requirement_status: str = "UNVERIFIED"


class CreditValidator:
    """Degree-credit validator with explicit source-status handling.

    A numeric target is not treated as an official graduation rule unless the
    degree requirements file marks it VERIFIED. This prevents demo assumptions
    from becoming authoritative academic advice.
    """

    def __init__(self, kg: AcademicKnowledgeGraph):
        self.kg = kg
        self.degree_req = kg.degree_requirements

    def _official_total(self) -> tuple[int | None, str]:
        value = self.degree_req.get("total_credits_required")
        status = self.degree_req.get("total_credits_required_status", "UNVERIFIED")
        if status != "VERIFIED" or not isinstance(value, int):
            return None, status
        return value, status

    def calculate_student_credits(self, student) -> CreditSummary:
        completed = (
            student.completed_course_ids
            if hasattr(student, "completed_course_ids")
            else set(student.completed_courses if hasattr(student, "completed_courses") else [])
        )
        planned = getattr(student, "planned_courses", [])

        total_completed = sum(self.kg.get_course_credits(c) for c in completed)
        total_in_progress = 0
        for item in planned:
            cid = item if isinstance(item, str) else item.get("course_id", "") if isinstance(item, dict) else getattr(item, "course_id", "")
            total_in_progress += self.kg.get_course_credits(cid)

        total_required, status = self._official_total()
        remaining = max(0, total_required - total_completed) if total_required is not None else None
        return CreditSummary(
            total_completed=total_completed,
            total_in_progress=total_in_progress,
            total_required=total_required,
            remaining=remaining,
            requirement_status=status,
        )

    def is_overload_semester(self, credit_count: int, student=None) -> bool:
        """Only enforce a load cap when a verified policy exists."""
        policy = self.degree_req.get("semester_credit_policy", {})
        if policy.get("status") != "VERIFIED":
            return False
        limit = policy.get("max_credits")
        return isinstance(limit, int) and credit_count > limit

    def get_remaining_requirements(self, completed_ids: set[str]) -> dict:
        """Track only category requirements explicitly marked VERIFIED."""
        result = {}
        category_reqs = self.degree_req.get("category_requirements", {})

        earned: dict[str, int] = {}
        for c_id in completed_ids:
            course = self.kg.get_course(c_id)
            if not course:
                continue
            for cat in course.credit_categories:
                earned[cat.value] = earned.get(cat.value, 0) + course.credits

        for category, spec in category_reqs.items():
            if isinstance(spec, int):
                # Legacy numeric entries are deliberately not assumed official.
                required = spec
                status = "UNVERIFIED"
            else:
                required = spec.get("min_credits")
                status = spec.get("status", "UNVERIFIED")
            if status != "VERIFIED" or not isinstance(required, int):
                result[category] = {
                    "required": required,
                    "earned": earned.get(category, 0),
                    "remaining": None,
                    "status": status,
                }
                continue
            current = earned.get(category, 0)
            result[category] = {
                "required": required,
                "earned": current,
                "remaining": max(0, required - current),
                "status": status,
            }
        return result

    def validate_credits(self, completed_ids: set[str], planned_pathway: DegreePathway = None) -> list[PathwayConstraint]:
        constraints: list[PathwayConstraint] = []
        all_ids = set(completed_ids)
        if planned_pathway:
            for plan in planned_pathway.semester_plans:
                all_ids.update(plan.courses)

        total_earned = sum(self.kg.get_course_credits(c) for c in all_ids)
        total_required, status = self._official_total()
        if total_required is not None:
            constraints.append(PathwayConstraint(
                name="Total Credits",
                description=f"Verified rule requires {total_required} total credits.",
                is_satisfied=total_earned >= total_required,
                details=f"Current/planned: {total_earned}/{total_required}",
            ))

        for cat, req in self.get_remaining_requirements(all_ids).items():
            if req.get("status") == "VERIFIED" and isinstance(req.get("required"), int):
                constraints.append(PathwayConstraint(
                    name=f"{cat} Credits",
                    description=f"Verified rule requires {req['required']} credits in {cat}.",
                    is_satisfied=req["remaining"] == 0,
                    details=f"Earned/planned: {req['earned']}/{req['required']}",
                ))
        return constraints

    def check_semester_overload(self, course_ids: list[str], max_credits: int | None = None) -> PathwayConstraint:
        total = sum(self.kg.get_course_credits(c) for c in course_ids)
        policy = self.degree_req.get("semester_credit_policy", {})
        verified_limit = policy.get("max_credits") if policy.get("status") == "VERIFIED" else None
        limit = max_credits if max_credits is not None else verified_limit

        if limit is None:
            return PathwayConstraint(
                name="Semester Credit Load",
                description="No verified semester credit-cap policy is available in the current source set.",
                is_satisfied=True,
                details=f"Planned load: {total}; advisory only.",
            )

        return PathwayConstraint(
            name="Semester Credit Load",
            description=f"Maximum {limit} credits per semester.",
            is_satisfied=total <= limit,
            details=f"Planned: {total}",
        )
