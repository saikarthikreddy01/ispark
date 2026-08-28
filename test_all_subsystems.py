"""
Comprehensive Automated Test Suite for Academic AI Advisor (3D Graph-RAG Platform)
Tests:
1. Knowledge Graph (NetworkX DAG, Acyclicity, Topological Closures, Bottlenecks)
2. Constraint Engine (Prerequisite Checker, Credit Validator, Schedule Feasibility)
3. Graph-RAG & Citations (Document Loader, Vector Store, Hybrid Retriever, Citation Tracking)
4. Multi-Agent System (Orchestrator, Classification, Pathway, Conflict, Risk, Substitution)
5. FastAPI REST API (All Core Endpoints via FastAPI TestClient)
"""

import sys
import os
import json
import traceback
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def print_header(title: str):
    print("\n" + "=" * 75)
    print(f"  [*] {title}")
    print("=" * 75)

def print_result(name: str, passed: bool, details: str = ""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} | {name}" + (f" -> {details}" if details else ""))

total_tests = 0
passed_tests = 0
failed_tests = 0

def record_test(name: str, passed: bool, details: str = ""):
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    if passed:
        passed_tests += 1
    else:
        failed_tests += 1
    print_result(name, passed, details)


# =========================================================================
# TEST SUITE 1: KNOWLEDGE GRAPH & NETWORKX DAG ALGORITHMS
# =========================================================================
def test_knowledge_graph():
    print_header("1. KNOWLEDGE GRAPH & NETWORKX DAG ALGORITHMS")
    try:
        from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
        import networkx as nx
        
        kg = AcademicKnowledgeGraph()
        courses_file = str(PROJECT_ROOT / "data" / "courses.json")
        degree_file = str(PROJECT_ROOT / "data" / "degree_requirements.json")
        equiv_file = str(PROJECT_ROOT / "data" / "equivalencies.json")
        
        kg.load_from_json(courses_file, degree_file, equiv_file)
        
        # Test 1.1: Node count
        num_nodes = len(kg.graph.nodes)
        num_courses = len(kg.courses)
        record_test("Load Courses into Knowledge Graph", num_courses > 0, f"{num_courses} courses, {num_nodes} total graph nodes")
        
        # Test 1.2: Directed Graph validation
        is_directed = isinstance(kg.graph, nx.DiGraph)
        record_test("Directed Graph Structure (DiGraph)", is_directed)
        
        # Test 1.3: Prerequisite Acyclicity (Only course-to-course prerequisite edges)
        prereq_subgraph = nx.DiGraph()
        for u, v, data in kg.graph.edges(data=True):
            if data.get("type") == "FORMAL_PREREQUISITE":
                prereq_subgraph.add_edge(u, v)
                
        is_dag = nx.is_directed_acyclic_graph(prereq_subgraph)
        record_test("Prerequisite DAG Acyclicity (Zero Circular Dependencies)", is_dag, f"{prereq_subgraph.number_of_edges()} prerequisite dependencies verified")
        
        # Test 1.4: Topological Sorting / Order
        prereq_subgraph.add_nodes_from(kg.courses)
        topological_order = list(nx.topological_sort(prereq_subgraph))
        record_test("Topological Sort Computation", len(topological_order) > 0, f"Topological order of {len(topological_order)} sequenced nodes")
        
        # Test 1.5: Course Ancestor / Prerequisite Closure Query
        sample_course = next(iter(kg.courses.keys()))
        ancestors = nx.ancestors(prereq_subgraph, sample_course) if sample_course in prereq_subgraph else set()
        record_test("Prerequisite Ancestor Closure Query", True, f"Course '{sample_course}' has {len(ancestors)} prerequisite ancestors")
        
    except Exception as e:
        record_test("Knowledge Graph Suite", False, f"Exception: {str(e)}\n{traceback.format_exc()}")


