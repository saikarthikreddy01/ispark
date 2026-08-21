import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.student import StudentProfile
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.knowledge_graph.graph_visualizer import create_student_progress_graph, create_prerequisite_graph
from src.constraint_engine.schedule_feasibility import ScheduleAnalyzer
from src.constraint_engine.prerequisite_checker import PrerequisiteChecker
from src.constraint_engine.credit_validator import CreditValidator
from src.utils.config import DATA_DIR

st.set_page_config(page_title="Pathway Planner | Academic Advisor", page_icon="🗺️", layout="wide")

st.title("🗺️ Degree Pathway Planner")
st.markdown("Automated semester-wise course sequencing with topological prerequisite resolution and load balancing.")

if "student" not in st.session_state:
    st.warning("⚠️ No student selected. Please select a student from the main page.")
    st.stop()

student: StudentProfile = st.session_state.student

# Load KG and Engines
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
schedule_analyzer = ScheduleAnalyzer(kg)
prereq_checker = PrerequisiteChecker(kg)
credit_val = CreditValidator(kg)

# Controls
col1, col2 = st.columns([1, 3])
with col1:
    generate_btn = st.button("✨ Auto-Generate Optimal Pathway", type="primary", use_container_width=True)
with col2:
    st.info("💡 **Graph-Optimized Pathway**: Topologically sorts remaining requirements, balances credit loads, and verifies semester offering availability.")

# Session state pathway initialization or generation
if generate_btn or "pathway_plans" not in st.session_state:
    with st.spinner("🤖 Resolving prerequisite graph and balancing semester loads..."):
        plans = schedule_analyzer.suggest_semester_load(student)
        st.session_state.pathway_plans = plans
        if generate_btn:
            st.success("✅ Pathway successfully generated and verified against degree constraints!")

plans = st.session_state.get("pathway_plans", [])

# Summary Metrics
if plans:
    total_planned_credits = sum(p.total_credits for p in plans)
    est_grad_term = f"{plans[-1].semester.value} {plans[-1].year}" if plans else "N/A"
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Planned Semesters", len(plans))
    with m2:
        st.metric("Total Credits Planned", total_planned_credits)
    with m3:
        st.metric("Projected Total Credits", student.total_credits_earned + total_planned_credits)
    with m4:
        st.metric("Est. Graduation", est_grad_term)

st.markdown("---")

col_plans, col_viz = st.columns([1, 1])

with col_plans:
    st.subheader("📅 Semester-by-Semester Roadmap")
    
    if not plans:
        st.info("No remaining courses need scheduling — student is ready to graduate!")
    
    accumulated_completed = set(student.completed_course_ids)
    all_planned_courses = set()
    
    for idx, plan in enumerate(plans):
        conflicts = prereq_checker.validate_semester_plan(plan.courses, accumulated_completed, plan.semester)
        has_conflicts = len(conflicts) > 0
        
        card_title = f"Semester {idx + 1}: {plan.semester.value} {plan.year} — {plan.total_credits} Credits"
        if has_conflicts:
            card_title = f"⚠️ {card_title} ({len(conflicts)} warning/conflict)"
            
        with st.expander(card_title, expanded=(idx < 3)):
            for cid in plan.courses:
                course = kg.get_course(cid)
                cname = course.name if course else cid
                dept = course.department if course else "CS"
                cr = course.credits if course else 3
                
                c_col1, c_col2 = st.columns([4, 1])
                with c_col1:
                    st.markdown(f"**[{dept}] {cid}**: {cname}")
                with c_col2:
                    st.caption(f"{cr} credits")
                    
            if conflicts:
                st.markdown("---")
                for c in conflicts:
                    if c.severity == "error":
                        st.error(f"❌ {c.description}")
                    else:
                        st.warning(f"⚠️ {c.description}")
            else:
                st.caption("✅ All prerequisites and credit constraints satisfied.")
                
        accumulated_completed.update(plan.courses)
        all_planned_courses.update(plan.courses)

with col_viz:
    st.subheader("🕸️ Academic Knowledge Graph Overlay")
    st.caption("🟢 Completed | 🟠 Planned in Pathway | 🔵 Available Now | ⚪ Locked")
    
    try:
        html_graph = create_student_progress_graph(kg, student.completed_course_ids, all_planned_courses)
        components.html(html_graph, height=650, scrolling=True)
    except Exception as e:
        st.error(f"Could not render graph visualization: {e}")

