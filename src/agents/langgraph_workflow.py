"""LangGraph workflow facade for the academic advisor demo."""

from typing import Any

from src.agents.orchestrator import AcademicAdvisor
from src.agents.state import AdvisorState

try:
    from langgraph.graph import END, StateGraph
except ImportError:  # Keep the core usable when optional orchestration deps are absent.
    END = "__end__"
    StateGraph = None


def build_advisor_graph(advisor: AcademicAdvisor | None = None):
    """Build a small, inspectable classify -> retrieve -> explain workflow."""
    advisor = advisor or AcademicAdvisor()

    def classify(state: AdvisorState) -> dict[str, Any]:
        query = str(state.get("query", ""))
        return {"query_type": advisor.classify_query(query)}

    def retrieve(state: AdvisorState) -> dict[str, Any]:
        query = str(state.get("query", ""))
        retrieval = advisor.retriever.retrieve(query, student=state.get("student"), top_k=4)
        return {
            "retrieved_context": "\n\n".join(
                part for part in (
                    retrieval.graph_context,
                    retrieval.policy_context,
                    retrieval.course_context,
                ) if part
            ),
            "citations": retrieval.citations,
        }

    def explain(state: AdvisorState) -> dict[str, Any]:
        result = advisor.chat_sync(str(state.get("query", "")), state.get("student"))
        return {
            "response": result.get("response", ""),
            "citations": result.get("citations", state.get("citations", [])),
            "conflicts": result.get("conflicts", []),
        }

    if StateGraph is None:
        class LocalWorkflow:
            def invoke(self, state: AdvisorState) -> AdvisorState:
                for step in (classify, retrieve, explain):
                    state.update(step(state))
                return state

        return LocalWorkflow()

    workflow = StateGraph(AdvisorState)
    workflow.add_node("classify", classify)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("explain", explain)
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "retrieve")
    workflow.add_edge("retrieve", "explain")
    workflow.add_edge("explain", END)
    return workflow.compile()


def ask_advisor(query: str, student: Any = None, advisor: AcademicAdvisor | None = None) -> AdvisorState:
    """Run the workflow and return its state for UI or API consumers."""
    graph = build_advisor_graph(advisor)
    return graph.invoke({"query": query, "student": student})
