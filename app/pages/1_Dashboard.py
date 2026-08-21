import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.student import StudentProfile
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.constraint_engine.credit_validator import CreditValidator
from src.constraint_engine.schedule_feasibility import ScheduleAnalyzer
from src.utils.config import DATA_DIR
from app.ui_theme import inject_custom_css, render_hero_banner, render_kpi_card, render_sidebar_student

st.set_page_config(page_title="Dashboard | Academic Advisor", page_icon="📊", layout="wide")
inject_custom_css()

if "student" not in st.session_state:
    st.warning("⚠️ No student selected. Please select a student from the main page.")
    st.stop()

student: StudentProfile = st.session_state.student
render_sidebar_student(student)

# Load KG
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
credit_val = CreditValidator(kg)
schedule_analyzer = ScheduleAnalyzer(kg)

# Page Header
render_hero_banner(
    title=f"📊 Degree Audit & Academic Profile: <span class='gradient-text'>{student.name}</span>",
    subtitle=f"Major: <strong>{student.major}</strong> · Catalog Year: <strong>{student.enrollment_year}</strong> · Term: <strong>{student.current_semester.value} (Year {student.current_year})</strong>",
    badge_text="Real-Time Degree Audit Engine"
)

# KPI Cards
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_kpi_card(
        title="Credits Earned",
        value=f"{student.total_credits_earned} <span style='font-size: 0.95rem; color:#94a3b8;'>/ 120</span>",
        delta=f"{max(0, 120 - student.total_credits_earned)} remaining",
        delta_type="info",
        icon="🎓"
    )
with c2:
    render_kpi_card(
        title="Cumulative GPA",
        value=f"{student.gpa:.2f}",
        delta="Good Standing" if student.gpa >= 2.0 else "Probation Risk",
        delta_type="success" if student.gpa >= 2.0 else "danger",
        icon="⭐"
    )
with c3:
    render_kpi_card(
        title="Current Standing",
        value=f"Year {student.current_year}",
        delta=f"Enrolled {student.enrollment_year}",
        delta_type="info",
        icon="🏛️"
    )
with c4:
    render_kpi_card(
        title="Current Term",
        value=student.current_semester.value,
        delta="Active Registration",
        delta_type="success",
        icon="🗓️"
    )
with c5:
    render_kpi_card(
        title="Completed Courses",
        value=str(len(student.completed_course_ids)),
        delta="Transcript Verified",
        delta_type="success",
        icon="✅"
    )

from app.ui_theme import render_help_tip
render_help_tip(
    title="Understanding Your Degree Audit & Risk Assessment",
    explanation="<strong>Overall Completion:</strong> Measures progress toward the required 120 credit units. &nbsp;|&nbsp; <strong>Bottleneck Courses:</strong> Essential foundational courses (like Data Structures or Calculus) that must be passed early because multiple upper-level courses depend on them.",
    icon="💡"
)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# Main Grid: Progress & Risk
col_prog, col_risk = st.columns([3, 2])

with col_prog:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🎓 Degree Requirements Progress")
    
    # Overall Progress
    overall_pct = min(student.total_credits_earned / 120.0, 1.0)
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;">
            <span style="font-weight: 700; color: #f8fafc; font-size: 1.05rem;">Overall Degree Completion</span>
            <span style="font-size: 1.25rem; font-weight: 800; color: #818cf8;">{int(overall_pct * 100)}%</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.progress(overall_pct)
    
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("##### 📑 Requirement Category Breakdown")
    cat_reqs = credit_val.get_remaining_requirements(student.completed_course_ids)
    
    for cat_name, info in cat_reqs.items():
        req = info.get("required", 0)
        earned = info.get("earned", 0)
        pct = min(earned / req, 1.0) if req > 0 else 1.0
        
        status_color = "#34d399" if pct >= 1.0 else ("#818cf8" if pct > 0.4 else "#fbbf24")
        
        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 12px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-weight: 600; color: #f1f5f9; font-size: 0.9rem;">{cat_name} <span style="font-size: 0.75rem; color: #94a3b8; font-weight: 400;">({info.get('description', '')})</span></span>
                    <span style="font-weight: 700; color: {status_color}; font-size: 0.85rem;">{earned}/{req} cr ({int(pct*100)}%)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.progress(pct)
    st.markdown('</div>', unsafe_allow_html=True)

