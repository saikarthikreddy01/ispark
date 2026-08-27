"""AcadGraph AI - unified hackathon application.

This module is the single FastAPI entrypoint for the prototype. It connects the
static single-page frontend, the resilient database layer, the academic
knowledge graph, Graph-RAG retrieval, LangGraph agents, deterministic
verification, and faculty review workflow.

Core principle:
    LLM explains -> graph/RAG retrieves -> rules verify -> faculty approves exceptions.
"""

from __future__ import annotations

import json
import os
import uuid
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.database import db_manager
from src.agents.orchestrator import AcademicAdvisor
from src.models.graph_schema import REL_EQUIVALENT, REL_KNOWLEDGE, REL_REQUIRES


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
WEB_DIR = ROOT_DIR / "web"


def load_json(name: str, fallback: Any) -> Any:
    path = DATA_DIR / name
    if not path.exists():
        return fallback
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def public_student(student: Optional[dict]) -> Optional[dict]:
    """Return only fields that are safe and useful for the prototype UI."""
    if not student:
        return None
    allowed = {
        "id", "student_id", "name", "major", "reg_regulation",
        "current_semester", "gpa", "completed", "planned", "conflicts",
        "expected_grad", "standing", "honours_enrolled", "honours_track",
        "career_goals",
    }
    clean = {key: value for key, value in student.items() if key in allowed}
    clean["id"] = clean.get("id") or clean.get("student_id")
    clean["completed"] = list(clean.get("completed") or [])
    clean["planned"] = list(clean.get("planned") or [])
    clean["conflicts"] = list(clean.get("conflicts") or [])
    return clean


@lru_cache(maxsize=1)
def get_advisor() -> AcademicAdvisor:
    """Load the graph, retriever and LangGraph workflow once per process."""
    return AcademicAdvisor()


class ChatRequest(BaseModel):
    student_id: str = Field(min_length=1)
    question: str = Field(min_length=1, max_length=4000)


class PetitionRequest(BaseModel):
    student_id: str
    course_id: Optional[str] = None
    request_type: str = "ACADEMIC_EXCEPTION_REVIEW"
    reason: str
    evidence: list[dict] = []
    faculty_packet: Optional[dict] = None


class ReviewRequest(BaseModel):
    decision: str
    reviewer: str = "Faculty Reviewer"
    comments: str = ""


app = FastAPI(
    title="AcadGraph AI",
    description="Explainable Agentic Graph-RAG academic advising prototype",
    version="5.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": "AcadGraph AI",
        "version": "5.0.0",
        "database": "mongodb" if db_manager.is_connected else "local-persistent-json",
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "architecture": "LangGraph + Graph-RAG + deterministic verification + human review",
    }


@app.get("/api/demo")
def demo_catalog() -> dict:
    """Curated judge-demo profiles and prompts without inventing academic rules."""
    students = [public_student(s) for s in db_manager.get_all_students()[:3]]
    students = [s for s in students if s]
    prompts = [
        {
            "title": "AI/ML readiness",
            "prompt": "I want to become an AI/ML engineer. Check my readiness for Machine Learning and Deep Learning and explain any academic risks.",
        },
        {
            "title": "Degree pathway",
            "prompt": "Plan my remaining semesters using the curriculum structure, flag bottlenecks, and keep elective choices flexible.",
        },
        {
            "title": "Substitution review",
            "prompt": "Can I substitute an equivalent course for one of my remaining courses? Show only supported candidates and escalate anything unverified to faculty.",
        },
    ]
    return {"students": students, "prompts": prompts}


@app.get("/api/student/{student_id}")
def student_detail(student_id: str) -> dict:
    student = public_student(db_manager.get_student_by_id(student_id))
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.get("/api/courses")
def courses(q: str = Query(default="", max_length=120)) -> list[dict]:
    items = db_manager.get_all_courses()
    if q.strip():
        needle = q.strip().lower()
        items = [
            c for c in items
            if needle in str(c.get("id", "")).lower()
            or needle in str(c.get("name", "")).lower()
            or needle in str(c.get("department", "")).lower()
        ]
    return [
        {
            "id": c.get("id"),
            "name": c.get("name"),
            "department": c.get("department"),
            "credits": c.get("credits"),
            "category": c.get("category"),
            "sem": c.get("sem"),
            "description": c.get("description", ""),
            "skills": c.get("skills", [])[:6],
        }
        for c in items
    ]


