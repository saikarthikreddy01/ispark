from src.agents.state import AdvisorState


class FacultyEscalationAgent:
    """Prepare, but never auto-approve, exceptional academic cases."""

    def process(self, state: AdvisorState) -> AdvisorState:
        if not state.get("needs_faculty_approval"):
            return {"faculty_packet": None}

        query = state.get("query", "")
        profile = state.get("student_profile", {})
        substitutions = state.get("substitutions", [])
        conflicts = state.get("conflicts", [])

        packet = {
            "status": "PENDING_HUMAN_REVIEW",
            "student_id": profile.get("student_id"),
            "student_name": profile.get("name"),
            "request": query,
            "exception_request": state.get("exception_request"),
            "candidate_substitutions": substitutions,
            "blocking_conflicts": [c for c in conflicts if c.get("blocking")],
            "readiness_warnings": [c for c in conflicts if not c.get("blocking")],
            "evidence": [
                {
                    "reference": c.get("reference"),
                    "source_status": c.get("source_status"),
                }
                for c in state.get("citations", [])
            ],
            "decision_authority": "FACULTY/HOD",
            "agent_action": "RECOMMEND_REVIEW_ONLY",
        }
        return {"faculty_packet": packet}
