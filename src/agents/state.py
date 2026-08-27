from typing import TypedDict, Optional, Any

class AdvisorState(TypedDict, total=False):
    messages: list[Any]
    query: str
    student: Optional[Any]
    query_type: str
    retrieved_context: str
    citations: list[dict]
    response: str
    conflicts: list[dict]
    pathway: Optional[dict]
    risk_assessment: Optional[dict]
    needs_faculty_approval: bool
