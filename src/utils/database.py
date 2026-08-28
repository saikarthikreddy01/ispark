"""SQLite persistence helpers for the Academic Pathway Advisor."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from src.models.student import StudentProfile
from src.utils.config import DATA_DIR, DATABASE_PATH


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS students (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS petitions (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    student_name TEXT NOT NULL,
    gpa REAL NOT NULL,
    type TEXT NOT NULL,
    course TEXT NOT NULL,
    justification TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    faculty_comments TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def _db_path() -> Path:
    return Path(DATABASE_PATH)


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Open a SQLite connection with row dictionaries enabled."""
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.commit()
    finally:
        conn.close()


def initialize_database(seed: bool = True) -> None:
    """Create tables and optionally seed students/petitions for the demo app."""
    with get_connection() as conn:
        conn.executescript(SCHEMA_SQL)

    if seed:
        seed_students_from_json(DATA_DIR / "sample_students.json")


def seed_students_from_json(path: Path) -> None:
    """Load sample student records into SQLite without overwriting existing rows."""
    if not path.exists():
        return

    with path.open("r", encoding="utf-8") as f:
        students = json.load(f)

    with get_connection() as conn:
        for raw in students:
            conn.execute(
                """
                INSERT OR IGNORE INTO students (id, payload)
                VALUES (?, ?)
                """,
                (raw["id"], json.dumps(raw)),
            )


def load_students() -> list[StudentProfile]:
    """Return all student profiles stored in SQLite."""
    initialize_database(seed=True)
    with get_connection() as conn:
        rows = conn.execute("SELECT payload FROM students ORDER BY id").fetchall()

    return [StudentProfile(**json.loads(row["payload"])) for row in rows]


def seed_default_petitions(student: StudentProfile) -> None:
    """Create demo petitions for the active student if they do not already exist."""
    defaults = [
        {
            "id": f"PET-{student.id}-101",
            "student_id": student.id,
            "student_name": student.name,
            "gpa": student.gpa,
            "type": "Prerequisite Waiver (Policy §1.2)",
            "course": "CS301 (Algorithms)",
            "justification": "Completed equivalent advanced coursework and industry internship in Python algorithms.",
            "status": "PENDING",
            "faculty_comments": "",
        },
        {
            "id": f"PET-{student.id}-102",
            "student_id": student.id,
            "student_name": student.name,
            "gpa": student.gpa,
            "type": "Credit Overload Exception - 20 cr (Policy §5.2)",
            "course": "General Semester Load",
            "justification": "Senior year accelerated graduation plan. Cumulative GPA is in good standing.",
            "status": "PENDING",
            "faculty_comments": "",
        },
    ]

    with get_connection() as conn:
        for petition in defaults:
            conn.execute(
                """
                INSERT OR IGNORE INTO petitions
                (id, student_id, student_name, gpa, type, course, justification, status, faculty_comments)
                VALUES (:id, :student_id, :student_name, :gpa, :type, :course, :justification, :status, :faculty_comments)
                """,
                petition,
            )


def load_petitions(student_id: str | None = None) -> list[dict]:
    """Load petitions, optionally filtered to a single student."""
    initialize_database(seed=True)
    with get_connection() as conn:
        if student_id:
            rows = conn.execute(
                "SELECT * FROM petitions WHERE student_id = ? ORDER BY created_at, id",
                (student_id,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM petitions ORDER BY created_at, id").fetchall()

    return [dict(row) for row in rows]


def update_petition_status(petition_id: str, status: str, faculty_comments: str) -> None:
    """Persist a faculty decision for one petition."""
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE petitions
            SET status = ?, faculty_comments = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, faculty_comments, petition_id),
        )