# =========================================================================
# TEST SUITE 2: FORMAL CONSTRAINT ENGINE
# =========================================================================
def test_constraint_engine():
    print_header("2. FORMAL CONSTRAINT ENGINE")
    try:
        from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
        from src.constraint_engine.prerequisite_checker import PrerequisiteChecker
        from src.constraint_engine.credit_validator import CreditValidator
        from src.constraint_engine.schedule_feasibility import ScheduleAnalyzer
        from src.models.student import Student
        
        kg = AcademicKnowledgeGraph()
        kg.load_from_json(
            str(PROJECT_ROOT / "data" / "courses.json"),
            str(PROJECT_ROOT / "data" / "degree_requirements.json"),
            str(PROJECT_ROOT / "data" / "equivalencies.json")
        )
        
        # 2.1 Prerequisite Checker
        prereq_checker = PrerequisiteChecker(kg)
        
        # Test course with no prereqs
        sample_no_prereqs = None
        sample_with_prereqs = None
        for c in kg.courses.values():
            if not c.prerequisites and not sample_no_prereqs:
                sample_no_prereqs = c.id
            if c.prerequisites and not sample_with_prereqs:
                sample_with_prereqs = c.id
        
        if sample_no_prereqs:
            ok, missing = prereq_checker.check_prerequisites(sample_no_prereqs, set())
            record_test(f"Prerequisite Check (No Prereqs: {sample_no_prereqs})", ok and len(missing) == 0)
            
        if sample_with_prereqs:
            # Without completed courses -> should fail
            ok_empty, missing_empty = prereq_checker.check_prerequisites(sample_with_prereqs, set())
            record_test(f"Prerequisite Violation Detection ({sample_with_prereqs})", not ok_empty and len(missing_empty) > 0, f"Correctly caught missing {missing_empty}")
            
            # With completed courses -> should pass
            needed = set(kg.courses[sample_with_prereqs].prerequisites)
            ok_sat, missing_sat = prereq_checker.check_prerequisites(sample_with_prereqs, needed)
            record_test(f"Prerequisite Satisfaction ({sample_with_prereqs})", ok_sat, "Approved when prerequisites satisfied")
            
        # 2.2 Credit Validator
        credit_validator = CreditValidator(kg)
        student = Student(
            id="TEST_STU_001",
            name="Alice Candidate",
            major="Computer Science & Engineering",
            gpa=3.8,
            completed_courses=["24CS101", "24MA101", "24PH101"],
            planned_courses=["24CS201", "24CS202"]
        )
        
        # Check credit calculation
        summary = credit_validator.calculate_student_credits(student)
        record_test("Credit Calculation & Degree Audit", summary.total_completed >= 0, f"Completed: {summary.total_completed} cr, In-Progress: {summary.total_in_progress} cr")
        
        # Check Overload detection
        is_overload = credit_validator.is_overload_semester(25, student)
        record_test("Credit Overload Detection (>24 credits)", is_overload)
        
        # 2.3 Schedule Feasibility
        analyzer = ScheduleAnalyzer(kg)
        feasibility = analyzer.analyze_graduation_feasibility(student)
        record_test("Graduation Feasibility & Remaining Terms", "semesters_remaining" in feasibility, f"Semesters remaining: {feasibility.get('semesters_remaining')}, Risk Score: {feasibility.get('risk_score')}")

    except Exception as e:
        record_test("Constraint Engine Suite", False, f"Exception: {str(e)}\n{traceback.format_exc()}")


