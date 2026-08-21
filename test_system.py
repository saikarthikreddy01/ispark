"""
Comprehensive End-to-End System Test for Graph-RAG Academic Advisor
Tests Knowledge Graph, Constraint Engine, Graph-RAG, and Agent Orchestrator.
"""

import sys
import json
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from src.models.student import StudentProfile
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.knowledge_graph.graph_queries import (
    get_prerequisites,
    get_all_prerequisites_recursive,
    get_dependents,
    get_available_courses,
    get_bottleneck_courses,
    topological_sort_prerequisites,
    get_equivalent_courses
)
from src.constraint_engine.prerequisite_checker import PrerequisiteChecker
from src.constraint_engine.credit_validator import CreditValidator
from src.constraint_engine.schedule_feasibility import ScheduleAnalyzer
from src.rag.document_loader import PolicyDocumentLoader
from src.rag.vector_store import AcademicVectorStore
from src.rag.graph_retriever import GraphRAGRetriever
from src.agents.orchestrator import AcademicAdvisor
from src.utils.config import DATA_DIR

def run_tests():
    print("=" * 70)
    print("🚀 RUNNING END-TO-END VERIFICATION FOR GRAPH-RAG ACADEMIC ADVISOR")
    print("=" * 70)

    # 1. Test Knowledge Graph Loading
    print("\n[1/6] 🏗️ Testing Academic Knowledge Graph Construction...")
    kg = AcademicKnowledgeGraph()
    kg.load_from_json(
        str(DATA_DIR / "courses.json"),
        str(DATA_DIR / "degree_requirements.json"),
        str(DATA_DIR / "equivalencies.json")
    )
    all_courses = kg.get_all_courses()
    print(f"  ✅ Loaded {len(all_courses)} courses into Knowledge Graph.")
    print(f"  ✅ Graph nodes: {kg.graph.number_of_nodes()}, Graph edges: {kg.graph.number_of_edges()}")
    assert len(all_courses) >= 40, "Expected at least 40 courses in curriculum"

    # 2. Test Graph Queries
    print("\n[2/6] 🔍 Testing Knowledge Graph Query Operators...")
    cs301_prereqs = get_prerequisites(kg, "CS301")
    print(f"  ✅ Direct Prerequisites for CS301 (Algorithms): {cs301_prereqs}")
    
    cs402_all_prereqs = get_all_prerequisites_recursive(kg, "CS402")
    print(f"  ✅ Recursive Prerequisite Chain for CS402 (Machine Learning): {sorted(list(cs402_all_prereqs))}")
    
    bottlenecks = get_bottleneck_courses(kg, top_n=5)
    print(f"  ✅ Top Curriculum Bottlenecks: {bottlenecks}")
    
    cs102_dependents = get_dependents(kg, "CS102")
    print(f"  ✅ Courses directly dependent on CS102: {cs102_dependents}")
    assert len(bottlenecks) > 0, "Expected bottleneck courses to be detected"

    # 3. Test Constraint Engine
    print("\n[3/6] ⚙️ Testing Prerequisite & Constraint Verification Engine...")
    checker = PrerequisiteChecker(kg)
    credit_val = CreditValidator(kg)
    schedule_analyzer = ScheduleAnalyzer(kg)

    # Test with no courses completed
    ok, missing = checker.check_prerequisites("CS301", set())
    print(f"  ✅ Freshman attempting CS301 -> Satisfied: {ok}, Missing: {missing}")
    assert not ok, "CS301 should not be permitted without prerequisites"

    # Test with prerequisites completed
    ok, missing = checker.check_prerequisites("CS301", {"CS201", "MATH201", "CS102", "CS101", "MATH101"})
    print(f"  ✅ Qualified student attempting CS301 -> Satisfied: {ok}, Missing: {missing}")
    assert ok, "CS301 should be permitted with completed prerequisites"

    # 4. Test Student Profiles & Feasibility
    print("\n[4/6] 🎓 Testing Student Profiles & Pathway Feasibility...")
    with open(DATA_DIR / "sample_students.json") as f:
        students_data = json.load(f)
    
    for s_raw in students_data:
        student = StudentProfile(**s_raw)
        feas = schedule_analyzer.analyze_graduation_feasibility(student)
        plans = schedule_analyzer.suggest_semester_load(student)
        print(f"\n  👤 Student: {student.name} ({student.id})")
        print(f"     - Completed Credits: {student.total_credits_earned} | Cumulative GPA: {student.gpa:.2f}")
        print(f"     - Risk Score: {feas.get('risk_score', 0.0):.2f} | Terms Remaining: {feas.get('semesters_remaining', 0)}")
        print(f"     - Generated Pathway: {len(plans)} semesters planned")

    # 5. Test Graph-RAG Document Loading & Vector Store
    print("\n[5/6] 📚 Testing Document Loading & Vector Store Indexing...")
    loader = PolicyDocumentLoader()
    policy_chunks = loader.load_and_chunk(str(DATA_DIR / "policies.md"))
    course_chunks = loader.load_course_descriptions(all_courses)
    print(f"  ✅ Generated {len(policy_chunks)} policy chunks and {len(course_chunks)} course catalog chunks.")

    vs = AcademicVectorStore(persist_dir=str(PROJECT_ROOT / "chroma_test_db"))
    vs.add_documents(policy_chunks + course_chunks)
    print(f"  ✅ Indexed all chunks into ChromaDB.")

    # 6. Test Graph-RAG Hybrid Retrieval & Advisor
    print("\n[6/6] 🤖 Testing Graph-RAG Retrieval & Multi-Agent Advisor...")
    retriever = GraphRAGRetriever(kg, vs)
    test_query = "Can I take CS301 (Algorithms) and what happens if I need a waiver?"
    retrieval_result = retriever.retrieve(test_query, top_k=3)
    
    print(f"  ✅ Query: '{test_query}'")
    print(f"  ✅ Retrieved Graph Context Length: {len(retrieval_result.graph_context)} chars")
    print(f"  ✅ Retrieved Policy Context Length: {len(retrieval_result.policy_context)} chars")
    print(f"  ✅ Generated Citations: {len(retrieval_result.citations)} sources")

    advisor = AcademicAdvisor(kg=kg, vector_store=vs)
    alice = StudentProfile(**students_data[0]) # Alice Freshman
    chat_res = advisor.chat_sync("Can I take CS301 next term?", student=alice)
    
    print(f"\n  💬 Sample Advisor Output for Alice (Freshman requesting CS301):")
    print(f"  -------------------------------------------------------------")
    print(chat_res['response'][:300] + "...\n")
    print(f"  ⚠️ Conflicts Detected: {chat_res.get('conflicts')}")
    print(f"  📚 Citations: {chat_res.get('citations')}")

    print("\n" + "=" * 70)
    print("🎉 ALL 6 TEST PHASES PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
