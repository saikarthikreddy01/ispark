import json
import os
import unittest
from pathlib import Path


os.environ.setdefault("OPENAI_API_KEY", "")
os.environ.setdefault("GEMINI_API_KEY", "")

from src.agents.orchestrator import AcademicAdvisor
from src.agents.profile_agent import ProfileAgent
from src.constraint_engine.prerequisite_checker import PrerequisiteChecker


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class AcademicAdvisorRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        students = json.loads((PROJECT_ROOT / "data" / "sample_students.json").read_text(encoding="utf-8"))
        cls.student = next(student for student in students if student.get("id") == "241FA04077")
        cls.advisor = AcademicAdvisor()

    def test_profile_uses_transcript_grades_and_credits(self):
        profile = ProfileAgent().build_profile(self.student)
        self.assertEqual(profile["completed_credits"], 93)
        self.assertEqual(profile["graded_credits"], 85)
        self.assertEqual(len(profile["completed_course_grades"]), 35)
        self.assertEqual(profile["gpa_scale"], 10)

    def test_ten_point_grade_order_supports_s_and_o(self):
        checker = PrerequisiteChecker(None)
        self.assertTrue(checker._grade_meets_min("S", "D"))
        self.assertTrue(checker._grade_meets_min("O", "D"))
        self.assertFalse(checker._grade_meets_min("B", "A"))

    def test_pathway_starts_from_current_academic_term(self):
        result = self.advisor.chat_sync("Generate my graduation pathway and semester-wise plan.", self.student)
        self.assertEqual(result["query_type"], "pathway")
        self.assertEqual(result["pathway"]["semesters"][0]["academic_term"], "III Year I Semester")
        self.assertEqual(result["risk"]["credit_summary"]["total_completed"], 93)

    def test_bottleneck_quick_action_runs_risk_agent(self):
        result = self.advisor.chat_sync("What courses are blocking my graduation?", self.student)
        self.assertEqual(result["query_type"], "risk")
        self.assertIsNotNone(result["risk"])
        self.assertIn("RiskBottleneckAgent", [item["agent"] for item in result["agent_trace"]])

    def test_substitution_quick_action_requires_faculty(self):
        result = self.advisor.chat_sync("Find approved substitutions for 24CS402", self.student)
        self.assertEqual(result["query_type"], "substitution")
        self.assertEqual(result["verification"]["decision"], "FACULTY_REVIEW_REQUIRED")
        self.assertTrue(result["faculty_packet"])
        self.assertEqual(result["substitutions"][0]["course_id"], "22CS953")

    def test_waiver_request_creates_human_review_packet(self):
        result = self.advisor.chat_sync(
            "I need a prerequisite waiver for 22CS804. Prepare it for faculty approval.",
            self.student,
        )
        self.assertEqual(result["query_type"], "waiver")
        self.assertEqual(result["verification"]["decision"], "FACULTY_REVIEW_REQUIRED")
        self.assertEqual(result["faculty_packet"]["status"], "PENDING_HUMAN_REVIEW")

    def test_unknown_course_is_not_approved(self):
        result = self.advisor.chat_sync("Can I take FAKE101?", self.student)
        self.assertEqual(result["verification"]["decision"], "INVALID_COURSE_REFERENCE")
        self.assertEqual(result["conflicts"][0]["type"], "UNKNOWN_COURSE")

    def test_irrelevant_question_has_no_citations(self):
        result = self.advisor.chat_sync("What color should I paint my bicycle?", self.student)
        self.assertEqual(result["query_type"], "out_of_scope")
        self.assertEqual(result["verification"]["decision"], "OUT_OF_SCOPE")
        self.assertEqual(result["citations"], [])

    def test_normal_greeting_gets_a_conversational_reply(self):
        result = self.advisor.chat_sync("Hello, how are you?", self.student)
        self.assertEqual(result["query_type"], "conversation")
        self.assertEqual(result["verification"]["decision"], "CONVERSATIONAL_RESPONSE")
        self.assertIn("ready to help", result["response"].lower())
        self.assertEqual(result["citations"], [])

    def test_capability_question_gets_a_helpful_reply(self):
        result = self.advisor.chat_sync("What can you do?", self.student)
        self.assertEqual(result["query_type"], "conversation")
        self.assertIn("degree pathway", result["response"].lower())

    def test_vague_study_question_routes_to_pathway(self):
        result = self.advisor.chat_sync("What should I study next?", self.student)
        self.assertEqual(result["query_type"], "pathway")
        self.assertIsNotNone(result["pathway"])

    def test_policy_citations_preserve_verified_status(self):
        result = self.advisor.chat_sync("Can I take 24CS302 Artificial Intelligence?", self.student)
        statuses = {citation["source_status"] for citation in result["citations"]}
        self.assertIn("VERIFIED_FROM_SUPPLIED_DOCUMENT", statuses)
        self.assertGreater(result["citation_quality"]["verified"], 0)


if __name__ == "__main__":
    unittest.main()