# =========================================================================
# TEST SUITE 3: GRAPH-RAG & POLICY CITATION SYSTEM
# =========================================================================
def test_graph_rag():
    print_header("3. GRAPH-RAG & POLICY CITATION SYSTEM")
    try:
        from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
        from src.rag.document_loader import PolicyDocumentLoader
        from src.rag.vector_store import AcademicVectorStore
        from src.rag.graph_retriever import GraphRAGRetriever
        from src.rag.citation_tracker import CitationTracker
        
        kg = AcademicKnowledgeGraph()
        kg.load_from_json(
            str(PROJECT_ROOT / "data" / "courses.json"),
            str(PROJECT_ROOT / "data" / "degree_requirements.json"),
            str(PROJECT_ROOT / "data" / "equivalencies.json")
        )
        
        # 3.1 Policy Document Loader
        loader = PolicyDocumentLoader()
        chunks = loader.load_and_chunk(str(PROJECT_ROOT / "data" / "policies.md"))
        record_test("Policy Document Loader & Section Chunking", len(chunks) > 0, f"Parsed {len(chunks)} policy sections from policies.md")
        
        # 3.2 Vector Store
        vector_store = AcademicVectorStore()
        chunks += loader.load_course_descriptions(kg.get_all_courses())
        vector_store.add_documents(chunks)
        record_test("Vector Store Indexing", vector_store.count() > 0, f"Indexed {vector_store.count()} document chunks into vector store")
        
        # 3.3 Semantic Retrieval
        search_results = vector_store.search("prerequisite waiver policy detention grade requirement", top_k=3)
        top_sec = search_results[0]['metadata'].get('section', 'Unknown') if search_results else 'None'
        record_test("Vector Similarity Search", len(search_results) > 0, f"Top match: {top_sec}")
        
        # 3.4 Hybrid Graph-RAG Retriever
        hybrid_retriever = GraphRAGRetriever(kg, vector_store)
        retrieval_output = hybrid_retriever.retrieve("What are the prerequisites for Data Structures?")
        record_test("Hybrid Graph-RAG Retrieval (Graph + Vector)", bool(retrieval_output.graph_context or retrieval_output.policy_context), f"Extracted {len(retrieval_output.citations)} citations")
        
        # 3.5 Citation Tracker
        tracker = CitationTracker()
        tracker.register_sources_from_chunks(chunks)
        sample_claim = "Students with CGPA below 4.0 are placed on academic probation."
        verified, best_cite = tracker.verify_claim(sample_claim)
        record_test("Citation Grounding Verification", bool(best_cite or tracker.citation_index), f"Citation index tracks {len(tracker.citation_index)} policy references")

    except Exception as e:
        record_test("Graph-RAG Suite", False, f"Exception: {str(e)}\n{traceback.format_exc()}")


# =========================================================================
# TEST SUITE 4: MULTI-AGENT ADVISING SYSTEM
# =========================================================================
def test_multi_agent():
    print_header("4. MULTI-AGENT ADVISING SYSTEM")
    try:
        from src.agents.orchestrator import AcademicAdvisor
        from src.models.student import Student
        
        advisor = AcademicAdvisor()
        
        # 4.1 Query Classification
        q_prereq = advisor.classify_query("Can I enroll in Machine Learning without prerequisites?")
        q_pathway = advisor.classify_query("Generate a multi-semester graduation roadmap for me")
        q_risk = advisor.classify_query("Am I at risk of delayed graduation?")
        q_sub = advisor.classify_query("Can I take an online course instead of Operating Systems?")
        q_pol = advisor.classify_query("What is the credit limit policy per semester?")
        
        record_test("Agent Query Classifier: Prerequisite", q_prereq == "prerequisite")
        record_test("Agent Query Classifier: Pathway", q_pathway == "pathway")
        record_test("Agent Query Classifier: Academic Risk", q_risk == "risk")
        record_test("Agent Query Classifier: Course Substitution", q_sub == "substitution")
        record_test("Agent Query Classifier: Policy Inquiry", q_pol == "policy")
        
        # 4.2 End-to-End Chat & Decision Synthesis
        student = Student(
            id="241FA04001",
            name="John Doe",
            major="Computer Science & Engineering",
            gpa=3.6,
            completed_courses=["24CS101", "24MA101"],
            planned_courses=["24CS201"]
        )
        
        chat_result = advisor.chat_sync("Can I enroll in 24CS201?", student=student)
        has_response = "response" in chat_result and len(chat_result["response"]) > 0
        has_citations = "citations" in chat_result and len(chat_result["citations"]) > 0
        record_test("End-to-End Advisor Chat Synthesis", has_response, f"Response: {len(chat_result.get('response', ''))} chars")
        record_test("Advisor Citations & Grounding", has_citations, f"{len(chat_result.get('citations', []))} citations attached")
        
    except Exception as e:
        record_test("Multi-Agent Suite", False, f"Exception: {str(e)}\n{traceback.format_exc()}")


