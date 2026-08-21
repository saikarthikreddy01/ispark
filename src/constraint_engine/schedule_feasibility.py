from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.knowledge_graph.graph_queries import get_bottleneck_courses, topological_sort_prerequisites
from src.models.course import Semester
from src.models.student import StudentProfile
from src.models.pathway import SemesterPlan
from src.constraint_engine.prerequisite_checker import PrerequisiteChecker

class ScheduleAnalyzer:
    def __init__(self, kg: AcademicKnowledgeGraph):
        self.kg = kg
        self.prereq_checker = PrerequisiteChecker(kg)
    
    def check_course_availability(self, course_id: str, semester: Semester) -> bool:
        """Checks if a course is offered in the given semester."""
        course = self.kg.get_course(course_id)
        if not course:
            return False
        return semester in course.offered_semesters
    
    def analyze_graduation_feasibility(self, student: StudentProfile) -> dict:
        """
        Analyzes the feasibility of graduation for a student.
        """
        completed = student.completed_course_ids if hasattr(student, 'completed_course_ids') else set(c.course_id for c in student.completed_courses)
        
        # Determine remaining requirements (mocked for simplicity)
        reqs = self.kg.degree_requirements.get('required_courses', [])
        remaining_courses = [r for r in reqs if r not in completed]
        
        bottlenecks = [b for b, count in get_bottleneck_courses(self.kg) if b in remaining_courses]
        critical_path = self.identify_critical_path(remaining_courses)
        semesters_remaining = len(critical_path) # Absolute minimum semesters
        
        total_req = self.kg.degree_requirements.get('total_credits', 120)
        total_earned = sum(self.kg.get_course_credits(c) for c in completed)
        remaining_credits = max(0, total_req - total_earned)
        
        # Simple heuristic risk score
        risk_score = min(1.0, (len(bottlenecks) * 0.1) + (semesters_remaining * 0.05))
        
        return {
            "can_graduate_on_time": semesters_remaining <= 8, # Assuming 4-year standard
            "earliest_graduation_semesters": semesters_remaining,
            "remaining_credits": remaining_credits,
            "semesters_remaining": semesters_remaining,
            "bottleneck_courses": bottlenecks,
            "risk_factors": [f"Missing {len(remaining_courses)} required courses"],
            "risk_score": risk_score
        }
    
    def suggest_semester_load(self, student: StudentProfile, target_graduation: str = None) -> list[SemesterPlan]:
        """
        Generates a balanced set of semester plans for remaining courses.
        """
        completed = student.completed_course_ids if hasattr(student, 'completed_course_ids') else set(c.course_id for c in student.completed_courses)
        reqs = self.kg.degree_requirements.get('required_courses', [])
        remaining_courses = [r for r in reqs if r not in completed]
        
        ordered_remaining = topological_sort_prerequisites(self.kg, remaining_courses)
        
        plans = []
        current_semester_val = student.current_semester
        current_year = student.current_year
        
        def next_semester(sem, year):
            if sem == Semester.FALL: return Semester.SPRING, year + 1
            if sem == Semester.SPRING: return Semester.SUMMER, year
            return Semester.FALL, year
            
        current_completed = set(completed)
        idx = 0
        
        while idx < len(ordered_remaining):
            plan_courses = []
            credits = 0
            
            # Simple greedy packing
            temp_idx = idx
            while temp_idx < len(ordered_remaining) and credits < student.max_credits_per_semester:
                course_id = ordered_remaining[temp_idx]
                c = self.kg.get_course(course_id)
                
                # Check prereqs against current_completed
                satisfied, _ = self.prereq_checker.check_prerequisites(course_id, current_completed)
                
                if satisfied and self.check_course_availability(course_id, current_semester_val):
                    if credits + c.credits <= student.max_credits_per_semester:
                        plan_courses.append(course_id)
                        credits += c.credits
                        ordered_remaining.pop(temp_idx)
                    else:
                        temp_idx += 1
                else:
                    temp_idx += 1
                    
            plans.append(SemesterPlan(
                semester=current_semester_val,
                year=current_year,
                courses=plan_courses,
                total_credits=credits
            ))
            
            current_completed.update(plan_courses)
            current_semester_val, current_year = next_semester(current_semester_val, current_year)
            
            if not plan_courses:
                # Break to avoid infinite loop if no courses can be scheduled
                break
                
        return plans
    
    def identify_critical_path(self, remaining_courses: list[str]) -> list[str]:
        """
        Identifies the longest prerequisite chain among remaining courses.
        """
        from src.knowledge_graph.graph_queries import get_prerequisite_chain_length
        if not remaining_courses:
            return []
            
        chains = [(c, get_prerequisite_chain_length(self.kg, c)) for c in remaining_courses]
        chains.sort(key=lambda x: x[1], reverse=True)
        
        # Simplified: just returns a list representing the maximum depth required
        # For actual path, would need to trace ancestors
        longest_target = chains[0][0]
        
        import networkx as nx
        from src.models.graph_schema import REL_REQUIRES
        req_edges = [(u, v) for u, v, d in self.kg.graph.edges(data=True) if d.get('type') == REL_REQUIRES]
        sub_graph = self.kg.graph.edge_subgraph(req_edges)
        
        if not sub_graph.has_node(longest_target):
            return [longest_target]
            
        longest_path = [longest_target]
        for node in sub_graph.nodes:
            if sub_graph.in_degree(node) == 0:
                paths = list(nx.all_simple_paths(sub_graph, source=node, target=longest_target))
                for p in paths:
                    if len(p) > len(longest_path):
                        longest_path = p
                        
        return longest_path
