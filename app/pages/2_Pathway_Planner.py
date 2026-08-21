import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.student import StudentProfile
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.knowledge_graph.graph_visualizer import create_student_progress_graph
from src.constraint_engine.schedule_feasibility import ScheduleAnalyzer
from src.constraint_engine.prerequisite_checker import PrerequisiteChecker
from src.constraint_engine.credit_validator import CreditValidator
from src.utils.config import DATA_DIR
from app.ui_theme import inject_custom_css, render_hero_banner, render_kpi_card, render_sidebar_student

st.set_page_config(page_title="Pathway Planner | Academic Advisor", page_icon="🗺️", layout="wide")
inject_custom_css()

if "student" not in st.session_state:
    st.warning("⚠️ No student selected. Please select a student from the main page.")
    st.stop()

student: StudentProfile = st.session_state.student
render_sidebar_student(student)

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

render_hero_banner(
    title="🗺️ Degree Pathway <span class='gradient-text'>Sequencer & Roadmap</span>",
    subtitle=f"Automated topological sequencing for <strong>{student.name}</strong> balancing term availability, load limits, and prerequisite trees.",
    badge_text="Graph-RAG Multi-Semester Engine"
)

# Controls
col1, col2 = st.columns([1, 3])
with col1:
    generate_btn = st.button("✨ Re-Optimize Pathway", type="primary", use_container_width=True)
with col2:
    st.markdown(
        """
        <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 12px; padding: 10px 16px; font-size: 0.88rem; color: #c7d2fe;">
            💡 <strong>Topological Load Balancing:</strong> Evaluates all remaining core and elective prerequisites, distributes 12-16 credits per term, and verifies term availability.
        </div>
        """,
        unsafe_allow_html=True
    )

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
        render_kpi_card(
            title="Planned Semesters",
            value=f"{len(plans)}",
            delta="Sequenced",
            delta_type="info",
            icon="📅"
        )
    with m2:
        render_kpi_card(
            title="Credits Scheduled",
            value=f"{total_planned_credits} cr",
            delta=f"~{total_planned_credits//len(plans) if plans else 0} cr / term",
            delta_type="success",
            icon="⚖️"
        )
    with m3:
        render_kpi_card(
            title="Projected Graduation Credits",
            value=f"{student.total_credits_earned + total_planned_credits} / 120",
            delta="Requirement Met" if (student.total_credits_earned + total_planned_credits) >= 120 else "Under 120cr",
            delta_type="success",
            icon="🎯"
        )
    with m4:
        render_kpi_card(
            title="Target Graduation",
            value=est_grad_term,
            delta="Earliest Horizon",
            delta_type="success",
            icon="🎓"
        )

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

col_plans, col_viz = st.columns([1, 1])

with col_plans:
    st.markdown("### 📅 Optimized Semester Roadmap")
    
    if not plans:
        st.info("No remaining courses need scheduling — student is ready to graduate!")
    
    accumulated_completed = set(student.completed_course_ids)
    all_planned_courses = set()
    
    for idx, plan in enumerate(plans):
        conflicts = prereq_checker.validate_semester_plan(plan.courses, accumulated_completed, plan.semester)
        has_conflicts = len(conflicts) > 0
        
        status_chip = "⚠️ Constraints Alert" if has_conflicts else "🟢 Verified Prereqs"
        chip_class = "delta-warning" if has_conflicts else "delta-success"
        
        card_header = f"Term {idx + 1}: {plan.semester.value} {plan.year} — {plan.total_credits} Credits"
        
        with st.expander(f"📍 {card_header}", expanded=(idx < 3)):
            for cid in plan.courses:
                course = kg.get_course(cid)
                cname = course.name if course else cid
                dept = course.department if course else "CS"
                cr = course.credits if course else 3
                
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px;">
                        <div>
                            <span style="font-weight: 700; color: #818cf8; font-size: 0.95rem;">[{dept}] {cid}</span>
                            <span style="color: #f1f5f9; margin-left: 8px; font-size: 0.9rem;">{cname}</span>
                        </div>
                        <div style="background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: 700; color: #c7d2fe;">
                            {cr} cr
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                    
            if conflicts:
                st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
                for c in conflicts:
                    if c.severity == "error":
                        st.error(f"❌ {c.description}")
                    else:
                        st.warning(f"⚠️ {c.description}")
            else:
                st.markdown("<div style='font-size: 0.8rem; color: #34d399; margin-top: 4px;'>✅ All prerequisite and credit load constraints passed.</div>", unsafe_allow_html=True)
                
        accumulated_completed.update(plan.courses)
        all_planned_courses.update(plan.courses)

with col_viz:
    st.markdown("### 🕸️ Degree Knowledge Graph Overlay")
    
    st.markdown(
        """
        <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; font-size: 0.8rem;">
            <span style="display: flex; align-items: center; gap: 4px;"><span style="color: #22c55e;">●</span> Completed</span>
            <span style="display: flex; align-items: center; gap: 4px;"><span style="color: #f97316;">●</span> Planned Pathway</span>
            <span style="display: flex; align-items: center; gap: 4px;"><span style="color: #3b82f6;">●</span> Eligible Now</span>
            <span style="display: flex; align-items: center; gap: 4px;"><span style="color: #94a3b8;">●</span> Locked</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    try:
        html_graph = create_student_progress_graph(kg, student.completed_course_ids, all_planned_courses)
        components.html(html_graph, height=650, scrolling=True)
    except Exception as e:
        st.error(f"Could not render graph visualization: {e}")
