"""Regression tests for the unified AcadGraph AI application."""

from backend import app as entrypoint


class FakeAdvisor:
    def chat_sync(self, message, student=None):
        return {
            "response": "Verified agent response",
            "query_type": "prerequisite",
            "citations": [
                {
                    "reference": "C24 curriculum",
                    "source_status": "CURRICULUM_DERIVED",
                    "content": "Evidence",
                }
            ],
            "citation_quality": {"verified": 1},
            "conflicts": [],
            "pathway": None,
            "risk": None,
            "career_alignment": None,
            "substitutions": [],
            "needs_faculty_approval": False,
            "verification": {"decision": "ADVISORY_OK"},
            "faculty_packet": None,
            "source_plan": {"authorities": ["CSE"]},
            "agent_trace": [
                {"agent": "SupervisorAgent", "action": "classified request", "status": "ok"},
                {"agent": "GraphRAGAgent", "action": "retrieved evidence", "status": "ok"},
            ],
            "errors": [],
        }


def test_unified_api_routes_precede_static_mount():
    routes = entrypoint.app.router.routes
    chat_index = next(
        i for i, route in enumerate(routes)
        if getattr(route, "path", None) == "/api/chat" and "POST" in getattr(route, "methods", set())
    )
    mount_index = next(i for i, route in enumerate(routes) if getattr(route, "path", None) == "")
    assert chat_index < mount_index


def test_health_describes_unified_architecture():
    payload = entrypoint.health()
    assert payload["status"] == "ok"
    assert payload["app"] == "AcadGraph AI"
    assert "LangGraph" in payload["architecture"]


def test_public_student_never_exposes_password():
    clean = entrypoint.public_student({
        "id": "TEST001",
        "name": "Test Student",
        "password": "secret",
        "major": "CSE",
        "completed": [],
    })
    assert "password" not in clean
    assert clean["id"] == "TEST001"


def test_advisor_chat_returns_agent_outputs(monkeypatch):
    student = {
        "id": "TEST001",
        "name": "Test Student",
        "major": "CSE",
        "completed": [],
    }

    monkeypatch.setattr(entrypoint, "repo_student", lambda _student_id: student)
    monkeypatch.setattr(entrypoint, "repo_save_chat", lambda *args, **kwargs: None)
    monkeypatch.setattr(entrypoint, "get_advisor", lambda: FakeAdvisor())

    response = entrypoint.advisor_chat(
        entrypoint.ChatRequest(student_id="TEST001", question="Can I take Machine Learning?")
    )

    assert response["reply"] == "Verified agent response"
    assert response["verification"]["decision"] == "ADVISORY_OK"
    assert response["agent_trace"][0]["agent"] == "SupervisorAgent"
    assert response["tool_executed"] == "LangGraph academic-advisor workflow"
    assert response["citations"] == ["C24 curriculum · CURRICULUM_DERIVED"]
