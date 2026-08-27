"""Hackathon Streamlit frontend for the Academic AI Advisor."""

import html
import json
from pathlib import Path

import streamlit as st

from src.agents.langgraph_workflow import ask_advisor
from src.agents.orchestrator import AcademicAdvisor
from src.models.student import Student

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"


@st.cache_resource
def load_advisor() -> AcademicAdvisor:
    return AcademicAdvisor()


@st.cache_data
def load_courses() -> list[dict]:
    with open(DATA_DIR / "courses.json", encoding="utf-8") as source:
        return json.load(source)


def load_student() -> Student:
    return Student(
        id="241FA04077",
        name="Sai Karthik Reddy",
        major="Computer Science & Engineering",
        gpa=3.82,
        completed_courses=["24CS101", "24MA101", "24PH101"],
        expected_grad="May 2028",
    )


def render_graph(advisor: AcademicAdvisor) -> None:
    courses = load_courses()
    lines = ["digraph {", 'rankdir=LR; bgcolor="transparent";']
    for course in courses:
        node_id = course["id"].replace("-", "_")
        label = html.escape(f"{course['id']}\\n{course.get('name', 'Course')}")
        lines.append(f'{node_id} [label="{label}"];')
        prereqs = course.get("prereqs", course.get("prerequisites", []))
        if not prereqs:
            prereqs = [
                prerequisite.get("course_id")
                for group in course.get("prerequisite_groups", [])
                for prerequisite in group.get("prerequisites", [])
            ]
        for prereq in prereqs:
            if not prereq:
                continue
            prereq_id = str(prereq).replace("-", "_")
            lines.append(f'{prereq_id} -> {node_id};')
    lines.append("}")
    st.graphviz_chart("\n".join(lines), use_container_width=True)
    st.caption(f"{len(courses)} course nodes loaded from the NetworkX knowledge graph.")


def course_prerequisites(course: dict) -> list[str]:
    prerequisites = course.get("prerequisites", course.get("prereqs", []))
    if prerequisites:
        return [str(item) for item in prerequisites]
    return [
        prerequisite.get("course_id")
        for group in course.get("prerequisite_groups", [])
        for prerequisite in group.get("prerequisites", [])
        if prerequisite.get("course_id")
    ]


def render_plan(advisor: AcademicAdvisor, student: Student) -> None:
    courses = {course.id: course for course in advisor.kg.get_all_courses()}
    required = advisor.kg.degree_requirements.get("required_courses", list(courses))
    completed = set(student.completed_course_ids)
    plans = []

    for term_number in range(1, 9):
        term_name = "FALL" if term_number % 2 else "SPRING"
        term_courses = []
        credits = 0
        candidates = []
        for course_id in required:
            course = courses.get(course_id)
            if not course or course_id in completed:
                continue
            offered = {str(value).upper() for value in course.offered_semesters}
            eligible, _ = advisor.prereq_checker.check_prerequisites(course_id, completed)
            if eligible and (not offered or term_name in offered):
                candidates.append(course)

        for course in sorted(candidates, key=lambda item: (item.sem or 99, item.difficulty_level, item.id)):
            if credits + course.credits > student.max_credits_per_semester:
                continue
            term_courses.append(course)
            credits += course.credits
            completed.add(course.id)

        plans.append((f"Term {term_number} · {term_name}", term_courses, credits))
        if not term_courses:
            break

    first, second, third = st.columns(3)
    first.metric("Completed credits", sum(courses[item].credits for item in student.completed_course_ids if item in courses))
    second.metric("Planned credits", sum(credits for _, _, credits in plans))
    third.metric("Credit cap", f"{student.max_credits_per_semester}/term")
    for term_name, term_courses, credits in plans:
        with st.expander(f"{term_name} · {credits} credits", expanded=True):
            if term_courses:
                for course in term_courses:
                    st.write(f"**{course.id}** · {course.name} · {course.credits} credits")
            else:
                st.info("No eligible courses under the current prerequisite rules.")


def render_conflicts(advisor: AcademicAdvisor, student: Student) -> None:
    course_ids = [course.id for course in advisor.kg.get_all_courses()]
    selected = st.multiselect("Courses to audit", course_ids, default=course_ids[:3])
    completed = student.completed_course_ids
    conflicts = []
    for course_id in selected:
        if course_id in completed:
            conflicts.append((course_id, "Already completed"))
            continue
        eligible, missing = advisor.prereq_checker.check_prerequisites(course_id, completed)
        if not eligible:
            conflicts.append((course_id, f"Missing prerequisites: {', '.join(missing)}"))

    if conflicts:
        for course_id, message in conflicts:
            st.warning(f"{course_id}: {message}")
    else:
        st.success("No conflicts detected for the selected courses.")


def render_substitutions(advisor: AcademicAdvisor) -> None:
    available = sorted({item.course_id for item in advisor.kg.equivalencies})
    if not available:
        st.info("No approved equivalencies are loaded.")
        return
    course_id = st.selectbox("Course requiring an alternative", available)
    matches = [item for item in advisor.kg.equivalencies if item.course_id == course_id]
    for match in matches:
        substitute = advisor.kg.get_course(match.equivalent_course_id)
        name = substitute.name if substitute else "Unknown course"
        st.success(f"{match.equivalent_course_id} · {name}")
        if match.notes:
            st.caption(match.notes)


def render_retrieval(advisor: AcademicAdvisor, student: Student) -> None:
    query = st.text_input("Search policies and course relationships", "prerequisite waiver")
    if not query:
        return
    result = advisor.retriever.retrieve(query, student=student, top_k=5)
    left, right = st.columns(2)
    with left:
        st.subheader("Graph context")
        st.write(result.graph_context or "No course references found.")
    with right:
        st.subheader("Policy context")
        st.write(result.policy_context or "No matching policy sections found.")
    if result.citations:
        with st.expander("Grounding citations"):
            for citation in result.citations:
                st.write(citation)


def main() -> None:
    st.set_page_config(page_title="Academic AI Advisor", page_icon="🎓", layout="wide")
    st.title("Academic AI Advisor")
    st.caption("LangGraph workflow | NetworkX knowledge graph | local policy retrieval")

    advisor = load_advisor()
    student = load_student()
    chat_tab, plan_tab, conflict_tab, substitution_tab, retrieval_tab, graph_tab = st.tabs([
        "Advisor chat", "Degree plan", "Conflict audit", "Substitutions", "Graph-RAG", "Knowledge graph"
    ])

    with chat_tab:
        question = st.chat_input("Ask about prerequisites, risk, pathway, or substitutions")
        if question:
            with st.chat_message("user"):
                st.write(question)
            with st.chat_message("assistant"):
                with st.spinner("Running classify -> retrieve -> explain..."):
                    result = ask_advisor(question, student=student, advisor=advisor)
                st.markdown(result.get("response", "No response generated."))
                if result.get("citations"):
                    with st.expander("Citations"):
                        for citation in result["citations"]:
                            st.write(citation)
                if result.get("conflicts"):
                    st.warning("\n".join(result["conflicts"]))

    with plan_tab:
        st.subheader("Greedy prerequisite-aware pathway")
        render_plan(advisor, student)

    with conflict_tab:
        st.subheader("Constraint and prerequisite audit")
        render_conflicts(advisor, student)

    with substitution_tab:
        st.subheader("Approved course equivalencies")
        render_substitutions(advisor)

    with retrieval_tab:
        st.subheader("Grounded retrieval inspector")
        render_retrieval(advisor, student)

    with graph_tab:
        render_graph(advisor)


if __name__ == "__main__":
    main()
