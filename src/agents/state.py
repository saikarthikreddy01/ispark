from typing import TypedDict, Optional, Any


class AdvisorState(TypedDict, total=False):
    query: str
    messages: list[Any]
    student: Optional[Any]
    query_type: str
    retrieved_context: str
    retrieval: Optional[Any]
    citations: list[dict]
    conflicts: list[dict]
    pathway: Optional[dict]
    risk_assessment: Optional[dict]
    needs_faculty_approval: bool
    final_response: str
