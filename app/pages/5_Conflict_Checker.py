import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.student import StudentProfile
from src.models.course import Semester
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.constraint_engine.prerequisite_checker import PrerequisiteChecker
from src.constraint_engine.credit_validator import CreditValidator
from src.utils.config import DATA_DIR
from app.ui_theme import inject_custom_css, render_hero_banner, render_kpi_card, render_sidebar_student

st.set_page_config(page_title="Conflict Checker | Academic Advisor", page_icon="⚠️", layout="wide")
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
prereq_checker = PrerequisiteChecker(kg)
credit_val = CreditValidator(kg)

render_hero_banner(
    title="⚠️ Real-Time Prerequisite & <span class='gradient-text'>Schedule Conflict Validator</span>",
    subtitle=f"Simulate upcoming semester course selections for <strong>{student.name}</strong> to catch prerequisite violations and credit overloads before registration.",
    badge_text="Constraint Verification Engine"
)

from app.ui_theme import render_help_tip
render_help_tip(
    title="How Schedule Validation Works",
    explanation="<strong>Step 1:</strong> Select the courses you want to take next term. &nbsp;|&nbsp; <strong>Step 2:</strong> Pick the semester (Fall/Spring). &nbsp;|&nbsp; <strong>Step 3:</strong> The engine automatically checks if you completed all prerequisites, ensures the course is offered in that semester, and verifies you stay within 12–18 credits.",
    icon="🔍"
)

all_courses = kg.get_all_courses()
course_options = [f"{c.id} - {c.name} ({c.credits} cr)" for c in all_courses]

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 1️⃣ Proposed Course Selection")
    
    # Sensible defaults for demo
    default_picks = [opt for opt in course_options if opt.startswith("CS301") or opt.startswith("CS302") or opt.startswith("CS303")]
    
    selected_options = st.multiselect(
        "Select courses you plan to take simultaneously:",
        course_options,
        default=default_picks[:2] if default_picks else course_options[:2]
    )
    
    c_sem, c_btn = st.columns([2, 1])
    with c_sem:
        target_sem_str = st.radio("Target Semester", ["FALL", "SPRING", "SUMMER"], horizontal=True)
        target_sem = Semester[target_sem_str]
    with c_btn:
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        check_btn = st.button("⚡ Verify Schedule", type="primary", use_container_width=True)
        
    selected_cids = [opt.split(" - ")[0] for opt in selected_options]
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 2️⃣ Credit Load Analysis")
    
    total_planned_credits = sum(kg.get_course_credits(cid) for cid in selected_cids)
    max_credits = student.max_credits_per_semester
    
    pct = min(total_planned_credits / max_credits, 1.0) if max_credits > 0 else 1.0
    st.progress(pct)
    
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin: 12px 0 8px 0;">
            <span style="color: #94a3b8; font-size: 0.88rem;">Scheduled Load:</span>
            <span style="font-weight: 800; color: #f8fafc; font-size: 1.25rem;">{total_planned_credits} / {max_credits} cr</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if total_planned_credits > max_credits:
        st.markdown(
            f"""
            <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 10px; font-size: 0.82rem; color: #fca5a5;">
                ❌ <strong>Credit Overload:</strong> {total_planned_credits} cr exceeds standard cap of {max_credits} cr (Requires Dean Overload Approval per Policy §5.2).
            </div>
            """,
            unsafe_allow_html=True
        )
    elif total_planned_credits < 12 and selected_cids:
        st.markdown(
            """
            <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 10px; font-size: 0.82rem; color: #fde68a;">
                ⚠️ <strong>Part-Time Load Alert:</strong> Under 12 credits may impact full-time standing or financial aid (Policy §5.3).
            </div>
            """,
            unsafe_allow_html=True
        )
    elif selected_cids:
        st.markdown(
            """
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 10px; font-size: 0.82rem; color: #6ee7b7;">
                ✅ <strong>Optimal Load:</strong> Perfectly balanced full-time schedule (12-18 credits).
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# Analysis results
st.markdown("### 3️⃣ Diagnostic Verification Engine Results")

if check_btn or selected_cids:
    with st.spinner("Checking prerequisite DAGs, corequisite constraints, and offering calendar..."):
        completed_ids = set(student.completed_course_ids)
        conflicts = prereq_checker.validate_semester_plan(selected_cids, completed_ids, target_sem)
        
        # Also check credit overload conflict
        if total_planned_credits > max_credits:
            from src.models.pathway import Conflict, ConflictType
            conflicts.append(Conflict(
                type=ConflictType.CREDIT_OVERLOAD,
                course_id="SCHEDULE",
                description=f"Semester load ({total_planned_credits} credits) exceeds maximum allowed limit of {max_credits} credits.",
                severity="error",
                suggested_resolution="Drop one elective course or submit a GPA-based overload petition (Policy §5.2)."
            ))
            
        if not conflicts:
            st.markdown(
                """
                <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 12px; padding: 20px; text-align: center; margin: 10px 0;">
                    <div style="font-size: 2.5rem; margin-bottom: 8px;">🎉</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #34d399; margin-bottom: 4px;">All Verification Checks Passed!</div>
                    <div style="font-size: 0.9rem; color: #a7f3d0;">No prerequisite violations, term offering conflicts, or credit overloads detected. This proposed schedule is 100% ready for enrollment.</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(f"**Found {len(conflicts)} diagnostic issue(s) in proposed schedule:**")
            
            for idx, conflict in enumerate(conflicts):
                sev_icon = "❌" if conflict.severity == "error" else "⚠️"
                border_color = "rgba(239, 68, 68, 0.4)" if conflict.severity == "error" else "rgba(245, 158, 11, 0.4)"
                bg_color = "rgba(239, 68, 68, 0.1)" if conflict.severity == "error" else "rgba(245, 158, 11, 0.1)"
                
                with st.expander(f"{sev_icon} [{conflict.type.value}] {conflict.course_id}: {conflict.description}", expanded=True):
                    st.write(f"**Diagnostic Details:** {conflict.description}")
                    
                    # Generate actionable resolution tip
                    if conflict.type.value == "PREREQUISITE_MISSING":
                        st.info("💡 **Resolution Action:** Take missing foundational prerequisite in an earlier term, or apply for a faculty waiver (Policy §1.2).")
                    elif conflict.type.value == "NOT_OFFERED":
                        st.info(f"💡 **Resolution Action:** This course is not offered in {target_sem.value}. Move it to an alternate term when offered.")
                    elif conflict.type.value == "ALREADY_COMPLETED":
                        st.info("💡 **Resolution Action:** You have already earned credit for this course. Remove it to avoid unneeded tuition charges.")
                    elif conflict.type.value == "COREQUISITE_MISSING":
                        st.info("💡 **Resolution Action:** Add the mandatory companion corequisite (e.g. lab section) to your schedule.")
                    else:
                        st.info(f"💡 **Resolution Action:** {conflict.suggested_resolution or 'Consult your academic advisor.'}")
