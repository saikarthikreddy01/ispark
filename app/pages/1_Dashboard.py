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

st.set_page_config(page_title="Dashboard | Academic Advisor", page_icon="📊", layout="wide")

if "student" not in st.session_state:
    st.warning("⚠️ No student selected. Please select a student from the main page.")
    st.stop()

student: StudentProfile = st.session_state.student

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
st.title("📊 Student Academic Dashboard")
st.markdown(f"Real-time degree audit, constraint verification, and pathway analysis for **{student.name}**.")

# Quick KPI Metrics
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Credits", f"{student.total_credits_earned} / 120", delta=f"{120 - student.total_credits_earned} remaining", delta_color="inverse")
with col2:
    st.metric("Cumulative GPA", f"{student.gpa:.2f}", delta="Good Standing" if student.gpa >= 2.0 else "Probation Risk", delta_color="normal" if student.gpa >= 2.0 else "inverse")
with col3:
    st.metric("Current Standing", f"Year {student.current_year}", help=f"Enrolled in {student.enrollment_year}")
with col4:
    st.metric("Semester", student.current_semester.value)
with col5:
    st.metric("Completed Courses", len(student.completed_course_ids))

st.markdown("---")

# Progress & Category Breakdown
col_prog, col_risk = st.columns([3, 2])

with col_prog:
    st.subheader("🎓 Degree Requirements Progress")
    
    # Overall Progress
    overall_pct = min(student.total_credits_earned / 120.0, 1.0)
    st.write(f"**Overall Degree Completion: {int(overall_pct * 100)}%**")
    st.progress(overall_pct)
    
    # Category breakdown
    st.markdown("##### Category Breakdown")
    cat_reqs = credit_val.get_remaining_requirements(student.completed_course_ids)
    
    for cat_name, info in cat_reqs.items():
        req = info.get("required", 0)
        earned = info.get("earned", 0)
        pct = min(earned / req, 1.0) if req > 0 else 1.0
        c1, c2 = st.columns([3, 1])
        with c1:
            st.caption(f"**{cat_name}** ({info.get('description', '')})")
            st.progress(pct)
        with c2:
            st.caption(f"**{earned}/{req}** cr ({int(pct*100)}%)")

with col_risk:
    st.subheader("⚠️ Graduation Risk & Feasibility")
    feasibility = schedule_analyzer.analyze_graduation_feasibility(student)
    
    risk_score = feasibility.get("risk_score", 0.0)
    if risk_score < 0.3:
        st.success(f"🟢 **Low Risk (Score: {risk_score:.2f})** — On track for timely graduation.")
    elif risk_score < 0.6:
        st.warning(f"🟡 **Moderate Risk (Score: {risk_score:.2f})** — Bottlenecks or prerequisite chains require attention.")
    else:
        st.error(f"🔴 **High Risk (Score: {risk_score:.2f})** — Prerequisite delays or missing key courses detected.")
        
    st.markdown(f"- **Earliest Possible Graduation:** {feasibility.get('semesters_remaining', 0)} terms remaining")
    st.markdown(f"- **Remaining Degree Credits:** {feasibility.get('remaining_credits', 0)} credits")
    
    bottlenecks = feasibility.get("bottleneck_courses", [])
    if bottlenecks:
        st.markdown("**Critical Bottleneck Courses to Take ASAP:**")
        for b in bottlenecks:
            course = kg.get_course(b)
            cname = course.name if course else b
            st.error(f"📌 **{b}** - {cname}")
    else:
        st.success("✅ No critical bottleneck courses blocking your path!")
        
    if student.career_goals:
        st.markdown("##### 🎯 Career Aspirations")
        for goal in student.career_goals:
            st.markdown(f"- 🚀 {goal}")

st.markdown("---")

# Completed Courses & Remaining Requirements
tab_completed, tab_remaining = st.tabs(["📚 Completed Courses & History", "🎯 Remaining Requirements & Readiness"])

with tab_completed:
    if student.completed_courses:
        records = []
        for c in student.completed_courses:
            course = kg.get_course(c.course_id)
            cname = course.name if course else "External / Transfer"
            dept = course.department if course else "N/A"
            records.append({
                "Course ID": c.course_id,
                "Course Name": cname,
                "Department": dept,
                "Credits": c.credits,
                "Grade": c.grade,
                "Term Taken": f"{c.semester_taken.value} {c.year}",
                "Type": "Transfer" if c.is_transfer else "Institutional"
            })
        df = pd.DataFrame(records)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No courses completed yet (Freshman enrollment).")

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
                "Course Name": cname,
                "Credits": course.credits if course else 3,
                "Offered": ", ".join([s.value for s in course.offered_semesters]) if course else "All",
                "Prerequisites": ", ".join(prereqs) if prereqs else "None",
                "Status": "🟢 Ready to Enroll" if is_ready else "🔒 Prerequisites Incomplete"
            })
        df_rem = pd.DataFrame(records)
        st.dataframe(df_rem, use_container_width=True, hide_index=True)
    else:
        st.success("🎉 All mandatory core requirements satisfied! Complete your electives to graduate.")