@app.get("/api/overview/{student_id}")
def overview(student_id: str) -> dict:
    student = public_student(db_manager.get_student_by_id(student_id))
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    degree = load_json("degree_requirements.json", {})
    courses_raw = db_manager.get_all_courses()
    course_map = {c.get("id"): c for c in courses_raw if c.get("id")}
    completed = set(student.get("completed", []))
    planned = set(student.get("planned", []))

    completed_credits = sum(
        int(course_map[cid].get("credits") or 0)
        for cid in completed
        if cid in course_map
    )

    semesters = []
    for semester in degree.get("semesters_structure", []):
        semester_courses = []
        for cid in semester.get("courses", []):
            course = course_map.get(cid, {"id": cid, "name": cid, "credits": 0})
            state = "completed" if cid in completed else "planned" if cid in planned else "remaining"
            semester_courses.append({
                "id": cid,
                "name": course.get("name", cid),
                "credits": course.get("credits", 0),
                "category": course.get("category", "Curriculum course"),
                "state": state,
            })
        semesters.append({
            "semester": semester.get("semester"),
            "semester_index": semester.get("semester_index"),
            "published_total_credits": semester.get("published_total_credits"),
            "courses": semester_courses,
            "choice_slots": semester.get("choice_slots", []),
            "optional_track_slot": semester.get("optional_track_slot", False),
            "note": semester.get("note"),
        })

    remaining_core = [
        cid for cid in degree.get("required_courses", [])
        if cid not in completed
    ]

    return {
        "student": student,
        "program": degree.get("program"),
        "institution": degree.get("institution"),
        "batch": degree.get("batch"),
        "completed_credits_observed": completed_credits,
        "planning_target_credits": degree.get("total_credits_required"),
        "planning_target_status": degree.get("total_credits_required_status", "UNVERIFIED"),
        "planning_target_note": degree.get("total_credits_note"),
        "remaining_core_count": len(remaining_core),
        "semesters": semesters,
        "requirement_groups": degree.get("requirement_groups", []),
        "source_reference": degree.get("source_reference"),
    }


@app.get("/api/graph")
def graph_data() -> dict:
    """Expose the provenance-aware course graph used by the agents."""
    advisor = get_advisor()
    kg = advisor.kg
    nodes = []
    for course in kg.get_all_courses():
        nodes.append({
            "id": course.id,
            "name": course.name,
            "department": course.department,
            "credits": course.credits,
            "category": str(course.category),
            "semester": course.sem,
        })

    edges = []
    allowed = {REL_REQUIRES, REL_KNOWLEDGE, REL_EQUIVALENT}
    for source, target, attrs in kg.graph.edges(data=True):
        relation = attrs.get("type")
        if source not in kg.courses or target not in kg.courses or relation not in allowed:
            continue
        edges.append({
            "source": source,
            "target": target,
            "type": relation,
            "blocking": relation == REL_REQUIRES,
            "source_reference": attrs.get("source_reference"),
            "requires_faculty_approval": attrs.get("requires_faculty_approval", False),
        })
    return {"nodes": nodes, "edges": edges}


@app.post("/api/chat")
def advisor_chat(req: ChatRequest) -> dict:
    student = db_manager.get_student_by_id(req.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = get_advisor().chat_sync(question, student=student)
    except Exception as exc:
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
        "query_type": result.get("query_type"),
        "citations": citation_labels,
        "citation_details": citation_details,
        "citation_quality": result.get("citation_quality"),
        "conflicts": result.get("conflicts", []),
        "pathway": result.get("pathway"),
        "risk": result.get("risk"),
        "career_alignment": result.get("career_alignment"),
        "substitutions": result.get("substitutions", []),
        "needs_faculty_approval": result.get("needs_faculty_approval", False),
        "verification": result.get("verification"),
        "faculty_packet": result.get("faculty_packet"),
        "source_plan": result.get("source_plan"),
        "agent_trace": result.get("agent_trace", []),
        "errors": result.get("errors", []),
        "tool_executed": "LangGraph academic-advisor workflow",
    }


@app.get("/api/chat/history/{student_id}")
def chat_history(student_id: str) -> dict:
    return {"history": db_manager.get_chat_history(student_id)}


@app.get("/api/faculty/petitions")
def petitions() -> dict:
    items = db_manager.get_all_petitions()
    items.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    return {"petitions": items}


@app.post("/api/faculty/petitions")
def create_petition(req: PetitionRequest) -> dict:
    if not db_manager.get_student_by_id(req.student_id):
        raise HTTPException(status_code=404, detail="Student not found")
    petition = {
        "petition_id": f"PET-{uuid.uuid4().hex[:8].upper()}",
        "student_id": req.student_id.upper(),
        "course_id": (req.course_id or "").upper() or None,
        "request_type": req.request_type,
        "reason": req.reason,
        "evidence": req.evidence,
        "faculty_packet": req.faculty_packet,
        "status": "PENDING",
        "agent_action": "RECOMMEND_REVIEW_ONLY",
    }
    return {"petition": db_manager.create_petition(petition)}


@app.post("/api/faculty/petitions/{petition_id}/review")
def review_petition(petition_id: str, req: ReviewRequest) -> dict:
    decision = req.decision.upper()
    if decision not in {"APPROVED", "REJECTED"}:
        raise HTTPException(status_code=400, detail="Decision must be APPROVED or REJECTED")
    petition = db_manager.review_petition(petition_id, decision, req.reviewer, req.comments)
    if not petition:
        raise HTTPException(status_code=404, detail="Petition not found")
    return {"petition": petition}


if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
