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

st.set_page_config(page_title="Conflict Checker | Academic Advisor", page_icon="⚠️", layout="wide")

st.title("⚠️ Real-Time Prerequisite & Schedule Conflict Resolver")
st.markdown("Select proposed courses for an upcoming term to run formal prerequisite, corequisite, offering availability, and credit overload verification.")

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
prereq_checker = PrerequisiteChecker(kg)
credit_val = CreditValidator(kg)

all_courses = kg.get_all_courses()
course_options = [f"{c.id} - {c.name} ({c.credits} cr)" for c in all_courses]

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("1. Proposed Course Selection")
    
    # Sensible defaults for demo: courses like CS301, CS303
    default_picks = [opt for opt in course_options if opt.startswith("CS301") or opt.startswith("CS302") or opt.startswith("CS303")]
    
    selected_options = st.multiselect(
        "Select courses you plan to take simultaneously:",
        course_options,
        default=default_picks[:2] if default_picks else course_options[:2]
    )
    
    target_sem_str = st.radio("Target Semester", ["FALL", "SPRING", "SUMMER"], horizontal=True)
    target_sem = Semester[target_sem_str]
    
    selected_cids = [opt.split(" - ")[0] for opt in selected_options]
    
    check_btn = st.button("⚡ Run Conflict Verification", type="primary", use_container_width=True)

with col2:
    st.subheader("2. Credit Load Verification")
    
    total_planned_credits = sum(kg.get_course_credits(cid) for cid in selected_cids)
    max_credits = student.max_credits_per_semester
    
    pct = min(total_planned_credits / max_credits, 1.0) if max_credits > 0 else 1.0
    st.progress(pct)
    st.markdown(f"**Total Selected Credits:** **{total_planned_credits} / {max_credits}** cr")
    
    if total_planned_credits > max_credits:
        st.error(f"❌ **Credit Overload Warning:** {total_planned_credits} credits exceeds the max standard load of {max_credits} (Requires Dean Overload Approval per Policy §5.2).")
    elif total_planned_credits < 12 and selected_cids:
        st.warning("⚠️ **Part-Time Load Warning:** Fewer than 12 credits may impact full-time student status or financial aid per Policy §5.3.")
    elif selected_cids:
        st.success("✅ Credit load is within standard full-time limits (12-18 credits).")

st.markdown("---")

# Analysis results
st.subheader("3. Verification & Diagnostic Engine Results")

if check_btn or selected_cids:
    with st.spinner("Checking prerequisite DAGs, corequisite constraints, and offering calendar..."):
        completed_ids = set(student.completed_course_ids)
        conflicts = prereq_checker.validate_semester_plan(selected_cids, completed_ids, target_sem)
        
        # Also check credit overload conflict
        if total_planned_credits > max_credits:
            from src.models.pathway import Conflict, ConflictType
            conflicts.append(Conflict(
                type=ConflictType.CREDIT_OVERLOAD,
                course_id="ALL",
                description=f"Semester load ({total_planned_credits} credits) exceeds maximum allowed limit of {max_credits} credits.",
                severity="error",
                suggested_resolution="Drop one elective course or submit a GPA-based overload petition (Policy §5.2)."
            ))
            
        if not conflicts:
            st.success("🎉 **All Clear!** No prerequisite violations, offering conflicts, or credit overloads detected. This schedule is 100% valid for registration!")
        else:
            st.markdown(f"**Found {len(conflicts)} issue(s) in proposed schedule:**")
            
            for idx, conflict in enumerate(conflicts):
                sev_icon = "❌" if conflict.severity == "error" else "⚠️"
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