with col_risk:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### ⚠️ Graduation Feasibility & Risks")
    feasibility = schedule_analyzer.analyze_graduation_feasibility(student)
    
    risk_score = feasibility.get("risk_score", 0.0)
    if risk_score < 0.3:
        st.markdown(
            f"""
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 14px; margin-bottom: 16px;">
                <div style="font-weight: 700; color: #34d399; font-size: 1rem; margin-bottom: 4px;">🟢 Low Risk (Score: {risk_score:.2f})</div>
                <div style="font-size: 0.85rem; color: #a7f3d0;">Student is on track for on-time graduation. Prerequisite paths are healthy.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif risk_score < 0.6:
        st.markdown(
            f"""
            <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 12px; padding: 14px; margin-bottom: 16px;">
                <div style="font-weight: 700; color: #fbbf24; font-size: 1rem; margin-bottom: 4px;">🟡 Moderate Risk (Score: {risk_score:.2f})</div>
                <div style="font-size: 0.85rem; color: #fde68a;">Curriculum bottlenecks or sequential prerequisite chains require attention.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 14px; margin-bottom: 16px;">
                <div style="font-weight: 700; color: #f87171; font-size: 1rem; margin-bottom: 4px;">🔴 High Risk (Score: {risk_score:.2f})</div>
                <div style="font-size: 0.85rem; color: #fecaca;">Significant prerequisite delays or unmet core foundational courses detected.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.markdown(
        f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 16px;">
            <div style="background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 10px; text-align: center;">
                <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase;">Terms Remaining</div>
                <div style="font-size: 1.3rem; font-weight: 800; color: #f8fafc;">{feasibility.get('semesters_remaining', 0)} Semesters</div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 10px; text-align: center;">
                <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase;">Credits Needed</div>
                <div style="font-size: 1.3rem; font-weight: 800; color: #818cf8;">{feasibility.get('remaining_credits', 0)} cr</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    bottlenecks = feasibility.get("bottleneck_courses", [])
    if bottlenecks:
        st.markdown("##### ⚡ Urgent Bottleneck Courses")
        for b in bottlenecks:
            course = kg.get_course(b)
            cname = course.name if course else b
            st.markdown(
                f"""
                <div style="background: rgba(239, 68, 68, 0.1); border-left: 3px solid #ef4444; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px; font-size: 0.88rem;">
                    <span style="font-weight: 700; color: #fca5a5;">{b}:</span> <span style="color: #f1f5f9;">{cname}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.success("✅ No critical prerequisite bottlenecks blocking your pathway!")
        
    if student.career_goals:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("##### 🎯 Target Career Aspirations")
        for goal in student.career_goals:
            st.markdown(f"<span style='display:inline-block; margin: 3px; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); padding: 4px 10px; border-radius: 12px; font-size: 0.82rem; color: #c7d2fe;'>🚀 {goal}</span>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# Completed Courses & Remaining Requirements
tab_completed, tab_remaining = st.tabs(["📚 Completed Courses Transcript", "🎯 Remaining Degree Requirements & Eligibility"])

with tab_completed:
    if student.completed_courses:
        records = []
        for c in student.completed_courses:
            course = kg.get_course(c.course_id)
            cname = course.name if course else "External / Transfer"
            dept = course.department if course else "N/A"
            records.append({
                "Course ID": c.course_id,
                "Course Title": cname,
                "Dept": dept,
                "Credits": c.credits,
                "Grade": c.grade,
                "Term Taken": f"{c.semester_taken.value} {c.year}",
                "Enrollment Type": "Transfer Credit" if c.is_transfer else "Institutional"
            })
        df = pd.DataFrame(records)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No courses completed yet (Freshman enrollment profile).")

with tab_remaining:
    required_courses = kg.degree_requirements.get("required_courses", [])
    remaining_reqs = [cid for cid in required_courses if cid not in student.completed_course_ids]
    
    if remaining_reqs:
        from src.knowledge_graph.graph_queries import get_available_courses, get_prerequisites
        available_now = set(get_available_courses(kg, student.completed_course_ids))
        
        records = []
        for cid in remaining_reqs:
            course = kg.get_course(cid)
            cname = course.name if course else cid
            prereqs = get_prerequisites(kg, cid)
            is_ready = cid in available_now
            records.append({
                "Course ID": cid,
                "Course Title": cname,
                "Credits": course.credits if course else 3,
                "Offered Terms": ", ".join([s.value for s in course.offered_semesters]) if course else "All",
                "Prerequisites": ", ".join(prereqs) if prereqs else "None",
                "Enrollment Status": "🟢 Ready to Enroll" if is_ready else "🔒 Prerequisites Incomplete"
            })
        df_rem = pd.DataFrame(records)
        st.dataframe(df_rem, use_container_width=True, hide_index=True)
    else:
        st.success("🎉 All mandatory core requirements satisfied! Complete your electives to graduate.")
