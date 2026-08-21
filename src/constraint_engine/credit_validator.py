from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.models.pathway import DegreePathway, PathwayConstraint
from src.models.course import CreditCategory

class CreditValidator:
    def __init__(self, kg: AcademicKnowledgeGraph):
        self.kg = kg
        self.degree_req = kg.degree_requirements
    
    def get_remaining_requirements(self, completed_ids: set[str]) -> dict:
        """
        Calculates required, earned, and remaining credits per category.
        """
        result = {}
        # Assume self.degree_req has a 'categories' dict mapping category enum to required credits
        required_credits = self.degree_req.get('categories', {})
        
        earned_credits = {cat: 0 for cat in CreditCategory}
        for c_id in completed_ids:
            course = self.kg.get_course(c_id)
            if course:
                # Simple logic: distribute credits among its categories, or just primary one
                # Here we just assign full credits to all listed categories for simplicity
                for cat in course.credit_categories:
                    earned_credits[cat] += course.credits
                    
        for cat in CreditCategory:
            req = required_credits.get(cat.name, 0)
            earned = earned_credits.get(cat, 0)
            result[cat.name] = {
                'required': req,
                'earned': earned,
                'remaining': max(0, req - earned)
            }
            
        return result
    
    def validate_credits(self, completed_ids: set[str], planned_pathway: DegreePathway = None) -> list[PathwayConstraint]:
        """
        Validates total credits and categorical requirements against degree requirements.
        """
        constraints = []
        total_required = self.degree_req.get('total_credits', 120)
        
        all_ids = set(completed_ids)
        if planned_pathway:
            for plan in planned_pathway.semester_plans:
                all_ids.update(plan.courses)
                
        total_earned = sum(self.kg.get_course_credits(c) for c in all_ids)
        
        constraints.append(PathwayConstraint(
            name="Total Credits",
            description=f"Require {total_required} total credits.",
            is_satisfied=(total_earned >= total_required),
            details=f"Current: {total_earned}/{total_required}"
        ))
        
        remaining = self.get_remaining_requirements(all_ids)
        for cat, reqs in remaining.items():
            if reqs['required'] > 0:
                constraints.append(PathwayConstraint(
                    name=f"{cat} Credits",
                    description=f"Require {reqs['required']} credits in {cat}.",
                    is_satisfied=(reqs['remaining'] == 0),
                    details=f"Earned: {reqs['earned']}/{reqs['required']}"
                ))
                
        return constraints
    
    def check_semester_overload(self, course_ids: list[str], max_credits: int = 18) -> PathwayConstraint:
        """
        Checks if a specific semester exceeds the max credit load.
        """
        total = sum(self.kg.get_course_credits(c) for c in course_ids)
        return PathwayConstraint(
            name="Semester Credit Load",
            description=f"Maximum {max_credits} credits per semester.",
            is_satisfied=(total <= max_credits),
            details=f"Planned: {total}"
        )
