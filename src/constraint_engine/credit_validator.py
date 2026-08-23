from dataclasses import dataclass
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.models.pathway import DegreePathway, PathwayConstraint
from src.models.course import CreditCategory

@dataclass
class CreditSummary:
    total_completed: int = 0
    total_in_progress: int = 0
    total_required: int = 160
    remaining: int = 160

class CreditValidator:
    def __init__(self, kg: AcademicKnowledgeGraph):
        self.kg = kg
        self.degree_req = kg.degree_requirements
    
    def calculate_student_credits(self, student) -> CreditSummary:
        """
        Calculates total completed and in-progress credits for a student.
        """
        completed = student.completed_course_ids if hasattr(student, 'completed_course_ids') else set(student.completed_courses if hasattr(student, 'completed_courses') else [])
        planned = getattr(student, 'planned_courses', [])
        
        total_completed = sum(self.kg.get_course_credits(c) for c in completed)
        total_in_prog = 0
        for p in planned:
            cid = p if isinstance(p, str) else p.get("course_id", "") if isinstance(p, dict) else getattr(p, "course_id", "")
            total_in_prog += self.kg.get_course_credits(cid)
            
        total_req = self.degree_req.get('total_credits', 160)
        return CreditSummary(
            total_completed=total_completed,
            total_in_progress=total_in_prog,
            total_required=total_req,
            remaining=max(0, total_req - total_completed)
        )

    def is_overload_semester(self, credit_count: int, student=None) -> bool:
        """
        Checks if credit load exceeds the policy maximum limit (usually 21 or 24 credits).
        """
        limit = 24
        if student and hasattr(student, 'max_credits_per_semester'):
            limit = max(student.max_credits_per_semester, 21)
        return credit_count > limit

    def get_remaining_requirements(self, completed_ids: set[str]) -> dict:
        """
        Calculates required, earned, and remaining credits per category.
        """
        result = {}
        required_credits = self.degree_req.get('categories', {})
        
        earned_credits = {cat: 0 for cat in CreditCategory}
        for c_id in completed_ids:
            course = self.kg.get_course(c_id)
            if course:
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
        total_required = self.degree_req.get('total_credits', 160)
        
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
