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

        verified_sources = [s for s in evidence_statuses if s in {"VERIFIED", "VERIFIED_FROM_COURSE_STRUCTURE", "CURRICULUM_DERIVED"}]
        unknown_sources = [s for s in evidence_statuses if s in {"UNVERIFIED", "AUTHORITATIVE_RULE_REQUIRED"}]

        decision = "ADVISORY_OK"
        if blocking:
            decision = "BLOCKED_BY_FORMAL_CONSTRAINT"
        elif needs_faculty:
            decision = "FACULTY_REVIEW_REQUIRED"
        elif pathway_status and pathway_status != "VERIFIED":
            decision = "CANDIDATE_PLAN"

        return {
            "decision": decision,
            "blocking_conflicts": blocking,
            "readiness_warnings": warnings,
            "faculty_review_required": needs_faculty,
            "verified_evidence_count": len(verified_sources),
            "unverified_evidence_count": len(unknown_sources),
            "hard_rule_safety": "PASS" if not any(c.get("type") == "PREREQUISITE_KNOWLEDGE_GAP" and c.get("blocking") for c in conflicts) else "FAIL",
            "note": "LLM output cannot override this verification result."
        }

    def process(self, state: AdvisorState) -> AdvisorState:
        return {"verification": self.verify(state)}
