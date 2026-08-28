import json
from pathlib import Path
from src.agents.state import AdvisorState


class CareerAgent:
    """Advisory career alignment. Never upgrades career preferences into degree rules."""

    def __init__(self, kg, data_dir=None):
        self.kg = kg
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).resolve().parents[2] / "data"
        path = self.data_dir / "career_tracks.json"
        self.tracks = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def _detect_goal(self, query: str, profile: dict) -> tuple[str | None, dict | None]:
        combined = " ".join([query or "", *profile.get("career_goals", [])]).lower()
        for track_id, track in self.tracks.items():
            candidates = [track.get("display_name", ""), *track.get("aliases", [])]
            if any(c and c.lower() in combined for c in candidates):
                return track_id, track
        return None, None

    def _course_text(self, course) -> str:
        skills = " ".join(getattr(course, "skills", []) or [])
        return f"{course.name} {course.description} {skills}".lower()

    def align(self, query: str, profile: dict) -> dict:
        track_id, track = self._detect_goal(query, profile)
        if not track:
            return {"matched": False, "recommendations": [], "source_status": "PROJECT_ADVISORY"}

        completed = set(profile.get("completed_course_ids", []))
        wanted = [s.lower() for s in track.get("skills", [])]
        scored = []
        for cid, course in self.kg.courses.items():
            if cid in completed:
                continue
            text = self._course_text(course)
            matched = [skill for skill in wanted if skill in text]
            if matched:
                scored.append((len(matched), cid, course, matched))

        scored.sort(key=lambda x: (-x[0], getattr(x[2], "sem", 99) or 99, x[1]))
        recommendations = [
            {
                "course_id": cid,
                "name": course.name,
                "matched_skills": matched,
                "score": score,
                "advisory_only": True,
            }
            for score, cid, course, matched in scored[:8]
        ]

        return {
            "matched": True,
            "track_id": track_id,
            "track": track.get("display_name"),
            "skills": track.get("skills", []),
            "recommendations": recommendations,
            "source_status": "PROJECT_ADVISORY",
            "disclaimer": "Career alignment is advisory and does not create degree or prerequisite requirements.",
        }

    def process(self, state: AdvisorState) -> AdvisorState:
        profile = state.get("student_profile", {})
        result = self.align(state.get("query", ""), profile)
        return {"career_alignment": result}
