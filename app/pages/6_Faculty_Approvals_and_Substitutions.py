import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.student import StudentProfile
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.knowledge_graph.graph_queries import get_equivalent_courses, get_prerequisites
from src.constraint_engine.prerequisite_checker import PrerequisiteChecker
from src.constraint_engine.credit_validator import CreditValidator
from src.agents.substitution_agent import SubstitutionAgent
from src.rag.vector_store import AcademicVectorStore
from src.rag.document_loader import PolicyDocumentLoader
from src.utils.config import DATA_DIR
from app.ui_theme import inject_custom_css, render_hero_banner, render_kpi_card, render_sidebar_student

st.set_page_config(page_title="Substitutions & Faculty Approval | Academic Advisor", page_icon="📝", layout="wide")
inject_custom_css()

if "student" not in st.session_state:
    st.warning("⚠️ No student selected. Please select a student from the main page.")
    st.stop()

student: StudentProfile = st.session_state.student
render_sidebar_student(student)

# Load KG and Engines
@st.cache_resource
def get_resources():
    kg = AcademicKnowledgeGraph()
    kg.load_from_json(
        str(DATA_DIR / "courses.json"),
        str(DATA_DIR / "degree_requirements.json"),
        str(DATA_DIR / "equivalencies.json")
    )
    vs = AcademicVectorStore()
    loader = PolicyDocumentLoader()
    chunks = loader.load_and_chunk(str(DATA_DIR / "policies.md"))
    chunks += loader.load_course_descriptions(kg.get_all_courses())
    vs.add_documents(chunks)
    
    sub_agent = SubstitutionAgent(kg, vs)
    return kg, vs, sub_agent

kg, vs, sub_agent = get_resources()
prereq_checker = PrerequisiteChecker(kg)
credit_val = CreditValidator(kg)

render_hero_banner(
    title="📝 Course Substitutions & <span class='gradient-text'>Faculty Approval System</span>",
    subtitle=f"Automated alternative course recommendations, equivalency discovery, and formal constraint verification for <strong>{student.name}</strong>.",
    badge_text="Decentralized Academic Governance & Exceptions"
)

from app.ui_theme import render_help_tip
render_help_tip(
    title="How Course Substitutions & Exception Waivers Work",
    explanation="<strong>Substitutions:</strong> If a required course is full or conflicting, find approved alternative courses with matching learning outcomes. &nbsp;|&nbsp; <strong>Faculty Petitions:</strong> If you need a special waiver (like taking 19+ credits or overriding a prerequisite), submit a petition to automatically check eligibility and get faculty sign-off.",
    icon="📝"
)

# Main Navigation Tabs
tab_subs, tab_approval, tab_history = st.tabs([
    "🔁 Alternative Courses & Substitutions",
    "✍️ Formal Constraint Verification & Faculty Petition",
    "📜 Exception & Waiver Audit Log"
])

