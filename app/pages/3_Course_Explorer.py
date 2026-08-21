import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.knowledge_graph.graph_queries import (
    get_prerequisites,
    get_all_prerequisites_recursive,
    get_dependents,
    get_bottleneck_courses,
    get_equivalent_courses,
    get_prerequisite_chain_length
)
from src.knowledge_graph.graph_visualizer import create_prerequisite_graph
from src.utils.config import DATA_DIR
from app.ui_theme import inject_custom_css, render_hero_banner, render_kpi_card, render_sidebar_student

st.set_page_config(page_title="Course Explorer | Academic Advisor", page_icon="🔍", layout="wide")
inject_custom_css()

if "student" in st.session_state:
    render_sidebar_student(st.session_state.student)

render_hero_banner(
    title="🔍 Academic Knowledge Graph & <span class='gradient-text'>Course Explorer</span>",
    subtitle="Inspect curriculum topologies, recursive prerequisite dependency chains, and critical bottleneck courses.",
    badge_text="2D Physics Knowledge Graph Visualizer"
)

from app.ui_theme import render_help_tip
render_help_tip(
    title="How to Read the Curriculum Knowledge Graph",
    explanation="Select any course on the left to see its direct requirements and all downstream classes that depend on it. In the interactive graph, drag nodes around, scroll to zoom in/out, and click nodes to explore prerequisite relationships.",
    icon="🕸️"
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

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🎛️ Catalog Filters")
    
    dept_filter = st.selectbox("Department Filter", ["All", "CS", "MATH", "PHYS", "ENG", "PHIL", "ECON", "PSY", "HIST", "COMM"])
    
    filtered_courses = all_courses
    if dept_filter != "All":
        filtered_courses = [c for c in all_courses if c.department == dept_filter]
        
    course_options = [f"{c.id} - {c.name}" for c in filtered_courses]
    selected_option = st.selectbox("Select Course to Inspect", course_options if course_options else ["None"])
    
    selected_cid = selected_option.split(" - ")[0] if selected_option != "None" else None
    
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    st.markdown("### ⚡ Critical Bottleneck Index")
    st.caption("Courses with the highest downstream prerequisite load across the degree:")
    
    bottlenecks = get_bottleneck_courses(kg, top_n=6)
    for cid, count in bottlenecks:
        c = kg.get_course(cid)
        cname = c.name if c else cid
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 8px 12px; margin-bottom: 6px;">
                <div>
                    <span style="font-weight: 700; color: #f87171; font-size: 0.9rem;">{cid}</span>
                    <span style="color: #cbd5e1; font-size: 0.82rem; margin-left: 6px;">{cname}</span>
                </div>
                <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); padding: 2px 8px; border-radius: 12px; font-size: 0.72rem; font-weight: 700; color: #fca5a5;">
                    Unlocks {count}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if selected_cid and selected_cid in kg.courses:
        course = kg.get_course(selected_cid)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"## 📖 <span class='gradient-text'>{course.id}: {course.name}</span>", unsafe_allow_html=True)
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            render_kpi_card("Credits", f"{course.credits} cr", "Semester Units", "info", "🎓")
        with m2:
            render_kpi_card("Department", course.department, "Faculty Unit", "info", "🏛️")
        with m3:
            render_kpi_card("Difficulty", f"{course.difficulty_level}/5", "Workload Index", "warning", "⚡")
        with m4:
            render_kpi_card("Offered In", ", ".join([s.value for s in course.offered_semesters]), "Availability", "success", "🗓️")
            
        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.5); border-left: 3px solid #6366f1; border-radius: 0 8px 8px 0; padding: 12px 16px; margin: 14px 0; color: #e2e8f0; font-size: 0.95rem; line-height: 1.6;">
                <strong>Catalog Description:</strong> {course.description}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Prereqs and dependents
        direct_prereqs = get_prerequisites(kg, selected_cid)
        all_prereqs = get_all_prerequisites_recursive(kg, selected_cid)
        dependents = get_dependents(kg, selected_cid)
        equivalencies = get_equivalent_courses(kg, selected_cid)
        
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            st.markdown("##### 📌 Prerequisite Chain")
            if direct_prereqs:
                st.markdown(
                    f"""
                    <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 8px; padding: 10px; font-size: 0.85rem; color: #c7d2fe;">
                        <div><strong>Direct:</strong> {', '.join(direct_prereqs)}</div>
                        <div style="margin-top: 4px; font-size: 0.8rem; color: #94a3b8;"><strong>Full Ancestry:</strong> {', '.join(all_prereqs) if all_prereqs else 'None'}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown("<div style='color: #34d399; font-size: 0.88rem;'>✅ No prerequisites (Entry-level introductory course).</div>", unsafe_allow_html=True)
                
            if course.corequisites:
                st.caption(f"Corequisites: {', '.join(course.corequisites)}")
                
        with c_p2:
            st.markdown("##### 🚀 Downstream Dependents")
            if dependents:
                st.markdown(
                    f"""
                    <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 8px; padding: 10px; font-size: 0.85rem; color: #fde68a;">
                        <strong>Required for {len(dependents)} courses:</strong><br>{', '.join(dependents)}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.caption("No downstream required courses (Terminal/Upper-division Elective).")
                
            if equivalencies:
                st.markdown(f"**🔁 Equivalent Course Substitutions:** `{', '.join(equivalencies)}`")
        st.markdown('</div>', unsafe_allow_html=True)
                
        st.markdown(f"### 🕸️ Prerequisite Dependency Subgraph: {selected_cid}")
        try:
            html_graph = create_prerequisite_graph(kg, selected_cid)
            components.html(html_graph, height=450, scrolling=True)
        except Exception as e:
            st.error(f"Error rendering graph: {e}")
    else:
        st.info("👈 Select a course from the list to inspect its graph relationships.")
        st.markdown("### 🕸️ Complete Curriculum Prerequisite Network")
        try:
            html_graph = create_prerequisite_graph(kg)
            components.html(html_graph, height=600, scrolling=True)
        except Exception as e:
            st.error(f"Error rendering graph: {e}")
