from pyvis.network import Network
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.models.pathway import DegreePathway
from src.models.graph_schema import REL_REQUIRES

def create_prerequisite_graph(kg: AcademicKnowledgeGraph, course_id: str = None, highlight_courses: set[str] = None) -> str:
    """Creates a pyvis HTML visualization of the prerequisite graph."""
    net = Network(height='750px', width='100%', directed=True, bgcolor='#222222', font_color='white')
    net.force_atlas_2based()
    
    nodes_to_add = set()
    edges_to_add = set()
    
    if course_id:
        from src.knowledge_graph.graph_queries import get_all_prerequisites_recursive
        nodes_to_add.add(course_id)
        nodes_to_add.update(get_all_prerequisites_recursive(kg, course_id))
        
        for u, v, d in kg.graph.edges(data=True):
            if d.get('type') == REL_REQUIRES and u in nodes_to_add and v in nodes_to_add:
                edges_to_add.add((u, v, d.get('logic_type', 'AND')))
    else:
        for u, v, d in kg.graph.edges(data=True):
            if d.get('type') == REL_REQUIRES:
                nodes_to_add.add(u)
                nodes_to_add.add(v)
                edges_to_add.add((u, v, d.get('logic_type', 'AND')))
                
    highlight_courses = highlight_courses or set()
    
    for n in nodes_to_add:
        course = kg.get_course(n)
        if not course:
            continue
        
        size = 10 + (course.credits * 2)
        color = '#ff9999' if n in highlight_courses else '#97c2fc'
        if course_id and n == course_id:
            color = '#ff3333'
            
        title = f"{course.id}: {course.name}\nCredits: {course.credits}\nDept: {course.department}"
        net.add_node(n, label=n, title=title, size=size, color=color, group=course.department)
        
    for u, v, logic in edges_to_add:
        net.add_edge(u, v, title=logic, label=logic if logic != 'AND' else '', color='#aaaaaa')
        
    return net.generate_html()

def create_student_progress_graph(kg: AcademicKnowledgeGraph, completed: set[str], planned: set[str] = None) -> str:
    """Visualizes student progress on the full graph."""
    planned = planned or set()
    
    net = Network(height='750px', width='100%', directed=True, bgcolor='#222222', font_color='white')
    net.force_atlas_2based()
    
    from src.knowledge_graph.graph_queries import get_available_courses, get_bottleneck_courses
    available = set(get_available_courses(kg, completed))
    bottlenecks = set([c for c, _ in get_bottleneck_courses(kg, 5)])
    
    for course_id, course in kg.courses.items():
        if course_id in completed:
            color = '#00ff00' 
        elif course_id in planned:
            color = '#ffa500' 
        elif course_id in available:
            color = '#0000ff' 
        else:
            color = '#808080' 
            
        border = '#ff0000' if course_id in bottlenecks else 'transparent'
        size = 15
        
        net.add_node(
            course_id, 
            label=course_id, 
            title=course.name, 
            color={'background': color, 'border': border},
            borderWidth=2 if border != 'transparent' else 0,
            size=size
        )
        
    for u, v, d in kg.graph.edges(data=True):
        if d.get('type') == REL_REQUIRES:
            net.add_edge(u, v, color='#aaaaaa')
            
    return net.generate_html()

def create_pathway_timeline(pathway: DegreePathway, kg: AcademicKnowledgeGraph) -> str:
    """Creates a hierarchical layout showing semester-by-semester progression."""
    net = Network(height='750px', width='100%', directed=True, layout=True, bgcolor='#222222', font_color='white')
    net.set_options("""
    var options = {
      "layout": {
        "hierarchical": {
          "enabled": true,
          "direction": "LR",
          "sortMethod": "directed",
          "levelSeparation": 150
        }
      }
    }
    """)
    
    for idx, plan in enumerate(pathway.semester_plans):
        semester_label = f"{plan.semester.value} {plan.year}"
        level = idx
        
        for course_id in plan.courses:
            course = kg.get_course(course_id)
            title = course.name if course else course_id
            
            has_conflict = any(c.course_id == course_id for c in pathway.conflicts)
            color = '#ff4444' if has_conflict else '#44ff44'
            
            net.add_node(course_id, label=course_id, title=title, level=level, color=color)
            
            for p_idx in range(idx):
                for p_course in pathway.semester_plans[p_idx].courses:
                    for u, v, d in kg.graph.edges(data=True):
                        if d.get('type') == REL_REQUIRES and u == p_course and v == course_id:
                            net.add_edge(u, v)
                            
    return net.generate_html()