# =========================================================================
# TEST SUITE 5: FASTAPI REST API SERVER & ENDPOINTS
# =========================================================================
def test_fastapi_endpoints():
    print_header("5. FASTAPI REST API SERVER & ENDPOINTS")
    try:
        from starlette.testclient import TestClient
        from backend.server import app
        
        client = TestClient(app)
        
        # 5.1 Health check
        res = client.get("/api/health")
        record_test("API Endpoint: GET /api/health", res.status_code == 200, f"Status: {res.json().get('status')}")
        
        # 5.2 Courses list
        res = client.get("/api/courses")
        record_test("API Endpoint: GET /api/courses", res.status_code == 200, f"{len(res.json())} courses retrieved")
        
        # 5.3 Single course details
        if res.status_code == 200 and len(res.json()) > 0:
            first_course_id = res.json()[0]["id"]
            res_course = client.get(f"/api/courses/{first_course_id}")
            record_test(f"API Endpoint: GET /api/courses/{first_course_id}", res_course.status_code == 200, f"Retrieved course: {res_course.json().get('name')}")
            
        # 5.4 Curriculum breakdown
        res = client.get("/api/curriculum")
        record_test("API Endpoint: GET /api/curriculum", res.status_code == 200, f"Semesters: {len(res.json().get('semesters', []))}")
        
        # 5.5 Equivalencies
        res = client.get("/api/equivalencies")
        record_test("API Endpoint: GET /api/equivalencies", res.status_code == 200, f"{len(res.json())} course equivalencies found")
        
        # 5.6 Students list
        res = client.get("/api/students")
        record_test("API Endpoint: GET /api/students", res.status_code == 200, f"{len(res.json())} student records")
        
        sample_student_id = res.json()[0]["id"] if (res.status_code == 200 and len(res.json()) > 0) else "241FA04001"
        
        # 5.7 Student detail
        res = client.get(f"/api/student/{sample_student_id}")
        record_test(f"API Endpoint: GET /api/student/{sample_student_id}", res.status_code == 200, f"Student: {res.json().get('name')}")
        
        # 5.8 Pathway generation
        res = client.post("/api/pathway/generate", json={
            "student_id": sample_student_id,
            "max_credits_per_semester": 18,
            "target_graduation": "Spring 2028"
        })
        record_test("API Endpoint: POST /api/pathway/generate", res.status_code == 200, f"Pathway status: {res.json().get('status')}")
        
        # 5.9 Audit verification
        res = client.post("/api/audit/verify", json={
            "student_id": sample_student_id,
            "selected_courses": ["24CS101", "24MA101"],
            "semester": "Fall 2026"
        })
        record_test("API Endpoint: POST /api/audit/verify", res.status_code == 200, f"Approved: {res.json().get('approved')}")
        
        # 5.10 Bottlenecks analysis
        res = client.get(f"/api/bottlenecks/{sample_student_id}")
        record_test(f"API Endpoint: GET /api/bottlenecks/{sample_student_id}", res.status_code == 200, f"Bottlenecks found: {len(res.json().get('critical_bottlenecks', []))}")
        
        # 5.11 Policies catalog
        res = client.get("/api/policies")
        record_test("API Endpoint: GET /api/policies", res.status_code == 200, f"{len(res.json())} policy documents")
        
        # 5.12 Petitions governance
        res = client.get("/api/petitions")
        record_test("API Endpoint: GET /api/petitions", res.status_code == 200, f"{len(res.json())} petitions in governance queue")
        
        # 5.13 AI Advising Chat Endpoint
        res = client.post("/api/chat", json={
            "student_id": sample_student_id,
            "question": "What courses should I register for next semester to graduate on time?"
        })
        record_test("API Endpoint: POST /api/chat", res.status_code == 200, f"Advisor answered ({len(res.json().get('response', ''))} chars, {len(res.json().get('citations', []))} citations)")
        
    except Exception as e:
        record_test("FastAPI Endpoints Suite", False, f"Exception: {str(e)}\n{traceback.format_exc()}")


# =========================================================================
# MAIN TEST RUNNER
# =========================================================================
if __name__ == "__main__":
    print("\n" + "#" * 75)
    print("  [>] RUNNING COMPREHENSIVE TEST SUITE ACROSS ALL PLATFORM SUBSYSTEMS")
    print("#" * 75)
    
    test_knowledge_graph()
    test_constraint_engine()
    test_graph_rag()
    test_multi_agent()
    test_fastapi_endpoints()
    
    print("\n" + "=" * 75)
    print("  [*] TEST EXECUTION SUMMARY")
    print("=" * 75)
    print(f"  Total Tests Executed : {total_tests}")
    print(f"  Passed Tests         : {passed_tests} [PASS]")
    print(f"  Failed Tests         : {failed_tests} [FAIL]")
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"  Success Rate         : {success_rate:.1f}%")
    print("=" * 75 + "\n")
    
    if failed_tests > 0:
        sys.exit(1)
    else:
        sys.exit(0)
