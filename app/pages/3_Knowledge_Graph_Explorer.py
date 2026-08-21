import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.student import StudentProfile
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.knowledge_graph.graph_queries import (
    get_prerequisites,
    get_all_prerequisites_recursive,
    get_dependents,
    get_bottleneck_courses,
    get_equivalent_courses
)
from src.knowledge_graph.graph_visualizer import create_prerequisite_graph, create_student_progress_graph
from src.utils.config import DATA_DIR
from app.ui_theme import inject_custom_css, render_hero_banner, render_kpi_card, render_sidebar_student, render_help_tip

st.set_page_config(page_title="Knowledge Graph Explorer | Academic Pathway Advisor", page_icon="🕸️", layout="wide")
inject_custom_css()

if "student" in st.session_state:
    render_sidebar_student(st.session_state.student)

student: StudentProfile = st.session_state.get("student")

render_hero_banner(
    title="🕸️ Knowledge Graph <span class='gradient-text'>Explorer</span>",
    subtitle="Interactive 2D graph visualization of curriculum dependencies, prerequisite chains, and course statuses.",
    badge_text="Section 3 · Curriculum Graph AI"
)

render_help_tip(
    title="Color Legend & Interactive Graph Controls",
    explanation="🟢 <strong>Green (Completed):</strong> Passed courses on transcript. &nbsp;|&nbsp; 🔵 <strong>Blue (Available):</strong> Prereqs met, ready to enroll. &nbsp;|&nbsp; 🔴 <strong>Red (Locked):</strong> Missing prerequisites. &nbsp;|&nbsp; 🟡 <strong>Yellow (In-Progress / Planned):</strong> Currently enrolled or planned. &nbsp;<br><em>(Drag nodes to explore, scroll to zoom in/out)</em>",
    icon="🎨"
)

@st.cache_resource
def get_kg():
    kg = AcademicKnowledgeGraph()
    kg.load_from_json(
        str(DATA_DIR / "courses.json"),
        str(DATA_DIR / "degree_requirements.json"),
        str(DATA_DIR / "equivalencies.json")
    )
    return kg

kg = get_kg()
all_courses = kg.get_all_courses()

col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🎛️ Select Course to Inspect")
    
    dept_filter = st.selectbox("Filter by Department", ["All", "CS", "MATH", "PHYS", "ENG", "PHIL", "ECON"])
    
    filtered_courses = all_courses
    if dept_filter != "All":
        filtered_courses = [c for c in all_courses if c.department == dept_filter]
        
    course_options = [f"{c.id} - {c.name}" for c in filtered_courses]
    selected_option = st.selectbox("Choose Course:", course_options if course_options else ["None"])
    
    selected_cid = selected_option.split(" - ")[0] if selected_option != "None" else None
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("### ⚡ Top Curriculum Bottlenecks")
    st.caption("Courses with the highest downstream prerequisite impact:")
    
    bottlenecks = get_bottleneck_courses(kg, top_n=5)
    for cid, count in bottlenecks:
        c = kg.get_course(cid)
        cname = c.name if c else cid
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 6px 10px; margin-bottom: 6px;">
                <div>
                    <strong style="color: #f87171; font-size: 0.88rem;">{cid}</strong>
                    <span style="color: #cbd5e1; font-size: 0.8rem; margin-left: 6px;">{cname}</span>
                </div>
                <span class="status-badge badge-locked">Unlocks {count}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    if selected_cid and selected_cid in kg.courses:
        course = kg.get_course(selected_cid)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"## 📖 <span class='gradient-text'>{course.id}: {course.name}</span>", unsafe_allow_html=True)
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            render_kpi_card("Credits", f"{course.credits} cr", "Units", "info", "🎓")
        with m2:
            render_kpi_card("Department", course.department, "Faculty", "info", "🏛️")
        with m3:
            render_kpi_card("Difficulty", f"{course.difficulty_level}/5", "Workload", "warning", "⚡")
        with m4:
            render_kpi_card("Offered", ", ".join([s.value for s in course.offered_semesters]), "Terms", "success", "🗓️")
            
        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.5); border-left: 3px solid #2563eb; padding: 10px 14px; border-radius: 0 8px 8px 0; margin: 10px 0; color: #e2e8f0; font-size: 0.9rem;">
                <strong>Course Description:</strong> {course.description}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Prereqs, Dependents, and Substitutions
        direct_prereqs = get_prerequisites(kg, selected_cid)
        all_prereqs = get_all_prerequisites_recursive(kg, selected_cid)
        dependents = get_dependents(kg, selected_cid)
        equivalencies = get_equivalent_courses(kg, selected_cid)
        
        cp1, cp2 = st.columns(2)
        with cp1:
            st.markdown("##### 📌 Prerequisites")
            if direct_prereqs:
                st.markdown(f"**Direct Prerequisites:** `{', '.join(direct_prereqs)}`")
                st.markdown(f"<span style='font-size: 0.8rem; color: #94a3b8;'>Full Recursive Chain: {', '.join(all_prereqs)}</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='color: #34d399;'>✅ Entry-level course (No prerequisites).</span>", unsafe_allow_html=True)
                
            if course.corequisites:
                st.markdown(f"**Co-requisites:** `{', '.join(course.corequisites)}`")
                
        with cp2:
            st.markdown("##### 🔁 Substitutions & Downstream")
            if equivalencies:
                st.markdown(f"**Approved Substitutes:** `{', '.join(equivalencies)}`")
            else:
                st.caption("No automatic substitute on file.")
                
            if dependents:
                st.markdown(f"**Required for:** `{', '.join(dependents[:4])}`")
            else:
                st.caption("Terminal or elective course.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"### 🕸️ Interactive Subgraph: {selected_cid}")
        try:
            completed_set = set(student.completed_course_ids) if student else set()
            html_graph = create_student_progress_graph(kg, completed_set)
            components.html(html_graph, height=450, scrolling=True)
        except Exception as e:
            st.error(f"Error rendering graph: {e}")
    else:
        st.info("👈 Select a course to inspect its prerequisites and substitution options.")
        try:
            completed_set = set(student.completed_course_ids) if student else set()
            html_graph = create_student_progress_graph(kg, completed_set)
            components.html(html_graph, height=550, scrolling=True)
        except Exception as e:
            st.error(f"Error rendering graph: {e}")
