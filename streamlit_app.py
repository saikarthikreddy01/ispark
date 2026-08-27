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


def main() -> None:
    st.set_page_config(page_title="Academic AI Advisor", page_icon="🎓", layout="wide")
    st.title("Academic AI Advisor")
    st.caption("LangGraph workflow | NetworkX knowledge graph | local policy retrieval")

    advisor = load_advisor()
    student = load_student()
    chat_tab, plan_tab, graph_tab = st.tabs(["Advisor chat", "Degree plan", "Knowledge graph"])

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
        completed = student.completed_course_ids
        credits = sum(
            int(course.get("credits", 0))
            for course in load_courses()
            if course["id"] in completed
        )
        first, second, third = st.columns(3)
        first.metric("Completed credits", credits)
        second.metric("Courses completed", len(completed))
        third.metric("Target graduation", student.expected_grad)
        st.subheader("Student profile")
        st.json({"name": student.name, "major": student.major, "gpa": student.gpa, "standing": student.standing})

    with graph_tab:
        render_graph(advisor)


if __name__ == "__main__":
    main()
