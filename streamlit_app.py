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
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@500;600;700&display=swap');
        :root { --ink: #173b40; --teal: #167c80; --mint: #dff4ed; --coral: #ef755e; --gold: #f2bd58; --paper: #f7f4ed; }
        .stApp { background: radial-gradient(circle at 85% 0%, #dff4ed 0, transparent 30%), var(--paper); color: var(--ink); }
        [data-testid="stSidebar"] { background: #173b40; }
        [data-testid="stSidebar"] * { color: #f7f4ed !important; }
        h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: var(--ink); letter-spacing: 0; }
        p, label, .stMarkdown { font-family: 'DM Sans', sans-serif; }
        .hero { padding: 1.2rem 1.4rem 1.4rem; border-bottom: 1px solid #c8d8d1; margin-bottom: 1rem; }
        .kicker { color: var(--coral); font-size: .76rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
        .hero h1 { font-size: clamp(2rem, 5vw, 3.6rem); line-height: 1; margin: .35rem 0 .6rem; }
        .hero p { max-width: 650px; color: #557174; font-size: 1.02rem; }
        .pipeline { display: flex; gap: .45rem; flex-wrap: wrap; margin: .8rem 0 1.4rem; }
        .node { background: white; border: 1px solid #c8d8d1; border-radius: 999px; padding: .38rem .72rem; font-size: .78rem; color: var(--ink); }
        .node.active { background: var(--teal); color: white; border-color: var(--teal); }
        .metric-card { background: white; border: 1px solid #c8d8d1; border-left: 4px solid var(--teal); padding: .85rem 1rem; min-height: 90px; }
        .metric-card small { color: #557174; text-transform: uppercase; letter-spacing: .08em; font-size: .68rem; }
        .metric-card strong { display: block; color: var(--ink); font: 700 1.55rem 'Space Grotesk', sans-serif; margin-top: .25rem; }
        </style>
        <div class="hero">
          <div class="kicker">Academic intelligence studio · C24 curriculum</div>
          <h1>Make the next semester make sense.</h1>
          <p>Grounded advising that connects policy, prerequisites, risk, and alternatives in one decision workspace.</p>
          <div class="pipeline"><span class="node active">Streamlit</span><span class="node">Orchestrator</span><span class="node">Retrieval</span><span class="node">Planner</span><span class="node">Rules</span><span class="node">Citations</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    advisor = load_advisor()
    student = load_student()
    with st.sidebar:
        st.markdown("## Student workspace")
        st.markdown(f"**{student.name}**")
        st.caption(f"{student.id} · {student.major}")
        st.divider()
        st.metric("Current GPA", f"{student.gpa:.2f}")
        st.metric("Completed courses", len(student.completed_course_ids))
        st.metric("Target graduation", student.expected_grad)
        st.divider()
        st.markdown("**Live architecture**")
        st.caption("NetworkX graph · local retrieval · LangGraph workflow")

    feasibility = advisor.schedule_analyzer.analyze_graduation_feasibility(student)
    summary_one, summary_two, summary_three, summary_four = st.columns(4)
    summary_one.markdown(f'<div class="metric-card"><small>Graph nodes</small><strong>{len(advisor.kg.get_all_courses())}</strong></div>', unsafe_allow_html=True)
    summary_two.markdown(f'<div class="metric-card"><small>Policy chunks</small><strong>{advisor.vector_store.count()}</strong></div>', unsafe_allow_html=True)
    summary_three.markdown(f'<div class="metric-card"><small>Risk score</small><strong>{feasibility.get("risk_score", 0):.2f}</strong></div>', unsafe_allow_html=True)
    summary_four.markdown(f'<div class="metric-card"><small>Credits remaining</small><strong>{feasibility.get("remaining_credits", 0)}</strong></div>', unsafe_allow_html=True)

    chat_tab, plan_tab, conflict_tab, substitution_tab, retrieval_tab, graph_tab = st.tabs([
        "Advisor chat", "Degree plan", "Conflict audit", "Substitutions", "Graph-RAG", "Knowledge graph"
    ])

    with chat_tab:
        st.subheader("Ask the academic system")
        st.caption("Every answer is routed through classification, retrieval, rules, and citation-aware explanation.")
        if "messages" not in st.session_state:
            st.session_state.messages = []
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        question = st.chat_input("Ask about prerequisites, risk, pathway, or substitutions")
        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.write(question)
            with st.chat_message("assistant"):
                with st.spinner("Running classify -> retrieve -> explain..."):
                    result = ask_advisor(question, student=student, advisor=advisor)
                response = result.get("response", "No response generated.")
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
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
