"""Regression tests for the focused production chat entrypoint."""

from backend import app as entrypoint


class FakeAdvisor:
    def chat_sync(self, message, student=None):
        return {
            "response": "Verified agent response",
            "citations": [
                {
                    "reference": "C24 curriculum",
                    "source_status": "CURRICULUM_DERIVED",
                    "content": "Evidence",
                }
            ],
            "conflicts": [],
            "pathway": None,
            "risk": None,
            "career_alignment": None,
            "verification": {"decision": "ADVISORY_OK"},
            "faculty_packet": None,
            "source_plan": {"authorities": ["CSE"]},
            "agent_trace": [
                {"agent": "SupervisorAgent", "action": "classified request", "status": "ok"},
                {"agent": "GraphRAGAgent", "action": "retrieved evidence", "status": "ok"},
            ],
        }


def test_agent_chat_route_precedes_legacy_mount():
    """The focused /api/chat route must win before the legacy mounted app."""
    routes = entrypoint.app.router.routes
    chat_index = next(
        i for i, route in enumerate(routes)
        if getattr(route, "path", None) == "/api/chat" and "POST" in getattr(route, "methods", set())
    )
    mount_index = next(i for i, route in enumerate(routes) if getattr(route, "path", None) == "")
    assert chat_index < mount_index


def test_advisor_chat_returns_agent_outputs(monkeypatch):
    student = {
        "id": "TEST001",
        "name": "Test Student",
        "major": "CSE",
        "completed": [],
    }

    monkeypatch.setattr(entrypoint.db_manager, "get_student_by_id", lambda _student_id: student)
    monkeypatch.setattr(entrypoint.db_manager, "save_chat_log", lambda *args, **kwargs: None)
    monkeypatch.setattr(entrypoint, "get_advisor", lambda: FakeAdvisor())

    response = entrypoint.advisor_chat(
        entrypoint.ChatRequest(student_id="TEST001", question="Can I take Machine Learning?")
    )

    assert response["reply"] == "Verified agent response"
    assert response["verification"]["decision"] == "ADVISORY_OK"
    assert response["agent_trace"][0]["agent"] == "SupervisorAgent"
    assert response["tool_executed"] == "LangGraph academic-advisor workflow"
    assert response["citations"] == ["C24 curriculum · CURRICULUM_DERIVED"]
