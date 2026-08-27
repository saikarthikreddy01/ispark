"""Agentic academic-advisor orchestration.

The workflow separates retrieval, deterministic constraints, pathway planning,
risk analysis, substitution review, and answer synthesis. LLM output never
becomes the source of truth for hard academic constraints.
"""

import os
from src.agents.state import AdvisorState
from src.agents.conflict_agent import ConflictAgent
from src.agents.pathway_agent import PathwayAgent
from src.agents.risk_agent import RiskAgent
from src.agents.substitution_agent import SubstitutionAgent
from src.utils.config import GEMINI_API_KEY, OPENAI_API_KEY, MODEL_NAME, DATA_DIR
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.rag.vector_store import AcademicVectorStore
from src.rag.document_loader import PolicyDocumentLoader
from src.rag.graph_retriever import GraphRAGRetriever
from src.constraint_engine.prerequisite_checker import PrerequisiteChecker
from src.constraint_engine.schedule_feasibility import ScheduleAnalyzer
from src.constraint_engine.credit_validator import CreditValidator

try:
    from langgraph.graph import StateGraph, START, END
except Exception:  # pragma: no cover - deterministic fallback remains available
    StateGraph = None
    START = END = None

try:
    import google.genai as genai
except ImportError:
    genai = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class AcademicAdvisor:
    def __init__(self, kg=None, vector_store=None, llm=None):
        self.kg = kg or AcademicKnowledgeGraph()
        if kg is None:
            self.kg.load_from_json(
                str(DATA_DIR / "courses.json"),
                str(DATA_DIR / "degree_requirements.json"),
                str(DATA_DIR / "equivalencies.json"),
            )

        self.vector_store = vector_store or AcademicVectorStore()
        if vector_store is None:
            loader = PolicyDocumentLoader()
            chunks = loader.load_and_chunk(str(DATA_DIR / "policies.md"))
            chunks += loader.load_course_descriptions(self.kg.get_all_courses())
            self.vector_store.add_documents(chunks)

        self.retriever = GraphRAGRetriever(self.kg, self.vector_store)
        self.prereq_checker = PrerequisiteChecker(self.kg)
        self.credit_validator = CreditValidator(self.kg)
        self.schedule_analyzer = ScheduleAnalyzer(self.kg)

        self.conflict_agent = ConflictAgent(self.kg, self.prereq_checker, self.credit_validator)
        self.pathway_agent = PathwayAgent(self.kg, self.prereq_checker, self.credit_validator, self.schedule_analyzer)
        self.risk_agent = RiskAgent(self.kg, self.schedule_analyzer, self.credit_validator)
        self.substitution_agent = SubstitutionAgent(self.kg, self.retriever)
        self.llm = llm

        self.openai_client = None
        key = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)
        if key and OpenAI:
            try:
                self.openai_client = OpenAI(api_key=key)
            except Exception:
                pass

        self.gemini_client = None
        key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
        if key and genai and not self.openai_client:
            try:
                self.gemini_client = genai.Client(api_key=key)
            except Exception:
                pass

        self.workflow = self._build_workflow()

    def classify_query(self, query: str) -> str:
        q = query.lower()
        if any(k in q for k in ["substitute", "instead of", "equivalent", "alternative"]):
            return "substitution"
        if any(k in q for k in ["pathway", "plan", "roadmap", "schedule", "semesters", "graduate"]):
            return "pathway"
        if any(k in q for k in ["risk", "delay", "bottleneck", "standing"]):
            return "risk"
        if any(k in q for k in ["policy", "waiver", "transfer", "repeat", "credit limit"]):
            return "policy"
        if any(k in q for k in ["prereq", "require", "eligible", "can i take", "enroll"]):
            return "prerequisite"
        return "general"

    # ---------------- LangGraph nodes ----------------
    def _classify_node(self, state: AdvisorState) -> AdvisorState:
        return {"query_type": self.classify_query(state.get("query", ""))}

    def _retrieve_node(self, state: AdvisorState) -> AdvisorState:
        retrieval = self.retriever.retrieve(state.get("query", ""), student=state.get("student"), top_k=5)
        context = "\n\n".join(x for x in [retrieval.graph_context, retrieval.policy_context, retrieval.course_context] if x)
        return {
            "retrieval": retrieval,
            "retrieved_context": context,
            "citations": retrieval.citations,
        }

    def _conflict_node(self, state: AdvisorState) -> AdvisorState:
        return self.conflict_agent.process(state)

    def _pathway_node(self, state: AdvisorState) -> AdvisorState:
        if state.get("query_type") == "pathway":
            return self.pathway_agent.process(state)
        return {}

    def _risk_node(self, state: AdvisorState) -> AdvisorState:
        if state.get("student") and state.get("query_type") in {"risk", "pathway"}:
            return self.risk_agent.process(state)
        return {}

    def _substitution_node(self, state: AdvisorState) -> AdvisorState:
        if state.get("query_type") == "substitution":
            return self.substitution_agent.process(state)
        return {}

    def _synthesis_node(self, state: AdvisorState) -> AdvisorState:
        response = self._synthesize(state)
        return {"final_response": response}

    def _build_workflow(self):
        if StateGraph is None:
            return None
        graph = StateGraph(AdvisorState)
        graph.add_node("classify", self._classify_node)
        graph.add_node("retrieve", self._retrieve_node)
        graph.add_node("conflicts", self._conflict_node)
        graph.add_node("pathway", self._pathway_node)
        graph.add_node("risk", self._risk_node)
        graph.add_node("substitution", self._substitution_node)
        graph.add_node("synthesize", self._synthesis_node)

        graph.add_edge(START, "classify")
        graph.add_edge("classify", "retrieve")
        graph.add_edge("retrieve", "conflicts")
        graph.add_edge("conflicts", "pathway")
        graph.add_edge("pathway", "risk")
        graph.add_edge("risk", "substitution")
        graph.add_edge("substitution", "synthesize")
        graph.add_edge("synthesize", END)
        return graph.compile()

    # ---------------- Answer synthesis ----------------
    def _student_summary(self, student) -> str:
        if not student:
            return "No student profile supplied."
        if isinstance(student, dict):
            return (
                f"Name: {student.get('name', 'Student')}\n"
                f"Major: {student.get('major', 'CSE')}\n"
                f"Completed: {student.get('completed', student.get('completed_courses', []))}"
            )
        return (
            f"Name: {getattr(student, 'name', 'Student')}\n"
            f"Major: {getattr(student, 'major', 'CSE')}\n"
            f"Completed: {sorted(getattr(student, 'completed_course_ids', set()))}"
        )

    def _synthesize(self, state: AdvisorState) -> str:
        conflicts = state.get("conflicts", [])
        blocking = [c for c in conflicts if c.get("blocking")]
        warnings = [c for c in conflicts if not c.get("blocking")]
        pathway = state.get("pathway")
        risk = state.get("risk_assessment")

        evidence = state.get("retrieved_context", "")
        prompt = f"""You are an academic-advising explanation layer. You MUST obey these rules:
1. Never convert prerequisite KNOWLEDGE into a formal registration prerequisite.
2. Only call a rule official/verified when the context explicitly marks it VERIFIED or formal.
3. Candidate substitutions require faculty approval unless explicitly APPROVED.
4. Do not invent credit limits, GPA thresholds, attendance rules, waivers, or graduation requirements.
5. The deterministic conflict engine below outranks the LLM.

Student:
{self._student_summary(state.get('student'))}

Question:
{state.get('query', '')}

Retrieved evidence:
{evidence}

Deterministic blocking conflicts:
{blocking}

Non-blocking readiness warnings:
{warnings}

Candidate pathway:
{pathway}

Planning risk indicator:
{risk}

Answer directly, distinguish BLOCKING vs READINESS WARNING, and cite only evidence actually supplied above."""

        if self.openai_client:
            try:
                model = MODEL_NAME if MODEL_NAME.startswith(("gpt", "o1", "o3")) else "gpt-4o-mini"
                completion = self.openai_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                )
                return completion.choices[0].message.content
            except Exception:
                pass

        if self.gemini_client:
            try:
                response = self.gemini_client.models.generate_content(model=MODEL_NAME, contents=prompt)
                if response and response.text:
                    return response.text
            except Exception:
                pass

        return self._deterministic_response(state)

    def _deterministic_response(self, state: AdvisorState) -> str:
        lines = ["### Academic advising result"]
        conflicts = state.get("conflicts", [])
        blocking = [c for c in conflicts if c.get("blocking")]
        warnings = [c for c in conflicts if not c.get("blocking")]

        if blocking:
            lines.append("\n**Blocking constraints**")
            lines.extend(f"- {c['message']}" for c in blocking)
        else:
            lines.append("\nNo sourced formal prerequisite block was detected for the referenced course(s).")

        if warnings:
            lines.append("\n**Academic readiness warnings (non-blocking)**")
            lines.extend(f"- {c['message']}" for c in warnings)

        if state.get("pathway"):
            lines.append("\n**Candidate pathway**")
            lines.append(str(state["pathway"]))

        if state.get("risk_assessment"):
            risk = state["risk_assessment"]
            lines.append(f"\n**Planning risk indicator:** {risk.get('level')} ({risk.get('score')})")
            for factor in risk.get("factors", []):
                lines.append(f"- {factor}")

        if state.get("retrieved_context"):
            lines.append("\n**Retrieved curriculum context**")
            lines.append(state["retrieved_context"][:1500])

        return "\n".join(lines)

    def _run_without_langgraph(self, state: AdvisorState) -> AdvisorState:
        for node in [
            self._classify_node,
            self._retrieve_node,
            self._conflict_node,
            self._pathway_node,
            self._risk_node,
            self._substitution_node,
            self._synthesis_node,
        ]:
            state.update(node(state))
        return state

    def chat_sync(self, message: str, student=None) -> dict:
        initial: AdvisorState = {"query": message, "student": student, "conflicts": [], "citations": []}
        final_state = self.workflow.invoke(initial) if self.workflow else self._run_without_langgraph(initial)
        citations = []
        for cite in final_state.get("citations", []):
            citations.append({
                "reference": cite.get("reference", "Source"),
                "source_status": cite.get("source_status", "UNVERIFIED"),
                "content": cite.get("content", "")[:220],
            })
        return {
            "response": final_state.get("final_response", ""),
            "citations": citations,
            "conflicts": final_state.get("conflicts", []),
            "pathway": final_state.get("pathway"),
            "risk": final_state.get("risk_assessment"),
            "agent_trace": ["classify", "retrieve", "conflicts", "pathway", "risk", "substitution", "synthesize"],
        }
