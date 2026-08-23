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
        completed_grades = self._extract_grades(student)
        completed_ids = set(completed_grades.keys())
        
        # Determine remaining requirements
        reqs = self.kg.degree_requirements.get('required_courses', [])
        remaining_courses = [r for r in reqs if r not in completed_ids]
        
        # Category tracking (Degree Audit)
        category_reqs = self.kg.degree_requirements.get('categories', {})
        earned_categories = {}
        for c_id in completed_ids:
            c = self.kg.get_course(c_id)
            if c:
                for cat in c.credit_categories:
                    earned_categories[cat.value] = earned_categories.get(cat.value, 0) + c.credits
                    
        category_deficits = {}
        for cat, req_creds in category_reqs.items():
            earned = earned_categories.get(cat, 0)
            if earned < req_creds:
                category_deficits[cat] = req_creds - earned
        
        bottlenecks = [b for b, count in get_bottleneck_courses(self.kg) if b in remaining_courses]
        critical_path = self.identify_critical_path(remaining_courses)
        semesters_remaining = len(critical_path) # Absolute minimum semesters
        
        total_req = self.kg.degree_requirements.get('total_credits', 120)
        total_earned = sum(self.kg.get_course_credits(c) for c in completed_ids)
        remaining_credits = max(0, total_req - total_earned)
        
        # Simple heuristic risk score
        risk_score = min(1.0, (len(bottlenecks) * 0.1) + (semesters_remaining * 0.05))
        
        return {
            "can_graduate_on_time": semesters_remaining <= 8, # Assuming 4-year standard
            "earliest_graduation_semesters": semesters_remaining,
            "remaining_credits": remaining_credits,
            "semesters_remaining": semesters_remaining,
            "bottleneck_courses": bottlenecks,
            "category_deficits": category_deficits,
            "risk_factors": [f"Missing {len(remaining_courses)} required courses"],
            "risk_score": risk_score
        }
        
    def _extract_grades(self, student: StudentProfile) -> dict[str, str]:
        """Extracts a mapping of course_id to grade from a student profile."""
        grades = {}
        for c in student.completed_courses:
            if hasattr(c, 'course_id') and hasattr(c, 'grade'):
                grades[c.course_id] = c.grade
            elif isinstance(c, dict) and 'course_id' in c and 'grade' in c:
                grades[c['course_id']] = c['grade']
            elif isinstance(c, str):
                grades[c] = "A" # Mock passing grade for simple string IDs
        return grades
    
    def suggest_semester_load(self, student: StudentProfile, target_graduation: str = None, max_difficulty_score: int = 14) -> list[SemesterPlan]:
        """
        Generates a balanced set of semester plans for remaining courses.
        Includes a max_difficulty_score to prevent burnout.
        """
        completed_grades = self._extract_grades(student)
        completed_ids = set(completed_grades.keys())
        reqs = self.kg.degree_requirements.get('required_courses', [])
        remaining_courses = [r for r in reqs if r not in completed_ids]
        
        ordered_remaining = topological_sort_prerequisites(self.kg, remaining_courses)
        
        plans = []
        current_semester_val = student.current_semester
        current_year = student.current_year
        
        def next_semester(sem, year):
            if sem == Semester.FALL: return Semester.SPRING, year + 1
            if sem == Semester.SPRING: return Semester.SUMMER, year
            return Semester.FALL, year
            
        current_grades = dict(completed_grades)
        idx = 0
        
        while idx < len(ordered_remaining):
            plan_courses = []
            credits = 0
            semester_difficulty = 0
            
            # Simple greedy packing
            temp_idx = idx
            while temp_idx < len(ordered_remaining) and credits < student.max_credits_per_semester:
                course_id = ordered_remaining[temp_idx]
                c = self.kg.get_course(course_id)
                
                # Check prereqs against current_grades
                satisfied, _ = self.prereq_checker.check_prerequisites(course_id, current_grades)
                
                if satisfied and self.check_course_availability(course_id, current_semester_val):
                    # Check both credits limit and difficulty score limit
                    if (credits + c.credits <= student.max_credits_per_semester) and (semester_difficulty + c.difficulty_level <= max_difficulty_score):
                        plan_courses.append(course_id)
                        credits += c.credits
                        semester_difficulty += c.difficulty_level
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
            
            # Simulate earning an 'A' in the planned courses for future semesters
            for c_id in plan_courses:
                current_grades[c_id] = "A"
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
