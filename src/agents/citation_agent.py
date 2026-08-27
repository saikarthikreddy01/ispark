from src.agents.state import AdvisorState


class CitationAgent:
    """Deduplicate citations and expose evidence quality for final synthesis."""

    def process(self, state: AdvisorState) -> AdvisorState:
        seen = set()
        cleaned = []
        for cite in state.get("citations", []):
            key = (cite.get("reference"), cite.get("source_status"), cite.get("content"))
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(cite)

        quality = {
            "total": len(cleaned),
            "curriculum_derived": sum(1 for c in cleaned if c.get("source_status") == "CURRICULUM_DERIVED"),
            "verified": sum(1 for c in cleaned if c.get("source_status") in {"VERIFIED", "VERIFIED_FROM_COURSE_STRUCTURE"}),
            "unverified": sum(1 for c in cleaned if c.get("source_status") in {"UNVERIFIED", "AUTHORITATIVE_RULE_REQUIRED"}),
        }
        return {"citations": cleaned, "citation_quality": quality}
