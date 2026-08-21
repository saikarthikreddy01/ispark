from src.agents.state import AdvisorState

class SubstitutionAgent:
    def __init__(self, kg, retriever):
        self.kg = kg
        self.retriever = retriever
    
    def find_substitutions(self, course_id: str, student=None) -> list[dict]:
        subs = []
        
        for eq in getattr(self.kg, "equivalencies", []):
            if eq.course_id == course_id:
                subs.append({
                    "course_id": eq.equivalent_id,
                    "name": self.kg.courses.get(eq.equivalent_id, type('obj', (object,), {'name': 'Unknown'})).name if eq.equivalent_id in self.kg.courses else "Unknown",
                    "reason": "Direct equivalency",
                    "needs_approval": False
                })
        
        return subs
    
    def process(self, state: AdvisorState) -> AdvisorState:
        if state.get("query_type") == "substitution":
            messages = state.get("messages", [])
            if not messages:
                return {}
            last_msg = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])
            
            target_course = None
            for cid in self.kg.courses.keys():
                if cid.lower() in str(last_msg).lower():
                    target_course = cid
                    break
                    
            if target_course:
                subs = self.find_substitutions(target_course, state.get("student"))
                return {"retrieved_context": state.get("retrieved_context", "") + f"\nSubstitutions for {target_course}: {subs}"}
        return {}
