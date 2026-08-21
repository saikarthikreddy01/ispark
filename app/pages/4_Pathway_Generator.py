import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.student import StudentProfile
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.constraint_engine.schedule_feasibility import ScheduleAnalyzer
from src.constraint_engine.prerequisite_checker import PrerequisiteChecker
from src.constraint_engine.credit_validator import CreditValidator
from src.utils.config import DATA_DIR
from app.ui_theme import inject_custom_css, render_hero_banner, render_kpi_card, render_sidebar_student, render_help_tip

st.set_page_config(page_title="Pathway Generator | Academic Pathway Advisor", page_icon="🗺️", layout="wide")
inject_custom_css()

if "student" not in st.session_state:
    st.warning("⚠️ No student selected. Please select a student from the sidebar.")
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
    title="🗺️ Pathway <span class='gradient-text'>Generator</span>",
    subtitle=f"Personalized multi-semester course roadmaps tailored to career goals and load constraints for <strong>{student.name}</strong>.",
    badge_text="Section 4 · Automated Degree Sequencing"
)

render_help_tip(
    title="How Pathway Generation Works",
    explanation="Enter your career goal and desired credit load below. The engine uses topological graph sorting to arrange all remaining prerequisites and core requirements into a conflict-free semester plan.",
    icon="🗺️"
)

# Input Form
with st.form(key="pathway_form"):
    st.markdown("### 🎛️ Pathway Preferences & Target Constraints")
    
    col1, col2 = st.columns(2)
    with col1:
        career_goal = st.selectbox(
            "🎯 Primary Career Goal / Track:",
            ["AI/ML Engineer & Data Science", "Full-Stack Software Engineering", "Cloud & Distributed Systems", "Cybersecurity & Cryptography", "General Computer Science"]
        )
        target_grad = st.selectbox(
            "🗓️ Target Graduation Horizon:",
            ["Spring 2025", "Fall 2025", "Spring 2026", "Fall 2026", "Spring 2027"]
        )
        
    with col2:
        max_credits = st.slider("⚖️ Maximum Allowed Credits / Term:", min_value=12, max_value=21, value=student.max_credits_per_semester)
        course_load = st.radio(
            "⚡ Preferred Course Intensity:",
            ["Balanced (15-16 credits/term)", "Light (12-14 credits/term)", "Accelerated (17-19 credits/term)"],
            horizontal=True
        )
        
    generate_btn = st.form_submit_button("✨ Generate Optimized Pathway", type="primary", use_container_width=True)

# Process Pathway
if generate_btn or "pathway_plans" not in st.session_state:
    with st.spinner("🤖 Running topological graph traversal and balancing semester credit constraints..."):
        plans = schedule_analyzer.suggest_semester_load(student)
        st.session_state.pathway_plans = plans

plans = st.session_state.get("pathway_plans", [])

# Output Timeline & Metrics
if plans:
    total_planned_credits = sum(p.total_credits for p in plans)
    est_grad_term = f"{plans[-1].semester.value} {plans[-1].year}" if plans else target_grad
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_kpi_card("Planned Semesters", f"{len(plans)} Terms", "Sequenced", "info", "📅")
    with m2:
        render_kpi_card("Credits Scheduled", f"{total_planned_credits} cr", f"~{total_planned_credits//len(plans) if plans else 0} cr / term", "success", "⚖️")
    with m3:
        render_kpi_card("Total Toward Degree", f"{student.total_credits_earned + total_planned_credits} / 120", "Goal Met", "success", "🎯")
    with m4:
        render_kpi_card("Projected Graduation", est_grad_term, "On Track", "success", "🎓")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📅 Semester-by-Semester Recommended Timeline")

    accumulated = set(student.completed_course_ids)
    
    for idx, plan in enumerate(plans):
        conflicts = prereq_checker.validate_semester_plan(plan.courses, accumulated, plan.semester)
        has_conflicts = len(conflicts) > 0
        
        card_class = "border-left: 4px solid #ef4444;" if has_conflicts else "border-left: 4px solid #10b981;"
        status_label = "⚠️ Conflicts Flagged" if has_conflicts else "🟢 Prerequisites Met"
        
        with st.expander(f"📍 Term {idx + 1}: {plan.semester.value} {plan.year} — {plan.total_credits} Credits ({status_label})", expanded=(idx < 2)):
            for cid in plan.courses:
                course = kg.get_course(cid)
                cname = course.name if course else cid
                dept = course.department if course else "CS"
                cr = course.credits if course else 3
                
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 8px 12px; margin-bottom: 6px;">
                        <div>
                            <strong style="color: #93c5fd;">[{dept}] {cid}</strong>
                            <span style="color: #f1f5f9; margin-left: 8px; font-size: 0.9rem;">{cname}</span>
                        </div>
                        <span style="background: rgba(37, 99, 235, 0.15); border: 1px solid rgba(37, 99, 235, 0.3); padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: 700; color: #93c5fd;">
                            {cr} cr
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            if conflicts:
                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                for c in conflicts:
                    st.markdown(
                        f"""
                        <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; padding: 8px 12px; margin-top: 6px; color: #fca5a5; font-size: 0.85rem;">
                            <strong>❌ Conflict Detected:</strong> {c.description}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.markdown("<div style='color: #34d399; font-size: 0.82rem; margin-top: 4px;'>✅ All prerequisite and credit load limits passed.</div>", unsafe_allow_html=True)
                
        accumulated.update(plan.courses)
else:
    st.success("🎉 All degree requirements satisfied! Student is ready for graduation.")
