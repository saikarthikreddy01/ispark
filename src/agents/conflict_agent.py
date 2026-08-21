from src.agents.state import AdvisorState

class ConflictAgent:
    def __init__(self, kg, prerequisite_checker, credit_validator):
        self.kg = kg
        self.prerequisite_checker = prerequisite_checker
        self.credit_validator = credit_validator
    
    def detect_conflicts(self, course_ids: list[str], student, semester=None) -> list[dict]:
        conflicts = []
        completed = set(student.get("completed_course_ids", [])) if isinstance(student, dict) else getattr(student, "completed_course_ids", set())
        
        for cid in course_ids:
            if cid in completed:
                conflicts.append({
                    "type": "ALREADY_COMPLETED",
                    "course": cid,
                    "message": f"{cid} is already completed."
                })
            else:
                ok, missing = self.prerequisite_checker.check_prerequisites(cid, completed)
                if not ok:
                    conflicts.append({
                        "type": "MISSING_PREREQUISITE",
                        "course": cid,
                        "message": f"Missing prerequisites for {cid}: {', '.join(missing)}"
                    })
        return conflicts
    
    def process(self, state: AdvisorState) -> AdvisorState:
        messages = state.get("messages", [])
        if not messages:
            return {}
            
        last_msg = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])
        
        course_ids = []
        for cid in self.kg.courses.keys():
            if cid.lower() in str(last_msg).lower():
                course_ids.append(cid)
                
        if course_ids and state.get("student"):
            conflicts = self.detect_conflicts(course_ids, state["student"])
            return {"conflicts": conflicts}
            
        return {}
