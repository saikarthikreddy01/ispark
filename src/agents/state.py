from typing import TypedDict, Optional, Any

class AdvisorState(TypedDict, total=False):
    messages: list[Any]
    student: Optional[Any]
    query_type: str
    retrieved_context: str
    citations: list[dict]
    conflicts: list[dict]
    pathway: Optional[dict]
    risk_assessment: Optional[dict]
    needs_faculty_approval: bool
