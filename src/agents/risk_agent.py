from src.agents.state import AdvisorState
from src.knowledge_graph.graph_queries import get_bottleneck_courses


class RiskAgent:
    """Transparent planning-risk indicator, not a graduation prediction model."""

    def __init__(self, kg, schedule_analyzer, credit_validator):
        self.kg = kg
        self.schedule_analyzer = schedule_analyzer
        self.credit_validator = credit_validator

    def _completed_ids(self, student) -> set[str]:
        if isinstance(student, dict):
            history = student.get("academic_history", []) or []
            from_history = set()
            for semester in history:
                for item in semester.get("courses", []) if isinstance(semester, dict) else []:
                    cid = item.get("course_id") or item.get("code") or item.get("id")
                    grade = str(item.get("grade", "A")).strip().upper()
                    if cid and grade not in {"F", "W", "I"}:
                        from_history.add(cid)
            if from_history:
                return from_history
            raw = student.get("completed", student.get("completed_courses", []))
            ids = set()
            for item in raw:
                if isinstance(item, str):
                    ids.add(item)
                elif isinstance(item, dict):
                    cid = item.get("course_id") or item.get("id")
                    if cid:
                        ids.add(cid)
            return ids
        return set(getattr(student, "completed_course_ids", set()))

    def assess_risk(self, student) -> dict:
        completed = self._completed_ids(student)
        required = [cid for cid in self.kg.degree_requirements.get("required_courses", []) if cid in self.kg.courses]
        remaining = [cid for cid in required if cid not in completed]

        # Bottleneck scores use formal dependencies with higher weight and
        # prerequisite-knowledge dependencies as readiness signals.
        ranked = get_bottleneck_courses(self.kg, top_n=20)
        remaining_bottlenecks = [(cid, score) for cid, score in ranked if cid in remaining and score > 0]

        # Keep the score interpretable and conservative. It measures planning
        # complexity, not probability of graduation.
        remaining_ratio = len(remaining) / max(1, len(required))
        bottleneck_component = min(40, sum(min(score, 10) for _, score in remaining_bottlenecks[:5]))
        remaining_component = min(40, round(remaining_ratio * 40))

        # Unverified credit rules do not contribute to risk.
        credit_summary = None
        try:
            credit_summary = self.credit_validator.calculate_student_credits(student)
        except Exception:
            credit_summary = None

        source_uncertainty = 10 if self.kg.degree_requirements.get("total_credits_required_status") != "VERIFIED" else 0
        risk_score = min(90, bottleneck_component + remaining_component + source_uncertainty)

        if risk_score >= 65:
            level = "HIGH"
        elif risk_score >= 35:
            level = "MODERATE"
        else:
            level = "LOW"

        factors = []
        if remaining:
            factors.append(f"{len(remaining)} source-defined required courses remain in the planning dataset.")
        if remaining_bottlenecks:
            factors.append(
                "High-impact remaining courses: " + ", ".join(f"{cid} (score {score})" for cid, score in remaining_bottlenecks[:5])
            )
        if source_uncertainty:
            factors.append("Official total-credit graduation minimum is not verified by the supplied source set, so no hard credit-deficit penalty was applied.")

        return {
            "level": level,
            "score": risk_score,
            "metric": "PLANNING_RISK_INDICATOR",
            "remaining_required_courses": remaining,
            "bottlenecks": [{"course_id": cid, "score": score} for cid, score in remaining_bottlenecks[:10]],
            "factors": factors,
            "credit_summary": credit_summary.__dict__ if credit_summary else None,
            "disclaimer": "This is a deterministic academic-planning indicator, not a statistical prediction of graduation outcome."
        }

    def process(self, state: AdvisorState) -> AdvisorState:
        if state.get("student"):
            return {"risk_assessment": self.assess_risk(state["student"])}
        return {}
