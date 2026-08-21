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
    title="🎓 Academic Advisor <span class='gradient-text'>Intelligence Hub</span>",
    subtitle="Next-generation university advising powered by Hybrid Graph-RAG, Topological Constraint Checking, and Gemini 3.6 Flash.",
    badge_text="⚡ Enterprise Academic AI Platform"
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
                <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; font-weight: 600;">Active AI Model</div>
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

    m1, m2, m3, m4, m5 = st.columns(5)
    
    with m1:
        st.markdown(
            """
            <div class="nav-card">
                <div class="nav-card-icon">📊</div>
                <div class="nav-card-title">Dashboard</div>
                <div class="nav-card-desc">Audit degree progress, category requirements, and risk scores.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.page_link("pages/1_Dashboard.py", label="Open Dashboard", icon="📊", use_container_width=True)

    with m2:
        st.markdown(
            """
            <div class="nav-card">
                <div class="nav-card-icon">🗺️</div>
                <div class="nav-card-title">Pathway Planner</div>
                <div class="nav-card-desc">Topologically sequence your future semesters without conflicts.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.page_link("pages/2_Pathway_Planner.py", label="Open Planner", icon="🗺️", use_container_width=True)

    with m3:
        st.markdown(
            """
            <div class="nav-card">
                <div class="nav-card-icon">🔍</div>
                <div class="nav-card-title">Course Explorer</div>
                <div class="nav-card-desc">Explore 2D interactive knowledge graphs and bottleneck chains.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.page_link("pages/3_Course_Explorer.py", label="Explore Graph", icon="🔍", use_container_width=True)

    with m4:
        st.markdown(
            """
            <div class="nav-card">
                <div class="nav-card-icon">💬</div>
                <div class="nav-card-title">AI Advisor</div>
                <div class="nav-card-desc">Ask questions with verified policy citations and RAG grounding.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.page_link("pages/4_AI_Advisor.py", label="Chat with AI", icon="💬", use_container_width=True)

    with m5:
        st.markdown(
            """
            <div class="nav-card">
                <div class="nav-card-icon">⚠️</div>
                <div class="nav-card-title">Conflict Checker</div>
                <div class="nav-card-desc">Simulate upcoming terms and validate against load limits.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.page_link("pages/5_Conflict_Checker.py", label="Check Conflicts", icon="⚠️", use_container_width=True)

else:
    st.warning("Please ensure the backend data is available in the `data/` directory.")
