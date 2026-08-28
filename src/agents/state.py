from typing import TypedDict, Optional, Any


class AdvisorState(TypedDict, total=False):
    query: str
    messages: list[Any]
    student: Optional[Any]
    student_profile: dict
    query_type: str
    source_plan: dict
    retrieved_context: str
    retrieval: Optional[Any]
    citations: list[dict]
    citation_quality: dict
    conflicts: list[dict]
    substitutions: list[dict]
    pathway: Optional[dict]
    career_alignment: Optional[dict]
    risk_assessment: Optional[dict]
    verification: Optional[dict]
    needs_faculty_approval: bool
    exception_request: Optional[dict]
    faculty_packet: Optional[dict]
    agent_trace: list[dict]
    errors: list[dict]
    final_response: str
