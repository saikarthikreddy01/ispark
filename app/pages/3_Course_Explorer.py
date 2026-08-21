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

st.set_page_config(page_title="Course Explorer | Academic Advisor", page_icon="🔍", layout="wide")

st.title("🔍 Academic Knowledge Graph & Course Explorer")
st.markdown("Explore course relationships, recursive prerequisite chains, dependencies, and curriculum bottleneck topology.")

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
    st.subheader("Filter & Select")
    
    dept_filter = st.selectbox("Filter Department", ["All", "CS", "MATH", "PHYS", "ENG", "PHIL", "ECON", "PSY", "HIST", "COMM"])
    
    filtered_courses = all_courses
    if dept_filter != "All":
        filtered_courses = [c for c in all_courses if c.department == dept_filter]
        
    course_options = [f"{c.id} - {c.name}" for c in filtered_courses]
    selected_option = st.selectbox("Select Course to Inspect", course_options if course_options else ["None"])
    
    selected_cid = selected_option.split(" - ")[0] if selected_option != "None" else None
    
    st.markdown("---")
    st.subheader("⚡ Top Curriculum Bottlenecks")
    st.caption("Courses with the highest number of dependent downstream courses in the prerequisite graph.")
    
    bottlenecks = get_bottleneck_courses(kg, top_n=6)
    for cid, count in bottlenecks:
        c = kg.get_course(cid)
        cname = c.name if c else cid
        st.markdown(f"- **{cid}** ({cname}): unlocks **{count} courses**")

with col2:
    if selected_cid and selected_cid in kg.courses:
        course = kg.get_course(selected_cid)
        
        st.subheader(f"📖 {course.id}: {course.name}")
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Credits", course.credits)
        with m2:
            st.metric("Department", course.department)
        with m3:
            st.metric("Difficulty", f"{course.difficulty_level}/5")
        with m4:
            st.metric("Offered Terms", ", ".join([s.value for s in course.offered_semesters]))
            
        st.markdown(f"**Course Description:**\n{course.description}")
        
        # Prereqs and dependents
        direct_prereqs = get_prerequisites(kg, selected_cid)
        all_prereqs = get_all_prerequisites_recursive(kg, selected_cid)
        dependents = get_dependents(kg, selected_cid)
        equivalencies = get_equivalent_courses(kg, selected_cid)
        chain_len = get_prerequisite_chain_length(kg, selected_cid)
        
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            st.markdown("##### 📌 Prerequisites")
            if direct_prereqs:
                st.info(f"**Direct:** {', '.join(direct_prereqs)}\n\n**Full Chain:** {', '.join(all_prereqs) if all_prereqs else 'None'}")
            else:
                st.success("No prerequisites (Entry-level course).")
                
            if course.corequisites:
                st.caption(f"**Corequisites:** {', '.join(course.corequisites)}")
                
        with c_p2:
            st.markdown("##### 🚀 Dependent Courses")
            if dependents:
                st.warning(f"**Required for {len(dependents)} courses:**\n{', '.join(dependents)}")
            else:
                st.caption("No downstream required courses (Terminal/Elective).")
                
            if equivalencies:
                st.markdown(f"**🔁 Equivalent Course Substitutions:** {', '.join(equivalencies)}")
                
        st.markdown("---")
        st.subheader(f"🕸️ Prerequisite Subgraph for {selected_cid}")
        
        try:
            html_graph = create_prerequisite_graph(kg, selected_cid)
            components.html(html_graph, height=450, scrolling=True)
        except Exception as e:
            st.error(f"Error rendering graph: {e}")
    else:
        st.info("👈 Select a course from the sidebar to inspect its graph relationships.")
        st.subheader("🕸️ Entire Computer Science Prerequisite Network")
        try:
            html_graph = create_prerequisite_graph(kg)
            components.html(html_graph, height=600, scrolling=True)
        except Exception as e:
            st.error(f"Error rendering graph: {e}")

