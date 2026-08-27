from src.agents.state import AdvisorState


class SourceRouterAgent:
    """Logical federation layer for decentralized academic authorities.

    The current MVP may store data in one process, but this agent keeps source
    authority explicit so CSE, Mathematics, and central policy stores can later
    be deployed independently without changing the supervisor contract.
    """

    def __init__(self, kg):
        self.kg = kg

    def plan_sources(self, query: str) -> dict:
        q = (query or "").lower()
        authorities = []

        course_hits = []
        for cid, course in self.kg.courses.items():
            candidates = [cid, course.name, *getattr(course, "aliases", [])]
            if any(c and c.lower() in q for c in candidates):
                course_hits.append(cid)
                dept = getattr(course, "department", None)
                if dept and dept not in authorities:
                    authorities.append(dept)

        if any(k in q for k in ["policy", "waiver", "credit", "transfer", "regulation", "graduation"]):
            authorities.append("CENTRAL_ACADEMIC_POLICY")

        if not authorities:
            authorities = ["CSE", "CENTRAL_ACADEMIC_POLICY"]

        # stable unique order
        authorities = list(dict.fromkeys(authorities))
        return {
            "mode": "FEDERATED_LOGICAL_ROUTING",
            "authorities": authorities,
            "course_targets": sorted(set(course_hits)),
            "note": "MVP federation is logical; authorities can be backed by separate stores/services later.",
        }

    def process(self, state: AdvisorState) -> AdvisorState:
        return {"source_plan": self.plan_sources(state.get("query", ""))}
