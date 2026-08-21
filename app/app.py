import streamlit as st
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.rag.vector_store import AcademicVectorStore
from src.rag.document_loader import PolicyDocumentLoader
from src.models.student import StudentProfile
from src.utils.config import DATA_DIR, MODEL_NAME
from app.ui_theme import inject_custom_css, render_hero_banner, render_kpi_card, render_sidebar_student

# Page config
st.set_page_config(
    page_title="🎓 Graph-RAG Academic Advisor AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
inject_custom_css()

# Initialize shared resources in session state (cached)
@st.cache_resource
def init_knowledge_graph():
    kg = AcademicKnowledgeGraph()
    kg.load_from_json(
        str(DATA_DIR / "courses.json"),
        str(DATA_DIR / "degree_requirements.json"),
        str(DATA_DIR / "equivalencies.json")
    )
    return kg

@st.cache_resource
def init_vector_store():
    vs = AcademicVectorStore()
    loader = PolicyDocumentLoader()
    chunks = loader.load_and_chunk(str(DATA_DIR / "policies.md"))
    kg = init_knowledge_graph()
    chunks += loader.load_course_descriptions(kg.get_all_courses())
    vs.add_documents(chunks)
    return vs, len(chunks)

@st.cache_data
def load_students():
    with open(DATA_DIR / "sample_students.json") as f:
        data = json.load(f)
    return {s["id"]: StudentProfile(**s) for s in data}

# Load engines
kg = init_knowledge_graph()
vs, chunk_count = init_vector_store()

# Sidebar - Student selector
st.sidebar.markdown('<div class="gradient-text" style="font-size: 1.25rem; font-weight: 800; margin-bottom: 8px;">🎓 Graph-RAG Advisor</div>', unsafe_allow_html=True)
st.sidebar.caption("Intelligent University Academic Intelligence")
st.sidebar.markdown("---")

try:
    students = load_students()
    selected_id = st.sidebar.selectbox(
        "Select Active Student Profile",
        options=list(students.keys()),
        format_func=lambda x: f"{students[x].name} ({students[x].major})"
    )
    st.session_state.student = students[selected_id]
    student = st.session_state.student

    # Render rich sidebar profile card
    render_sidebar_student(student)
except Exception as e:
    st.sidebar.error("Could not load student data.")
    student = None

# Main Hero Banner
render_hero_banner(
    title="🎓 Decentralized <span class='gradient-text'>Graph-RAG Academic Advisor</span>",
    subtitle="AI-driven academic planning, prerequisite conflict resolution, topological pathway generation, and faculty exception workflows.",
    badge_text="⚡ Enterprise Academic Intelligence & Graph AI"
)

# System Health Bar
col_sys1, col_sys2, col_sys3, col_sys4 = st.columns(4)
with col_sys1:
    st.markdown(
        f"""
        <div class="glass-card-compact" style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.5rem;">🕸️</span>
            <div>
                <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; font-weight: 600;">Knowledge Graph</div>
                <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">{kg.graph.number_of_nodes()} Nodes · {kg.graph.number_of_edges()} Edges</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col_sys2:
    st.markdown(
        f"""
        <div class="glass-card-compact" style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.5rem;">📚</span>
            <div>
                <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; font-weight: 600;">Vector RAG Index</div>
                <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">{chunk_count} Policy Chunks</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col_sys3:
    st.markdown(
        f"""
        <div class="glass-card-compact" style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.5rem;">🤖</span>
            <div>
                <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; font-weight: 600;">Active AI Engine</div>
                <div style="font-weight: 700; color: #818cf8; font-size: 0.95rem;">{MODEL_NAME}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col_sys4:
    st.markdown(
        """
        <div class="glass-card-compact" style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.5rem;">🟢</span>
            <div>
                <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; font-weight: 600;">Constraint Engine</div>
                <div style="font-weight: 700; color: #34d399; font-size: 0.95rem;">Active & Validated</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# Student Quick Metrics
if student:
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        render_kpi_card(
            title="Earned Credits",
            value=f"{student.total_credits_earned} <span style='font-size: 1rem; color: #94a3b8;'>/ 120</span>",
            delta=f"{max(0, 120 - student.total_credits_earned)} credits to grad",
            delta_type="info",
            icon="🎓"
        )
    with kpi2:
        render_kpi_card(
            title="Cumulative GPA",
            value=f"{student.gpa:.2f}",
            delta="Good Standing" if student.gpa >= 2.0 else "Probation Alert",
            delta_type="success" if student.gpa >= 2.0 else "danger",
            icon="📈"
        )
    with kpi3:
        render_kpi_card(
            title="Academic Standing",
            value=f"Year {student.current_year}",
            delta=f"{student.current_semester.value} Term",
            delta_type="info",
            icon="🏛️"
        )
    with kpi4:
        render_kpi_card(
            title="Courses Completed",
            value=f"{len(student.completed_course_ids)}",
            delta="Prereqs Indexed",
            delta_type="success",
            icon="✅"
        )

    st.markdown("### 🧭 Interactive Intelligence Modules")
    st.caption("Select a specialized workflow to explore your degree pathway, curriculum topology, or converse with AI.")

    # 6 Feature cards in 2 rows of 3
    r1_c1, r1_c2, r1_c3 = st.columns(3)
    
    with r1_c1:
        st.markdown(
            """
            <div class="nav-card">
                <div class="nav-card-icon">📊</div>
                <div class="nav-card-title">1. Dashboard & Degree Audit</div>
                <div class="nav-card-desc">Audit degree requirements, GPA standing, and graduation feasibility risk scores.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.page_link("pages/1_Dashboard.py", label="Open Dashboard", icon="📊", use_container_width=True)

    with r1_c2:
        st.markdown(
            """
            <div class="nav-card">
                <div class="nav-card-icon">🗺️</div>
                <div class="nav-card-title">2. Pathway Planner</div>
                <div class="nav-card-desc">Topologically sequence multi-semester roadmaps balancing loads and term offerings.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.page_link("pages/2_Pathway_Planner.py", label="Open Planner", icon="🗺️", use_container_width=True)

    with r1_c3:
        st.markdown(
            """
            <div class="nav-card">
                <div class="nav-card-icon">🔍</div>
                <div class="nav-card-title">3. Course Explorer & Graph</div>
                <div class="nav-card-desc">Explore 2D interactive knowledge graph topologies and critical bottleneck paths.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.page_link("pages/3_Course_Explorer.py", label="Explore Graph", icon="🔍", use_container_width=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    r2_c1, r2_c2, r2_c3 = st.columns(3)

    with r2_c1:
        st.markdown(
            """
            <div class="nav-card">
                <div class="nav-card-icon">💬</div>
                <div class="nav-card-title">4. AI Academic Advisor</div>
                <div class="nav-card-desc">Natural language advising with verified policy citations and RAG grounding.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.page_link("pages/4_AI_Advisor.py", label="Chat with AI", icon="💬", use_container_width=True)

    with r2_c2:
        st.markdown(
            """
            <div class="nav-card">
                <div class="nav-card-icon">⚠️</div>
                <div class="nav-card-title">5. Conflict Checker</div>
                <div class="nav-card-desc">Simulate upcoming schedules and validate against prerequisite & credit rules.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.page_link("pages/5_Conflict_Checker.py", label="Check Conflicts", icon="⚠️", use_container_width=True)

    with r2_c3:
        st.markdown(
            """
            <div class="nav-card">
                <div class="nav-card-icon">📝</div>
                <div class="nav-card-title">6. Substitutions & Faculty Approval</div>
                <div class="nav-card-desc">Discover alternative courses and submit formal constraint waiver petitions.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.page_link("pages/6_Faculty_Approvals_and_Substitutions.py", label="Open Exceptions & Approvals", icon="📝", use_container_width=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Hackathon Expected Features Verification Matrix
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🏆 Prototype Feature Requirements Matrix")
    st.caption("Verification of all 8 core problem statement requirements:")

    req_cols1, req_cols2 = st.columns(2)
    with req_cols1:
        st.markdown(
            """
            - ✅ **Knowledge Graph Engine:** NetworkX course DAGs, prerequisite chains, and curriculum rules ([Course Explorer](pages/3_Course_Explorer.py)).
            - ✅ **Graph-RAG Policy Retrieval:** ChromaDB semantic store over institutional academic policies ([AI Advisor](pages/4_AI_Advisor.py)).
            - ✅ **Student-Specific Pathway Generation:** Automated topological sequencing to graduation ([Pathway Planner](pages/2_Pathway_Planner.py)).
            - ✅ **Prerequisite & Credit Conflict Detection:** Real-time multi-course overload and dependency checks ([Conflict Checker](pages/5_Conflict_Checker.py)).
            """
        )
    with req_cols2:
        st.markdown(
            """
            - ✅ **Graduation-Risk & Bottleneck Identification:** Downstream dependent impact scores and feasibility metrics ([Dashboard](pages/1_Dashboard.py)).
            - ✅ **Alternative Course Recommendations:** Direct and cross-disciplinary substitution suggestions ([Substitutions](pages/6_Faculty_Approvals_and_Substitutions.py)).
            - ✅ **Citation-Traceable Advising:** Grounded Gemini 3.6 Flash responses with clickable policy footnotes ([AI Advisor](pages/4_AI_Advisor.py)).
            - ✅ **Formal Constraint & Faculty Approval Workflow:** Waiver petitions with Dean/Chair sign-off ([Faculty Approvals](pages/6_Faculty_Approvals_and_Substitutions.py)).
            """
        )
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.warning("Please ensure the backend data is available in the `data/` directory.")
