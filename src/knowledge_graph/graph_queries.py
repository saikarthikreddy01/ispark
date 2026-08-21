import networkx as nx
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.models.course import CreditCategory
from src.models.graph_schema import REL_REQUIRES, REL_COREQUISITE, REL_EQUIVALENT, REL_SATISFIES

def get_prerequisites(kg: AcademicKnowledgeGraph, course_id: str) -> list[str]:
    """Returns direct prerequisites for a course."""
    if not kg.graph.has_node(course_id):
        return []
    return [u for u, v, d in kg.graph.in_edges(course_id, data=True) if d.get('type') == REL_REQUIRES]

def get_all_prerequisites_recursive(kg: AcademicKnowledgeGraph, course_id: str) -> set[str]:
    """Returns all recursive prerequisites for a course."""
    if not kg.graph.has_node(course_id):
        return set()
    req_edges = [(u, v) for u, v, d in kg.graph.edges(data=True) if d.get('type') == REL_REQUIRES]
    sub_graph = kg.graph.edge_subgraph(req_edges)
    if not sub_graph.has_node(course_id):
        return set()
    return set(nx.ancestors(sub_graph, course_id))

def get_dependents(kg: AcademicKnowledgeGraph, course_id: str) -> list[str]:
    """Returns courses that require this course."""
    if not kg.graph.has_node(course_id):
        return []
    return [v for u, v, d in kg.graph.out_edges(course_id, data=True) if d.get('type') == REL_REQUIRES]

def get_available_courses(kg: AcademicKnowledgeGraph, completed: set[str]) -> list[str]:
    """Returns a list of course IDs whose prerequisites are fully satisfied."""
    from src.constraint_engine.prerequisite_checker import PrerequisiteChecker
    checker = PrerequisiteChecker(kg)
    available = []
    for course_id in kg.courses.keys():
        if course_id not in completed:
            satisfied, _ = checker.check_prerequisites(course_id, completed)
            if satisfied:
                available.append(course_id)
    return available

def get_bottleneck_courses(kg: AcademicKnowledgeGraph, top_n: int = 10) -> list[tuple[str, int]]:
    """Returns courses with the most dependents."""
    counts = []
    for course_id in kg.courses.keys():
        dependents = get_dependents(kg, course_id)
        counts.append((course_id, len(dependents)))
    counts.sort(key=lambda x: x[1], reverse=True)
    return counts[:top_n]

def get_prerequisite_chain_length(kg: AcademicKnowledgeGraph, course_id: str) -> int:
    """Gets the length of the longest prerequisite chain leading to this course."""
    if not kg.graph.has_node(course_id):
        return 0
    req_edges = [(u, v) for u, v, d in kg.graph.edges(data=True) if d.get('type') == REL_REQUIRES]
    sub_graph = kg.graph.edge_subgraph(req_edges)
    if not sub_graph.has_node(course_id):
        return 0
    
    longest_path_len = 0
    for node in sub_graph.nodes:
        if sub_graph.in_degree(node) == 0:
            paths = list(nx.all_simple_paths(sub_graph, source=node, target=course_id))
            for p in paths:
                if len(p) - 1 > longest_path_len:
                    longest_path_len = len(p) - 1
    return longest_path_len

def detect_circular_prerequisites(kg: AcademicKnowledgeGraph) -> list[list[str]]:
    """Detects any circular prerequisites (cycles)."""
    req_edges = [(u, v) for u, v, d in kg.graph.edges(data=True) if d.get('type') == REL_REQUIRES]
    sub_graph = kg.graph.edge_subgraph(req_edges)
    try:
        cycles = list(nx.simple_cycles(sub_graph))
        return cycles
    except nx.NetworkXNoCycle:
        return []

def get_courses_by_category(kg: AcademicKnowledgeGraph, category: CreditCategory) -> list[str]:
    """Returns course IDs satisfying a credit category."""
    cat_node_id = f"CAT_{category.value}"
    if not kg.graph.has_node(cat_node_id):
        return []
    return [u for u, v, d in kg.graph.in_edges(cat_node_id, data=True) if d.get('type') == REL_SATISFIES]

def get_equivalent_courses(kg: AcademicKnowledgeGraph, course_id: str) -> list[str]:
    """Returns equivalent course IDs."""
    if not kg.graph.has_node(course_id):
        return []
    return [v for u, v, d in kg.graph.out_edges(course_id, data=True) if d.get('type') == REL_EQUIVALENT]

def topological_sort_prerequisites(kg: AcademicKnowledgeGraph, target_courses: list[str]) -> list[str]:
    """Sorts target courses based on prerequisite order."""
    req_edges = [(u, v) for u, v, d in kg.graph.edges(data=True) if d.get('type') == REL_REQUIRES]
    sub_graph = kg.graph.edge_subgraph(req_edges).copy()
    
    nodes_to_keep = set(target_courses)
    for course in target_courses:
        nodes_to_keep.update(get_all_prerequisites_recursive(kg, course))
        
    sub_graph.remove_nodes_from([n for n in sub_graph if n not in nodes_to_keep])
    
    try:
        sorted_nodes = list(nx.topological_sort(sub_graph))
        return [n for n in sorted_nodes if n in target_courses]
    except nx.NetworkXUnfeasible:
        return target_courses

def get_course_difficulty_path(kg: AcademicKnowledgeGraph, course_id: str) -> list[str]:
    """Returns a path optimizing for lowest difficulty if available."""
    req_edges = [(u, v) for u, v, d in kg.graph.edges(data=True) if d.get('type') == REL_REQUIRES]
    sub_graph = kg.graph.edge_subgraph(req_edges)
    
    if not sub_graph.has_node(course_id):
        return [course_id]
        
    paths = []
    for node in sub_graph.nodes:
        if sub_graph.in_degree(node) == 0:
            if nx.has_path(sub_graph, node, course_id):
                paths.append(nx.shortest_path(sub_graph, node, course_id))
    
    if not paths:
        return [course_id]
        
    def path_difficulty(path):
        return sum(kg.get_course(n).difficulty_level for n in path if kg.get_course(n))
        
    return sorted(paths, key=path_difficulty)[0]
