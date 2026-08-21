import streamlit as st
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.rag.vector_store import AcademicVectorStore
from src.rag.document_loader import PolicyDocumentLoader
from src.models.student import StudentProfile
from src.utils.config import DATA_DIR

# Page config
st.set_page_config(
    page_title="🎓 Academic Advisor AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    # Load policies
    chunks = loader.load_and_chunk(str(DATA_DIR / "policies.md"))
    kg = init_knowledge_graph()
    chunks += loader.load_course_descriptions(kg.get_all_courses())
    vs.add_documents(chunks)
    return vs

@st.cache_data
def load_students():
    with open(DATA_DIR / "sample_students.json") as f:
        data = json.load(f)
    return {s["id"]: StudentProfile(**s) for s in data}

# Sidebar - Student selector
st.sidebar.title("🎓 Graph-RAG Academic Advisor")
st.sidebar.markdown("---")

try:
    students = load_students()
    selected_id = st.sidebar.selectbox(
        "Select Student",
        options=list(students.keys()),
        format_func=lambda x: f"{students[x].name} ({students[x].major})"
    )
    st.session_state.student = students[selected_id]
    student = st.session_state.student

    # Student info card in sidebar
    st.sidebar.markdown(f"### {student.name}")
    st.sidebar.markdown(f"**Major:** {student.major}")
    st.sidebar.markdown(f"**Year:** {student.current_year} | **Semester:** {student.current_semester.value}")
    st.sidebar.markdown(f"**GPA:** {student.gpa:.2f}")
    st.sidebar.markdown(f"**Credits:** {student.total_credits_earned}/120")
    st.sidebar.progress(min(student.total_credits_earned / 120, 1.0))
except Exception as e:
    st.sidebar.error("Could not load student data. Please check data files.")
    student = None

# Main landing page
st.title("🎓 Graph-RAG Academic Advisor")
st.markdown("### AI-Powered Academic Planning with Knowledge Graphs")
st.markdown("---")

if student:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Credits Earned", student.total_credits_earned)
    with col2:
        st.metric("Credits Remaining", max(0, 120 - student.total_credits_earned))
    with col3:
        st.metric("GPA", f"{student.gpa:.2f}")
    with col4:
        st.metric("Courses Completed", len(student.completed_course_ids))

    st.markdown("---")
    st.markdown("#### Navigate to:")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.page_link("pages/1_Dashboard.py", label="Dashboard", icon="📊")
    with c2:
        st.page_link("pages/2_Pathway_Planner.py", label="Pathway Planner", icon="🗺️")
    with c3:
        st.page_link("pages/3_Course_Explorer.py", label="Course Explorer", icon="🔍")
    with c4:
        st.page_link("pages/4_AI_Advisor.py", label="AI Advisor", icon="💬")
    with c5:
        st.page_link("pages/5_Conflict_Checker.py", label="Conflict Checker", icon="⚠️")
else:
    st.warning("Please ensure the backend data is available in the `data/` directory.")
