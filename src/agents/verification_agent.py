from src.agents.state import AdvisorState


class VerificationAgent:
    """Final deterministic gate between candidate advice and user-visible advice."""

    def __init__(self, kg, prerequisite_checker, credit_validator):
        self.kg = kg
        self.prerequisite_checker = prerequisite_checker
        self.credit_validator = credit_validator

    def verify(self, state: AdvisorState) -> dict:
        conflicts = state.get("conflicts", [])
        blocking = [c for c in conflicts if c.get("blocking")]
        warnings = [c for c in conflicts if not c.get("blocking")]

        pathway = state.get("pathway") or {}
        pathway_status = pathway.get("verification_status") if isinstance(pathway, dict) else None
        needs_faculty = bool(state.get("needs_faculty_approval"))

        evidence_statuses = []
        for citation in state.get("citations", []):
            status = citation.get("source_status", "UNVERIFIED")
            evidence_statuses.append(status)

        authoritative_statuses = {"VERIFIED", "VERIFIED_FROM_COURSE_STRUCTURE", "VERIFIED_FROM_SUPPLIED_DOCUMENT"}
        verified_sources = [s for s in evidence_statuses if s in authoritative_statuses]
        curriculum_sources = [s for s in evidence_statuses if s == "CURRICULUM_DERIVED"]
        unknown_sources = [s for s in evidence_statuses if s in {"UNVERIFIED", "AUTHORITATIVE_RULE_REQUIRED"}]
        formal_rule_count = sum(len(course.formal_prerequisite_groups) for course in self.kg.courses.values())
        unknown_courses = [c for c in conflicts if c.get("type") == "UNKNOWN_COURSE"]

        decision = "ADVISORY_OK"
        if state.get("query_type") == "out_of_scope":
            decision = "OUT_OF_SCOPE"
        elif unknown_courses:
            decision = "INVALID_COURSE_REFERENCE"
        elif blocking:
            decision = "BLOCKED_BY_FORMAL_CONSTRAINT"
        elif needs_faculty:
            decision = "FACULTY_REVIEW_REQUIRED"
        elif pathway_status and pathway_status != "VERIFIED":
            decision = "CANDIDATE_PLAN"
        elif state.get("query_type") == "prerequisite" and formal_rule_count == 0:
            decision = "READINESS_OK_FORMAL_RULE_UNAVAILABLE"

        return {
            "decision": decision,
            "blocking_conflicts": blocking,
            "readiness_warnings": warnings,
            "faculty_review_required": needs_faculty,
            "verified_evidence_count": len(verified_sources),
            "curriculum_evidence_count": len(curriculum_sources),
            "unverified_evidence_count": len(unknown_sources),
            "formal_rule_count": formal_rule_count,
            "hard_rule_safety": (
                "FORMAL_RULES_UNAVAILABLE"
                if state.get("query_type") == "prerequisite" and formal_rule_count == 0 and not blocking
                else "PASS" if not any(c.get("type") == "PREREQUISITE_KNOWLEDGE_GAP" and c.get("blocking") for c in conflicts) else "FAIL"
            ),
            "note": "LLM output cannot override this verification result."
        }

    def process(self, state: AdvisorState) -> AdvisorState:
        return {"verification": self.verify(state)}