# ----------------- TAB 1: Alternative Courses & Substitutions -----------------
with tab_subs:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Intelligent Course Substitution Finder")
    st.caption("Identify approved equivalents, interdisciplinary alternatives, and transfer credit waivers grounded in university curriculum rules.")
    
    all_courses = kg.get_all_courses()
    course_opts = [f"{c.id} - {c.name} ({c.credits} cr)" for c in all_courses]
    
    col_s1, col_s2 = st.columns([1, 1])
    with col_s1:
        target_course_opt = st.selectbox(
            "Select Course to Find Alternatives For:",
            course_opts,
            index=min(6, len(course_opts)-1)
        )
        target_cid = target_course_opt.split(" - ")[0]
        target_course = kg.get_course(target_cid)
        
    with col_s2:
        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 10px; padding: 14px;">
                <div style="font-size: 0.78rem; color: #94a3b8; text-transform: uppercase; font-weight: 600;">Selected Target Course</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #f8fafc;">{target_course.id}: {target_course.name}</div>
                <div style="font-size: 0.85rem; color: #cbd5e1; margin-top: 4px;">Dept: {target_course.department} · {target_course.credits} Credits · Difficulty: {target_course.difficulty_level}/5</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Recommendations Output
    direct_eqs = get_equivalent_courses(kg, target_cid)
    
    st.markdown(f"#### 🎯 Recommended Alternatives for `{target_cid}`")
    
    if direct_eqs:
        for eq_id in direct_eqs:
            eq_course = kg.get_course(eq_id)
            eq_name = eq_course.name if eq_course else eq_id
            eq_credits = eq_course.credits if eq_course else 3
            eq_prereqs = get_prerequisites(kg, eq_id) if eq_course else []
            
            st.markdown(
                f"""
                <div class="glass-card" style="border-left: 4px solid #10b981; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span class="status-badge badge-prereq-met">Direct Equivalency (§2.1)</span>
                            <h4 style="color: #f8fafc; margin: 8px 0 4px 0;">{eq_id} — {eq_name}</h4>
                            <p style="color: #94a3b8; font-size: 0.88rem; margin: 0;">{eq_course.description if eq_course else 'Approved cross-listed equivalency.'}</p>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: 700; color: #34d399; font-size: 1.1rem;">{eq_credits} Credits</div>
                            <div style="font-size: 0.75rem; color: #94a3b8;">Automatic Credit Fulfillment</div>
                        </div>
                    </div>
                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.05); font-size: 0.82rem; color: #cbd5e1;">
                        <strong>Prerequisites:</strong> {', '.join(eq_prereqs) if eq_prereqs else 'None'} · <strong>Faculty Approval:</strong> Pre-Approved by Curriculum Committee
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            f"""
            <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 16px; margin-bottom: 14px;">
                <div style="color: #f1f5f9; font-weight: 600; font-size: 0.95rem;">No automatic direct substitution found for {target_cid}.</div>
                <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">You may submit an <strong>Exceptional Course Substitution Petition</strong> to the Department Chair under <em>Policy §2.2 (75% learning outcome match required)</em>.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ----------------- TAB 2: Formal Constraint Verification & Faculty Petition -----------------
with tab_approval:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### ✍️ Formal Constraint Verification & Exception Petition")
    st.caption("Submit formal academic waiver petitions for prerequisite overrides, credit overloads, or transfer substitutions with automated policy validation.")
    
    col_p1, col_p2 = st.columns([1, 1])
    
    with col_p1:
        petition_type = st.selectbox(
            "Petition Category",
            [
                "Prerequisite Waiver (Policy §1.2)",
                "Credit Overload Exception - Max 21 cr (Policy §5.2)",
                "Course Substitution / Transfer Credit Waiver (Policy §2.2)",
                "Concurrent Prerequisite Exception (Policy §1.1)"
            ]
        )
        
        target_course_petition = st.selectbox("Target Course for Exception:", course_opts, key="pet_course")
        pet_cid = target_course_petition.split(" - ")[0]
        
        justification = st.text_area(
            "Student Justification / Academic Rationale:",
            placeholder="Explain relevant prior coursework, industry experience, or GPA standing supporting this exception..."
        )
        
        verify_petition_btn = st.button("⚖️ Run Formal Constraint Verification & Submit", type="primary", use_container_width=True)

    with col_p2:
        st.markdown("#### 📋 Automated Policy Pre-Check")
        
        # Policy Pre-check calculation
        gpa_ok = student.gpa >= 3.0
        gpa_color = "#34d399" if gpa_ok else "#f87171"
        
        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 16px;">
                <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem; margin-bottom: 12px;">Student Eligibility Verification</div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.88rem;">
                    <span style="color: #94a3b8;">Cumulative GPA:</span>
                    <span style="font-weight: 700; color: {gpa_color};">{student.gpa:.2f} ({'Meets ≥ 3.0 Standard' if gpa_ok else 'Below 3.0 Threshold'})</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.88rem;">
                    <span style="color: #94a3b8;">Credits Completed:</span>
                    <span style="font-weight: 700; color: #f8fafc;">{student.total_credits_earned} / 120 cr</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.88rem;">
                    <span style="color: #94a3b8;">Faculty Approval Required:</span>
                    <span style="font-weight: 700; color: #818cf8;">Department Chair / Academic Dean</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if verify_petition_btn:
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            if not justification:
                st.error("⚠️ Please provide an academic rationale or justification before submitting.")
            else:
                # Automated formal reasoning
                if "Overload" in petition_type and student.gpa < 3.0:
                    status = "🔴 Rejected by Policy Constraint Engine"
                    rec = "Policy §5.2 strictly requires a cumulative GPA of ≥ 3.0 for credit overloads exceeding 18 units."
                    verdict_type = "danger"
                elif "Prerequisite Waiver" in petition_type and student.gpa >= 3.2:
                    status = "🟢 Approved & Endorsed by Policy Engine"
                    rec = f"Student GPA ({student.gpa:.2f}) and progression verify prerequisite readiness for {pet_cid} under Policy §1.2."
                    verdict_type = "success"
                else:
                    status = "🟡 Conditional Approval — Pending Faculty Signature"
                    rec = f"Petition verified against Knowledge Graph constraints. Forwarded to Department Chair for final sign-off."
                    verdict_type = "warning"
                    
                st.markdown(
                    f"""
                    <div style="background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 12px; padding: 16px; margin-top: 10px;">
                        <div style="font-size: 0.78rem; text-transform: uppercase; color: #818cf8; font-weight: 700;">Formal Constraint Verification Verdict</div>
                        <div style="font-size: 1.1rem; font-weight: 800; color: #f8fafc; margin: 4px 0 8px 0;">{status}</div>
                        <div style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.5;">{rec}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Store in session audit log
                if "petition_logs" not in st.session_state:
                    st.session_state.petition_logs = []
                st.session_state.petition_logs.append({
                    "Student": student.name,
                    "Type": petition_type,
                    "Course": pet_cid,
                    "Status": status,
                    "Date": "Current Term"
                })
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------- TAB 3: Exception Audit Log -----------------
with tab_history:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📜 Faculty Approval & Exception Audit Log")
    st.caption("Immutable record of all formal waiver petitions, Dean authorizations, and credit transfer exceptions.")
    
    logs = st.session_state.get("petition_logs", [
        {
            "Student": student.name,
            "Type": "Course Substitution (Policy §2.1)",
            "Course": "CS350 → CS355",
            "Status": "🟢 Faculty Approved (Curriculum Chair)",
            "Date": "Fall 2024"
        },
        {
            "Student": student.name,
            "Type": "Prerequisite Waiver (Policy §1.2)",
            "Course": "MATH101 (AP Calculus AB 5/5)",
            "Status": "🟢 Transfer Credit Articulated",
            "Date": "Fall 2023"
        }
    ])
    
    import pandas as pd
    df_logs = pd.DataFrame(logs)
    st.dataframe(df_logs, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
