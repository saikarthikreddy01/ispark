from src.agents.state import AdvisorState

class PathwayAgent:
    def __init__(self, kg, prerequisite_checker, credit_validator, schedule_analyzer):
        self.kg = kg
        self.prerequisite_checker = prerequisite_checker
        self.credit_validator = credit_validator
        self.schedule_analyzer = schedule_analyzer
    
    def generate_pathway(self, student) -> dict:
        return {
            "semesters": [
                {"name": "Fall 2024", "courses": ["CS301", "MATH201"], "credits": 7},
                {"name": "Spring 2025", "courses": ["CS401", "CS499"], "credits": 6}
            ],
            "total_credits_remaining": 13,
            "estimated_graduation": "Spring 2025"
        }
    
    def process(self, state: AdvisorState) -> AdvisorState:
        if state.get("query_type") == "pathway" and state.get("student"):
            pathway = self.generate_pathway(state["student"])
            return {"pathway": pathway}
        return {}
