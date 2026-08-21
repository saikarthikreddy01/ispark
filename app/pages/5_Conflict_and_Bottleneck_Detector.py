import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.student import StudentProfile
from src.models.course import Semester
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.knowledge_graph.graph_queries import get_equivalent_courses, get_bottleneck_courses
from src.constraint_engine.prerequisite_checker import PrerequisiteChecker
from src.constraint_engine.credit_validator import CreditValidator
from src.utils.config import DATA_DIR
from app.ui_theme import inject_custom_css, render_hero_banner, render_kpi_card, render_sidebar_student, render_help_tip

st.set_page_config(page_title="Conflict & Bottleneck Detector | Academic Pathway Advisor", page_icon="⚠️", layout="wide")
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
prereq_checker = PrerequisiteChecker(kg)
credit_val = CreditValidator(kg)

render_hero_banner(
    title="⚠️ Conflict & <span class='gradient-text'>Bottleneck Detector</span>",
    subtitle=f"Audit prerequisite dependency violations, curriculum rule mismatches, and course availability risks for <strong>{student.name}</strong>.",
    badge_text="Section 5 · Constraint Verification & Bottlenecks"
)

render_help_tip(
    title="Understanding Conflicts & Bottlenecks",
    explanation="<strong>Prerequisite Conflicts:</strong> Attempting to register for courses without passing all foundational prerequisites. &nbsp;|&nbsp; <strong>Curriculum Bottlenecks:</strong> High-demand courses with strict prerequisite trees that can delay your expected graduation if missed.",
    icon="⚠️"
)

# Section A: Interactive Term Conflict Simulator
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("### 1️⃣ Upcoming Term Schedule Simulator")

all_courses = kg.get_all_courses()
course_options = [f"{c.id} - {c.name} ({c.credits} cr)" for c in all_courses]

col1, col2 = st.columns([2, 1])
with col1:
    default_picks = [opt for opt in course_options if opt.startswith("CS301") or opt.startswith("CS302") or opt.startswith("CS303")]
    selected_options = st.multiselect(
        "Select courses you plan to take simultaneously:",
        course_options,
        default=default_picks[:2] if default_picks else course_options[:2]
    )
    selected_cids = [opt.split(" - ")[0] for opt in selected_options]
    
with col2:
    target_sem_str = st.radio("Target Semester Offering", ["FALL", "SPRING", "SUMMER"], horizontal=True)
    target_sem = Semester[target_sem_str]
    total_credits = sum(kg.get_course_credits(cid) for cid in selected_cids)
    st.metric("Total Selected Credits", f"{total_credits} / {student.max_credits_per_semester} cr")

st.markdown('</div>', unsafe_allow_html=True)

# Run Diagnostics
completed_ids = set(student.completed_course_ids)
conflicts = prereq_checker.validate_semester_plan(selected_cids, completed_ids, target_sem)

if total_credits > student.max_credits_per_semester:
    from src.models.pathway import Conflict, ConflictType
    conflicts.append(Conflict(
        type=ConflictType.CREDIT_OVERLOAD,
        course_id="SCHEDULE",
        description=f"Semester load ({total_credits} cr) exceeds maximum allowed limit of {student.max_credits_per_semester} cr (Policy §5.2).",
        severity="error",
        suggested_resolution="Drop an elective course or request a Dean GPA overload waiver."
    ))

# Display Conflict Report
st.markdown("### 📋 Schedule Conflict & Violation Report")
if conflicts:
    st.markdown(f"**Found {len(conflicts)} issue(s) in proposed schedule:**")
    for conflict in conflicts:
        eqs = get_equivalent_courses(kg, conflict.course_id)
        sub_text = f"Approved Alternatives: {', '.join(eqs)}" if eqs else "No direct substitute on file."
        
        st.markdown(
            f"""
            <div style="background: rgba(239, 68, 68, 0.12); border-left: 4px solid #ef4444; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="color: #fca5a5; font-size: 0.95rem;">❌ [{conflict.type.value}] {conflict.course_id}</strong>
                    <span class="status-badge badge-locked">Violation</span>
                </div>
                <div style="color: #f1f5f9; font-size: 0.88rem; margin: 4px 0 6px 0;">{conflict.description}</div>
                <div style="font-size: 0.82rem; color: #93c5fd; background: rgba(15, 23, 42, 0.6); padding: 6px 10px; border-radius: 6px;">
                    💡 <strong>Suggested Action / Substitute:</strong> {conflict.suggested_resolution or sub_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.markdown(
        """
        <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 10px; padding: 16px; text-align: center; margin-bottom: 16px;">
            <div style="font-weight: 700; color: #34d399; font-size: 1.05rem;">✅ All Clear! No Prerequisite or Credit Conflicts Found.</div>
            <div style="font-size: 0.84rem; color: #a7f3d0; margin-top: 2px;">This schedule meets all curriculum rules and is 100% valid for registration.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# Section B: Bottleneck Risk Matrix
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("### ⚡ Curriculum Bottleneck Risk Analysis")
st.caption("Courses with high downstream prerequisite dependency and limited term availability:")

bottlenecks = get_bottleneck_courses(kg, top_n=6)
b_records = []
for cid, count in bottlenecks:
    c = kg.get_course(cid)
    is_done = cid in completed_ids
    eqs = get_equivalent_courses(kg, cid)
    b_records.append({
        "Course ID": cid,
        "Course Title": c.name if c else cid,
        "Department": c.department if c else "CS",
        "Credits": c.credits if c else 3,
        "Downstream Impact": f"Unlocks {count} courses",
        "Status": "🟢 Passed" if is_done else "🔴 Needs Clearance",
        "Approved Substitutions": ", ".join(eqs) if eqs else "None (Core Requirement)"
    })

df_b = pd.DataFrame(b_records)
st.dataframe(df_b, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)
