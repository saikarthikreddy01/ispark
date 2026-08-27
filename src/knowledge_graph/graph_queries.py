import networkx as nx
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.models.course import CreditCategory
from src.models.graph_schema import (
    REL_REQUIRES, REL_KNOWLEDGE, REL_COREQUISITE, REL_EQUIVALENT, REL_SATISFIES
)


def _relationship_subgraph(kg: AcademicKnowledgeGraph, relationship_type: str) -> nx.DiGraph:
    g = nx.DiGraph()
    for u, v, data in kg.graph.edges(data=True):
        if data.get("type") == relationship_type:
            g.add_edge(u, v, **data)
    return g


def get_prerequisites(kg: AcademicKnowledgeGraph, course_id: str) -> list[str]:
    """Return direct FORMAL registration prerequisites only."""
    if not kg.graph.has_node(course_id):
        return []
    return [u for u, _, d in kg.graph.in_edges(course_id, data=True) if d.get("type") == REL_REQUIRES]


def get_prerequisite_knowledge(kg: AcademicKnowledgeGraph, course_id: str) -> list[str]:
    """Return direct non-blocking prerequisite-knowledge dependencies."""
    if not kg.graph.has_node(course_id):
        return []
    return [u for u, _, d in kg.graph.in_edges(course_id, data=True) if d.get("type") == REL_KNOWLEDGE]


def get_all_prerequisites_recursive(kg: AcademicKnowledgeGraph, course_id: str) -> set[str]:
    g = _relationship_subgraph(kg, REL_REQUIRES)
    return set(nx.ancestors(g, course_id)) if g.has_node(course_id) else set()


def get_all_knowledge_dependencies_recursive(kg: AcademicKnowledgeGraph, course_id: str) -> set[str]:
    g = _relationship_subgraph(kg, REL_KNOWLEDGE)
    return set(nx.ancestors(g, course_id)) if g.has_node(course_id) else set()


def get_dependents(kg: AcademicKnowledgeGraph, course_id: str, include_knowledge: bool = False) -> list[str]:
    if not kg.graph.has_node(course_id):
        return []
    allowed = {REL_REQUIRES}
    if include_knowledge:
        allowed.add(REL_KNOWLEDGE)
    return [v for _, v, d in kg.graph.out_edges(course_id, data=True) if d.get("type") in allowed]


def get_available_courses(kg: AcademicKnowledgeGraph, completed: set[str]) -> list[str]:
    """Return courses that are not blocked by authoritative formal prerequisites."""
    from src.constraint_engine.prerequisite_checker import PrerequisiteChecker
    checker = PrerequisiteChecker(kg)
    available = []
    for course_id in kg.courses:
        if course_id not in completed:
            satisfied, _ = checker.check_prerequisites(course_id, completed)
            if satisfied:
                available.append(course_id)
    return available


def get_bottleneck_courses(kg: AcademicKnowledgeGraph, top_n: int = 10) -> list[tuple[str, int]]:
    """Rank courses by downstream impact across formal + knowledge dependency graphs.

    Formal downstream dependencies carry more weight because they can block
    registration. Knowledge dependencies still matter for academic readiness.
    """
    formal = _relationship_subgraph(kg, REL_REQUIRES)
    knowledge = _relationship_subgraph(kg, REL_KNOWLEDGE)
    scored = []
    for course_id in kg.courses:
        formal_downstream = len(nx.descendants(formal, course_id)) if formal.has_node(course_id) else 0
        knowledge_downstream = len(nx.descendants(knowledge, course_id)) if knowledge.has_node(course_id) else 0
        direct = len(get_dependents(kg, course_id, include_knowledge=True))
        score = (formal_downstream * 3) + knowledge_downstream + direct
        scored.append((course_id, score))
    return sorted(scored, key=lambda item: item[1], reverse=True)[:top_n]


def get_prerequisite_chain_length(kg: AcademicKnowledgeGraph, course_id: str) -> int:
    g = _relationship_subgraph(kg, REL_REQUIRES)
    if not g.has_node(course_id) or not nx.is_directed_acyclic_graph(g):
        return 0
    lengths = {node: 0 for node in nx.topological_sort(g)}
    for node in nx.topological_sort(g):
        for succ in g.successors(node):
            lengths[succ] = max(lengths.get(succ, 0), lengths[node] + 1)
    return lengths.get(course_id, 0)


def detect_circular_prerequisites(kg: AcademicKnowledgeGraph) -> list[list[str]]:
    g = _relationship_subgraph(kg, REL_REQUIRES)
    return list(nx.simple_cycles(g))


def get_courses_by_category(kg: AcademicKnowledgeGraph, category: CreditCategory) -> list[str]:
    cat_node_id = f"CAT_{category.value}"
    if not kg.graph.has_node(cat_node_id):
        return []
    return [u for u, _, d in kg.graph.in_edges(cat_node_id, data=True) if d.get("type") == REL_SATISFIES]


def get_equivalent_courses(kg: AcademicKnowledgeGraph, course_id: str, approved_only: bool = False) -> list[str]:
    if not kg.graph.has_node(course_id):
        return []
    results = []
    for _, v, data in kg.graph.out_edges(course_id, data=True):
        if data.get("type") != REL_EQUIVALENT:
            continue
        if approved_only and data.get("status") != "APPROVED":
            continue
        results.append(v)
    return results


def topological_sort_prerequisites(kg: AcademicKnowledgeGraph, target_courses: list[str]) -> list[str]:
    """Topologically order targets using formal prerequisites only."""
    g = _relationship_subgraph(kg, REL_REQUIRES)
    nodes_to_keep = set(target_courses)
    for course in target_courses:
        if g.has_node(course):
            nodes_to_keep.update(nx.ancestors(g, course))
    sub = g.subgraph(nodes_to_keep).copy()
    if not sub.nodes:
        return list(target_courses)
    try:
        ordered = list(nx.topological_sort(sub))
    except nx.NetworkXUnfeasible:
        return list(target_courses)
    rank = {cid: idx for idx, cid in enumerate(ordered)}
    return sorted(target_courses, key=lambda cid: rank.get(cid, len(rank)))


def get_course_difficulty_path(kg: AcademicKnowledgeGraph, course_id: str) -> list[str]:
    g = _relationship_subgraph(kg, REL_REQUIRES)
    if not g.has_node(course_id):
        return [course_id]
    candidates = []
    for node in g.nodes:
        if g.in_degree(node) == 0 and nx.has_path(g, node, course_id):
            candidates.append(nx.shortest_path(g, node, course_id))
    if not candidates:
        return [course_id]

    def difficulty(path):
        return sum(kg.get_course(n).difficulty_level for n in path if kg.get_course(n))

    return min(candidates, key=difficulty)
