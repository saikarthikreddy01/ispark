"""Agentic academic-advisor orchestration.

Architecture rule:
    LLM proposes/explains -> federated sources + graph retrieve -> deterministic
    rules verify -> human faculty approves exceptions.

The supervisor dynamically routes requests to specialized agents rather than
running every agent for every question. Shared state records source authority,
evidence, verification, escalation packets, and an execution trace for the UI.
"""

import os
from src.agents.state import AdvisorState
from src.agents.profile_agent import ProfileAgent
from src.agents.source_router_agent import SourceRouterAgent
from src.agents.conflict_agent import ConflictAgent
from src.agents.pathway_agent import PathwayAgent
from src.agents.risk_agent import RiskAgent
from src.agents.substitution_agent import SubstitutionAgent
from src.agents.career_agent import CareerAgent
from src.agents.verification_agent import VerificationAgent
from src.agents.citation_agent import CitationAgent
from src.agents.faculty_agent import FacultyEscalationAgent
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
except Exception:
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

        self.profile_agent = ProfileAgent()
        self.source_router_agent = SourceRouterAgent(self.kg)
        self.conflict_agent = ConflictAgent(self.kg, self.prereq_checker, self.credit_validator)
        self.pathway_agent = PathwayAgent(self.kg, self.prereq_checker, self.credit_validator, self.schedule_analyzer)
        self.risk_agent = RiskAgent(self.kg, self.schedule_analyzer, self.credit_validator)
        self.substitution_agent = SubstitutionAgent(self.kg, self.retriever)
        self.career_agent = CareerAgent(self.kg, DATA_DIR)
        self.verification_agent = VerificationAgent(self.kg, self.prereq_checker, self.credit_validator)
        self.citation_agent = CitationAgent()
        self.faculty_agent = FacultyEscalationAgent()
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
        if any(k in q for k in ["substitute", "instead of", "equivalent", "alternative course", "replacement"]):
            return "substitution"
        if any(k in q for k in ["career", "ai engineer", "ml engineer", "backend", "cybersecurity", "data scientist", "data engineer"]):
            return "career"
        if any(k in q for k in ["pathway", "plan", "roadmap", "schedule", "semesters", "graduate", "graduation plan"]):
            return "pathway"
        if any(k in q for k in ["risk", "delay", "bottleneck", "standing", "blocked graduation"]):
            return "risk"
        if any(k in q for k in ["policy", "waiver", "transfer", "repeat", "credit limit", "regulation"]):
            return "policy"
        if any(k in q for k in ["prereq", "prerequisite", "require", "eligible", "can i take", "enroll", "register"]):
            return "prerequisite"
        return "general"

    def _trace(self, state: AdvisorState, agent: str, action: str, status: str = "ok") -> list[dict]:
        trace = list(state.get("agent_trace", []))
        trace.append({"agent": agent, "action": action, "status": status})
        return trace

    def _profile_node(self, state: AdvisorState) -> AdvisorState:
        out = self.profile_agent.process(state)
        out["agent_trace"] = self._trace(state, "ProfileAgent", "normalized student academic history")
        return out

    def _classify_node(self, state: AdvisorState) -> AdvisorState:
        q_type = self.classify_query(state.get("query", ""))
        return {"query_type": q_type, "agent_trace": self._trace(state, "SupervisorAgent", f"classified request as {q_type}")}

    def _source_router_node(self, state: AdvisorState) -> AdvisorState:
        out = self.source_router_agent.process(state)
        authorities = out.get("source_plan", {}).get("authorities", [])
        out["agent_trace"] = self._trace(state, "FederatedSourceRouter", f"selected authorities: {', '.join(authorities)}")
        return out

    def _retrieve_node(self, state: AdvisorState) -> AdvisorState:
        try:
            retrieval = self.retriever.retrieve(state.get("query", ""), student=state.get("student"), top_k=5)
            context = "\n\n".join(x for x in [retrieval.graph_context, retrieval.policy_context, retrieval.course_context] if x)
            source_plan = state.get("source_plan", {})
            if source_plan:
                context = f"Federated source plan: {source_plan}\n\n{context}"
            return {
                "retrieval": retrieval,
                "retrieved_context": context,
                "citations": retrieval.citations,
                "agent_trace": self._trace(state, "GraphRAGAgent", "retrieved graph relations and source text"),
            }
        except Exception as exc:
            errors = list(state.get("errors", []))
            errors.append({"agent": "GraphRAGAgent", "error": str(exc)})
            return {
                "errors": errors,
                "retrieved_context": "",
                "citations": [],
                "agent_trace": self._trace(state, "GraphRAGAgent", "retrieval failed; continuing with deterministic data", "degraded"),
            }

    def _conflict_node(self, state: AdvisorState) -> AdvisorState:
        out = self.conflict_agent.process(state)
        out["agent_trace"] = self._trace(state, "ConstraintConflictAgent", "checked formal prerequisites and non-blocking knowledge gaps")
        return out

    def _pathway_node(self, state: AdvisorState) -> AdvisorState:
        out = self.pathway_agent.process(state)
        out["agent_trace"] = self._trace(state, "PathwayAgent", "generated candidate semester pathway from degree structure")
        return out

    def _risk_node(self, state: AdvisorState) -> AdvisorState:
        out = self.risk_agent.process(state)
        out["agent_trace"] = self._trace(state, "RiskBottleneckAgent", "calculated transparent planning-risk and bottlenecks")
        return out

    def _substitution_node(self, state: AdvisorState) -> AdvisorState:
        out = self.substitution_agent.process(state)
        out["agent_trace"] = self._trace(state, "SubstitutionAgent", "searched candidate substitutions/equivalencies")
        return out

    def _career_node(self, state: AdvisorState) -> AdvisorState:
        out = self.career_agent.process(state)
        out["agent_trace"] = self._trace(state, "CareerAlignmentAgent", "matched curriculum courses to advisory career skills")
        return out

    def _verification_node(self, state: AdvisorState) -> AdvisorState:
        out = self.verification_agent.process(state)
        decision = out.get("verification", {}).get("decision", "UNKNOWN")
        out["agent_trace"] = self._trace(state, "FormalVerificationAgent", f"verification decision: {decision}")
        return out

    def _citation_node(self, state: AdvisorState) -> AdvisorState:
        out = self.citation_agent.process(state)
        out["agent_trace"] = self._trace(state, "CitationAgent", "deduplicated evidence and scored source quality")
        return out

    def _faculty_node(self, state: AdvisorState) -> AdvisorState:
        out = self.faculty_agent.process(state)
        action = "prepared human-review packet" if state.get("needs_faculty_approval") else "no human escalation required"
        out["agent_trace"] = self._trace(state, "FacultyEscalationAgent", action)
        return out

    def _synthesis_node(self, state: AdvisorState) -> AdvisorState:
        response = self._synthesize(state)
        return {"final_response": response, "agent_trace": self._trace(state, "AdvisorSynthesisAgent", "generated source-aware natural-language advice")}

    def _route_after_retrieval(self, state: AdvisorState) -> str:
        return state.get("query_type", "general")

    def _route_after_substitution(self, state: AdvisorState) -> str:
        return "faculty" if state.get("needs_faculty_approval") else "verify"

    def _build_workflow(self):
        if StateGraph is None:
            return None
        graph = StateGraph(AdvisorState)
        for name, fn in [
            ("profile", self._profile_node), ("classify", self._classify_node),
            ("source_router", self._source_router_node), ("retrieve", self._retrieve_node),
            ("conflicts", self._conflict_node), ("pathway", self._pathway_node),
            ("risk", self._risk_node), ("substitution", self._substitution_node),
            ("career", self._career_node), ("verify", self._verification_node),
            ("citations", self._citation_node), ("faculty", self._faculty_node),
            ("synthesize", self._synthesis_node),
        ]:
            graph.add_node(name, fn)

        graph.add_edge(START, "profile")
        graph.add_edge("profile", "classify")
        graph.add_edge("classify", "source_router")
        graph.add_edge("source_router", "retrieve")
        graph.add_conditional_edges("retrieve", self._route_after_retrieval, {
            "prerequisite": "conflicts", "pathway": "pathway", "risk": "risk",
            "substitution": "substitution", "career": "career", "policy": "verify", "general": "conflicts",
        })
        graph.add_edge("pathway", "risk")
        graph.add_edge("risk", "career")
        graph.add_edge("career", "verify")
        graph.add_edge("conflicts", "verify")
        graph.add_conditional_edges("substitution", self._route_after_substitution, {"faculty": "faculty", "verify": "verify"})
        graph.add_edge("faculty", "verify")
        graph.add_edge("verify", "citations")
        graph.add_edge("citations", "synthesize")
        graph.add_edge("synthesize", END)
        return graph.compile()

    def _student_summary(self, state: AdvisorState) -> str:
        profile = state.get("student_profile", {})
        if not profile.get("available"):
            return "No student profile supplied."
        return (
            f"Name: {profile.get('name')}\nMajor: {profile.get('major')}\n"
            f"Completed: {profile.get('completed_course_ids', [])}\nCareer goals: {profile.get('career_goals', [])}"
        )

    def _synthesize(self, state: AdvisorState) -> str:
        verification = state.get("verification") or {}
        evidence = state.get("retrieved_context", "")
        prompt = f"""You are only the explanation layer of an agentic academic advising system.
The deterministic agents and source labels below are the authority.

NON-NEGOTIABLE RULES
1. Never convert curriculum PREREQUISITE KNOWLEDGE into a formal registration prerequisite.
2. Only call a rule official/verified when evidence explicitly says VERIFIED/formal.
3. Candidate substitutions require faculty approval unless explicitly APPROVED.
4. Career mappings are advisory only; they never create degree requirements.
5. Do not invent credit limits, GPA thresholds, attendance rules, waivers, or graduation requirements.
6. If verification says BLOCKED, explain the block. If it says FACULTY_REVIEW_REQUIRED, do not imply approval.

Student:\n{self._student_summary(state)}
Question:\n{state.get('query', '')}
Intent: {state.get('query_type')}
Federated source plan: {state.get('source_plan')}
Retrieved evidence:\n{evidence}
Conflicts / readiness warnings: {state.get('conflicts', [])}
Candidate pathway: {state.get('pathway')}
Career alignment: {state.get('career_alignment')}
Planning risk: {state.get('risk_assessment')}
Substitution candidates: {state.get('substitutions', [])}
Formal verification: {verification}
Faculty escalation packet: {state.get('faculty_packet')}
Citation quality: {state.get('citation_quality')}

Answer directly. Clearly label FORMAL BLOCK, READINESS WARNING, ADVISORY RECOMMENDATION, and FACULTY REVIEW when applicable. Cite only supplied evidence."""

        if self.openai_client:
            try:
                model = MODEL_NAME if MODEL_NAME.startswith(("gpt", "o1", "o3")) else "gpt-4o-mini"
                completion = self.openai_client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], temperature=0.1)
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
        verification = state.get("verification") or {}
        lines.append(f"\n**Verification:** {verification.get('decision', 'ADVISORY_OK')}")
        blocking = verification.get("blocking_conflicts", [])
        warnings = verification.get("readiness_warnings", [])
        if blocking:
            lines.append("\n**FORMAL BLOCKS**")
            lines.extend(f"- {c.get('message')}" for c in blocking)
        if warnings:
            lines.append("\n**READINESS WARNINGS (non-blocking)**")
            lines.extend(f"- {c.get('message')}" for c in warnings)
        if state.get("pathway"):
            lines.append("\n**Candidate pathway**")
            lines.append(str(state["pathway"]))
        career = state.get("career_alignment") or {}
        if career.get("matched"):
            lines.append(f"\n**Career alignment:** {career.get('track')} (advisory)")
            for rec in career.get("recommendations", [])[:5]:
                lines.append(f"- {rec['course_id']} {rec['name']}: {', '.join(rec['matched_skills'])}")
        if state.get("risk_assessment"):
            risk = state["risk_assessment"]
            lines.append(f"\n**Planning risk indicator:** {risk.get('level')} ({risk.get('score')})")
            lines.extend(f"- {factor}" for factor in risk.get("factors", []))
        if state.get("substitutions"):
            lines.append("\n**Substitution candidates**")
            for sub in state["substitutions"]:
                approval = "faculty approval required" if sub.get("needs_approval") else "approved"
                lines.append(f"- {sub['course_id']} {sub['name']} — {approval}")
        if state.get("faculty_packet"):
            lines.append("\n**FACULTY REVIEW REQUIRED** — escalation packet prepared; no exception was auto-approved.")
        if state.get("retrieved_context"):
            lines.append("\n**Retrieved curriculum context**")
            lines.append(state["retrieved_context"][:1600])
        return "\n".join(lines)

    def _run_without_langgraph(self, state: AdvisorState) -> AdvisorState:
        for node in [self._profile_node, self._classify_node, self._source_router_node, self._retrieve_node]:
            state.update(node(state))
        route = self._route_after_retrieval(state)
        if route in {"prerequisite", "general"}:
            state.update(self._conflict_node(state))
        elif route == "pathway":
            state.update(self._pathway_node(state)); state.update(self._risk_node(state)); state.update(self._career_node(state))
        elif route == "risk":
            state.update(self._risk_node(state)); state.update(self._career_node(state))
        elif route == "substitution":
            state.update(self._substitution_node(state))
            if state.get("needs_faculty_approval"):
                state.update(self._faculty_node(state))
        elif route == "career":
            state.update(self._career_node(state))
        for node in [self._verification_node, self._citation_node, self._synthesis_node]:
            state.update(node(state))
        return state

    def chat_sync(self, message: str, student=None) -> dict:
        initial: AdvisorState = {"query": message, "student": student, "conflicts": [], "citations": [], "substitutions": [], "agent_trace": [], "errors": []}
        final_state = self.workflow.invoke(initial) if self.workflow else self._run_without_langgraph(initial)
        citations = [{"reference": cite.get("reference", "Source"), "source_status": cite.get("source_status", "UNVERIFIED"), "content": cite.get("content", "")[:220]} for cite in final_state.get("citations", [])]
        return {
            "response": final_state.get("final_response", ""),
            "query_type": final_state.get("query_type"),
            "source_plan": final_state.get("source_plan"),
            "verification": final_state.get("verification"),
            "citations": citations,
            "citation_quality": final_state.get("citation_quality"),
            "conflicts": final_state.get("conflicts", []),
            "pathway": final_state.get("pathway"),
            "career_alignment": final_state.get("career_alignment"),
            "risk": final_state.get("risk_assessment"),
            "substitutions": final_state.get("substitutions", []),
            "needs_faculty_approval": final_state.get("needs_faculty_approval", False),
            "faculty_packet": final_state.get("faculty_packet"),
            "agent_trace": final_state.get("agent_trace", []),
            "errors": final_state.get("errors", []),
        }
