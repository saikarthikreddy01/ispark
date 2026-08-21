import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.student import StudentProfile
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from app.ui_theme import inject_custom_css, render_hero_banner, render_kpi_card, render_sidebar_student, render_help_tip
from src.utils.database import load_petitions, seed_default_petitions, update_petition_status

st.set_page_config(page_title="Faculty Approval Panel | Academic Pathway Advisor", page_icon="📝", layout="wide")
inject_custom_css()

if "student" not in st.session_state:
    st.warning("⚠️ No student selected. Please select a student from the sidebar.")
    st.stop()

student: StudentProfile = st.session_state.student
render_sidebar_student(student)

render_hero_banner(
    title="📝 Faculty Approval <span class='gradient-text'>Panel</span>",
    subtitle=f"Administrative portal to review student exception requests, prerequisite overrides, and credit overload petitions.",
    badge_text="Section 6 · Administrative Governance & Overrides"
)

render_help_tip(
    title="About the Faculty Approval Workflow",
    explanation="Students who require course substitutions, prerequisite waivers (§1.2), or credit overloads (>18 cr) submit petitions here. Faculty and Deans can review academic qualifications and formally approve or reject petitions with audit comments.",
    icon="🏛️"
)

# Load persistent petition queue from SQLite.
seed_default_petitions(student)
petitions = load_petitions(student.id)

# Summary KPI Cards
pending_count = len([p for p in petitions if p["status"] == "PENDING"])
approved_count = len([p for p in petitions if p["status"] == "APPROVED"])
rejected_count = len([p for p in petitions if p["status"] == "REJECTED"])

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Pending Petitions", f"{pending_count}", "Awaiting Review", "warning", "⏳")
with c2:
    render_kpi_card("Approved Cases", f"{approved_count}", "Authorized", "success", "✅")
with c3:
    render_kpi_card("Rejected Cases", f"{rejected_count}", "Declined", "danger", "❌")
with c4:
    render_kpi_card("Active Student GPA", f"{student.gpa:.2f}", "Meets >3.0 Cap" if student.gpa >= 3.0 else "Below 3.0", "info", "⭐")

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# Interactive Review Cards
st.markdown("### ✍️ Pending Exception Petitions Review")

if pending_count == 0:
    st.info("🎉 All student petitions have been processed! No pending items in the review queue.")

for idx, pet in enumerate(petitions):
    if pet["status"] == "PENDING":
        st.markdown(
            f"""
            <div class="glass-card" style="border-left: 4px solid #f59e0b; margin-bottom: 14px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="color: #f8fafc; font-size: 1.05rem;">{pet['id']}: {pet['type']}</strong>
                    <span class="status-badge badge-progress">Awaiting Decision</span>
                </div>
                <div style="font-size: 0.88rem; color: #cbd5e1; margin: 6px 0;">
                    <strong>Student:</strong> {pet['student_name']} (ID: {pet['student_id']}) · <strong>GPA:</strong> {pet['gpa']:.2f} · <strong>Target:</strong> {pet['course']}
                </div>
                <div style="background: rgba(15, 23, 42, 0.6); padding: 8px 12px; border-radius: 6px; font-size: 0.85rem; color: #94a3b8; margin-bottom: 12px;">
                    <strong>Student Justification:</strong> {pet['justification']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        col_c, col_act1, col_act2 = st.columns([3, 1, 1])
        with col_c:
            comments = st.text_input("Faculty Reviewer Comments:", key=f"comment_{idx}", placeholder="e.g. Approved based on verified AP credit / prerequisite readiness.")
        with col_act1:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("✅ Approve", key=f"app_{idx}", type="primary", use_container_width=True):
                update_petition_status(pet["id"], "APPROVED", comments or "Approved by Department Chair.")
                st.success(f"Approved {pet['id']}!")
                st.rerun()
        with col_act2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("❌ Reject", key=f"rej_{idx}", use_container_width=True):
                update_petition_status(pet["id"], "REJECTED", comments or "Denied: Does not meet minimum GPA/prerequisite policy.")
                st.warning(f"Rejected {pet['id']}.")
                st.rerun()

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# Historical Decision Audit Table
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("### 📜 Faculty Decision & Waiver Audit Log")
st.caption("Permanent institutional record of all approved and rejected exception petitions:")

df_audit = pd.DataFrame(petitions)
st.dataframe(df_audit, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)
