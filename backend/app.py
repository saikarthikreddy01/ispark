"""Production FastAPI entrypoint for the hackathon prototype.

The legacy server still owns the existing REST endpoints and static web UI, but
/api/chat is intercepted here and routed through the real LangGraph
AcademicAdvisor. This keeps the prototype focused while removing the old
hard-coded chatbot decision path from the deployed request flow.
"""

from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.database import db_manager
from backend.server import app as legacy_app
from src.agents.orchestrator import AcademicAdvisor


class ChatRequest(BaseModel):
    student_id: str
    question: str


@lru_cache(maxsize=1)
def get_advisor() -> AcademicAdvisor:
    """Create one reusable advisor graph per application process."""
    return AcademicAdvisor()


app = FastAPI(
    title="AcadGraph AI",
    description=(
        "Agentic Graph-RAG academic advising with deterministic constraint "
        "verification and faculty escalation for exceptional cases."
    ),
    version="4.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/chat")
def advisor_chat(req: ChatRequest):
    """Run the real multi-agent academic-advising workflow.

    Flow:
      student profile -> supervisor -> federated source routing -> Graph-RAG ->
      specialist agent -> deterministic verification -> citations -> Gemini
      explanation. Faculty review is prepared when an exception is required.
    """
    student = db_manager.get_student_by_id(req.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = get_advisor().chat_sync(question, student=student)
    except Exception as exc:
        # Do not fall back to fabricated academic rules. Surface a safe failure
        # instead so the user knows the advising workflow could not verify it.
        raise HTTPException(
            status_code=503,
            detail=f"Academic advising workflow unavailable: {exc}",
        ) from exc

    citation_details = result.get("citations", []) or []
    citation_labels = []
    for citation in citation_details:
        if isinstance(citation, dict):
            reference = citation.get("reference", "Academic source")
            status = citation.get("source_status", "UNVERIFIED")
            citation_labels.append(f"{reference} · {status}")
        else:
            citation_labels.append(str(citation))

    reply = result.get("response", "")
    db_manager.save_chat_log(req.student_id, question, reply, citation_labels)

    return {
        "reply": reply,
        "citations": citation_labels,
        "citation_details": citation_details,
        "citation_quality": result.get("citation_quality"),
        "conflicts": result.get("conflicts", []),
        "pathway": result.get("pathway"),
        "risk": result.get("risk"),
        "career_alignment": result.get("career_alignment"),
        "verification": result.get("verification"),
        "faculty_packet": result.get("faculty_packet"),
        "needs_faculty_approval": result.get("needs_faculty_approval", False),
        "substitutions": result.get("substitutions", []),
        "query_type": result.get("query_type"),
        "source_plan": result.get("source_plan"),
        "agent_trace": result.get("agent_trace", []),
        "errors": result.get("errors", []),
        "workflow_mode": result.get("workflow_mode"),
        "tool_executed": result.get("workflow_mode", "ACADEMIC_ADVISOR"),
    }


# Keep all existing APIs and the static frontend available behind the new
# focused entrypoint. Because this mount is registered after /api/chat, the
# agentic chat route above takes precedence over the legacy hard-coded route.
app.mount("/", legacy_app)
