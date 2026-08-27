"""Focused regression tests for the academic-integrity fixes."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build_kg():
    from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
    kg = AcademicKnowledgeGraph()
    kg.load_from_json(
        str(ROOT / "data" / "courses.json"),
        str(ROOT / "data" / "degree_requirements.json"),
        str(ROOT / "data" / "equivalencies.json"),
    )
    return kg


def test_legacy_prerequisite_groups_are_non_blocking_knowledge():
    from src.constraint_engine.prerequisite_checker import PrerequisiteChecker
    kg = build_kg()
    checker = PrerequisiteChecker(kg)

    # 24CS302 currently carries the curriculum-derived Probability background
    # in the legacy prerequisite_groups field. It must warn, not block.
    formal_ok, formal_missing = checker.check_prerequisites("24CS302", set())
    ready, knowledge_missing = checker.check_knowledge_requirements("24CS302", set())

    assert formal_ok is True
    assert formal_missing == []
    assert ready is False
    assert "22ST202" in knowledge_missing


def test_deep_learning_is_not_mandatory_base_degree_course():
    kg = build_kg()
    required = set(kg.degree_requirements.get("required_courses", []))
    assert "22CS804" not in required
    assert kg.degree_requirements["optional_tracks"]["HONOURS_MINORS"]["required_for_base_degree"] is False


def test_digital_logic_semester_mapping_corrected():
    import json
    data = json.loads((ROOT / "data" / "degree_requirements.json").read_text(encoding="utf-8"))
    sem3 = next(s for s in data["semesters_structure"] if s["semester_index"] == 3)
    sem4 = next(s for s in data["semesters_structure"] if s["semester_index"] == 4)
    assert "24CS208" not in sem3["courses"]
    assert "24CS208" in sem4["courses"]


def test_unsourced_equivalencies_require_review():
    kg = build_kg()
    assert kg.equivalencies
    for eq in kg.equivalencies:
        assert eq.status != "APPROVED"
        assert eq.requires_faculty_approval is True


def test_total_credit_target_is_not_enforced_as_verified():
    from src.constraint_engine.credit_validator import CreditValidator
    kg = build_kg()
    validator = CreditValidator(kg)
    total, status = validator._official_total()
    assert total is None
    assert status == "UNVERIFIED"


def test_graph_exposes_knowledge_relationship_separately():
    from src.knowledge_graph.graph_queries import get_prerequisites, get_prerequisite_knowledge
    kg = build_kg()
    assert get_prerequisites(kg, "24CS302") == []
    assert "22ST202" in get_prerequisite_knowledge(kg, "24CS302")


def test_course_name_entity_resolution_for_machine_learning():
    from src.rag.vector_store import AcademicVectorStore
    from src.rag.graph_retriever import GraphRAGRetriever
    kg = build_kg()
    retriever = GraphRAGRetriever(kg, AcademicVectorStore())
    refs = retriever._extract_course_references("Can I take Machine Learning next semester?")
    assert "24CS306" in refs
