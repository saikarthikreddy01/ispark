from src.agents.state import AdvisorState

class RiskAgent:
    def __init__(self, kg, schedule_analyzer, credit_validator):
        self.kg = kg
        self.schedule_analyzer = schedule_analyzer
        self.credit_validator = credit_validator
    
    def assess_risk(self, student) -> dict:
        completed_credits = sum(c.credits for c in student.get("completed_courses", [])) if isinstance(student, dict) else sum(c.credits for c in getattr(student, "completed_courses", []))
        
        risk_level = "Low"
        factors = []
        
        if completed_credits < 30:
            factors.append("Early in degree, standard risk.")
        elif completed_credits > 90:
            factors.append("Approaching graduation, monitor remaining requirements closely.")
            
        return {
            "level": risk_level,
            "factors": factors
        }
    
    def process(self, state: AdvisorState) -> AdvisorState:
        if state.get("query_type") == "risk" and state.get("student"):
            risk_assessment = self.assess_risk(state["student"])
            return {"risk_assessment": risk_assessment}
        return {}
