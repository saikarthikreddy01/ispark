"""
MongoDB Database Connection & Repository for Academic AI Advisor
Connects to local or MongoDB Atlas cluster, with automatic seeding and resilient persistence.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGODB_DB", "academic_advisor")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class MongoDBManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.is_connected = False
        self._init_connection()

    def _init_connection(self):
        try:
            from pymongo import MongoClient
            client_kwargs = {
                "serverSelectionTimeoutMS": 5000,
                "connectTimeoutMS": 5000
            }
            if "mongodb+srv" in MONGODB_URI:
                try:
                    import certifi
                    client_kwargs["tlsCAFile"] = certifi.where()
                except Exception:
                    client_kwargs["tlsAllowInvalidCertificates"] = True
            
            self.client = MongoClient(MONGODB_URI, **client_kwargs)
            # Trigger server check
            self.client.admin.command('ping')
            self.db = self.client[DATABASE_NAME]
            self.is_connected = True
            print(f"[OK] Connected to MongoDB at {MONGODB_URI} [DB: {DATABASE_NAME}]")
            self._seed_initial_data()
        except Exception as e:
            try:
                # Second attempt with tlsAllowInvalidCertificates if SSL failed
                from pymongo import MongoClient
                self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000, tlsAllowInvalidCertificates=True)
                self.client.admin.command('ping')
                self.db = self.client[DATABASE_NAME]
                self.is_connected = True
                print(f"[OK] Connected to MongoDB (TLS fallback) at {MONGODB_URI} [DB: {DATABASE_NAME}]")
                self._seed_initial_data()
            except Exception as e2:
                print(f"[INFO] MongoDB at {MONGODB_URI} ({e2}). Using local persistent database.")
                self.is_connected = False
                self._init_file_db()

    def ensure_connected(self):
        """Attempts to reconnect if connection dropped or failed earlier."""
        if not self.is_connected:
            self._init_connection()

    def _init_file_db(self):
        self.fallback_file = DATA_DIR / "persistent_db.json"
        if not self.fallback_file.exists():
            self._seed_file_db()

    def _seed_file_db(self):
        students = self._load_json(DATA_DIR / "sample_students.json")
        courses = self._load_json(DATA_DIR / "courses.json")
        equivs = self._load_json(DATA_DIR / "equivalencies.json")
        
        data = {
            "students": students,
            "courses": courses,
            "equivalencies": equivs,
            "chat_history": [],
            "petitions": []
        }
        with open(self.fallback_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _seed_initial_data(self):
        """Seed MongoDB collections if empty"""
        if not self.is_connected or self.db is None:
            return

        try:
            # 1. Students
            if self.db.students.count_documents({}) == 0:
                students = self._load_json(DATA_DIR / "sample_students.json")
                if students:
                    self.db.students.insert_many(students)
                    print(f"[SEED] Seeded {len(students)} students to MongoDB.")

            # 2. Courses
            if self.db.courses.count_documents({}) == 0:
                courses = self._load_json(DATA_DIR / "courses.json")
                if courses:
                    self.db.courses.insert_many(courses)
                    print(f"[SEED] Seeded {len(courses)} courses to MongoDB.")

            # 3. Equivalencies
            if self.db.equivalencies.count_documents({}) == 0:
                equivs = self._load_json(DATA_DIR / "equivalencies.json")
                if equivs:
                    self.db.equivalencies.insert_one({"_id": "course_equivalencies", "data": equivs})
        except Exception as err:
            print(f"[WARN] Error seeding MongoDB: {err}")

    def _load_json(self, path: Path) -> Any:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _normalize_student(self, student: Dict) -> Dict:
        if not student:
            return student
        s = dict(student)
        if "id" not in s and "student_id" in s:
            s["id"] = s["student_id"]
        if "completed" not in s:
            if "completed_courses" in s and isinstance(s["completed_courses"], list):
                s["completed"] = [
                    c["course_id"] if isinstance(c, dict) and "course_id" in c else c
                    for c in s["completed_courses"]
                ]
            elif "completed_course_ids" in s:
                s["completed"] = s["completed_course_ids"]
            else:
                s["completed"] = []
        if "planned" not in s:
            s["planned"] = s.get("planned_course_ids", [])
        if "conflicts" not in s:
            s["conflicts"] = []
        if "password" not in s:
            s["password"] = "password123"
        return s

    # --- Student Operations ---
    def get_all_students(self) -> List[Dict]:
        self.ensure_connected()
        if self.is_connected and self.db is not None:
            try:
                students = list(self.db.students.find({}, {"_id": 0}))
                return [self._normalize_student(s) for s in students]
            except Exception:
                self.is_connected = False
        with open(self.fallback_file, "r", encoding="utf-8") as f:
            students = json.load(f).get("students", [])
            return [self._normalize_student(s) for s in students]

    def get_student_by_id(self, student_id: str) -> Optional[Dict]:
        self.ensure_connected()
        student_id = student_id.upper()
        if self.is_connected and self.db is not None:
            try:
                doc = self.db.students.find_one(
                    {"$or": [
                        {"id": {"$regex": f"^{student_id}$", "$options": "i"}},
                        {"student_id": {"$regex": f"^{student_id}$", "$options": "i"}}
                    ]},
                    {"_id": 0}
                )
                if doc:
                    return self._normalize_student(doc)
            except Exception:
                self.is_connected = False
        for s in self.get_all_students():
            if s.get("id", "").upper() == student_id or s.get("student_id", "").upper() == student_id:
                return self._normalize_student(s)
        return None

    def create_student(self, student_data: Dict) -> Dict:
        self.ensure_connected()
        student_data["id"] = student_data.get("id", "").upper()
        if self.is_connected and self.db is not None:
            try:
                self.db.students.update_one(
                    {"id": student_data["id"]},
                    {"$set": student_data},
                    upsert=True
                )
                return self._normalize_student(student_data)
            except Exception:
                self.is_connected = False
        with open(self.fallback_file, "r", encoding="utf-8") as f:
            db_data = json.load(f)
        # Remove existing if any
        db_data["students"] = [s for s in db_data["students"] if s.get("id", "").upper() != student_data["id"]]
        db_data["students"].append(student_data)
        with open(self.fallback_file, "w", encoding="utf-8") as f:
            json.dump(db_data, f, indent=2)
        return self._normalize_student(student_data)

    # --- Course Operations ---
    def get_all_courses(self) -> List[Dict]:
        self.ensure_connected()
        if self.is_connected and self.db is not None:
            try:
                return list(self.db.courses.find({}, {"_id": 0}))
            except Exception:
                self.is_connected = False
        with open(self.fallback_file, "r", encoding="utf-8") as f:
            return json.load(f).get("courses", [])

    # --- Chat History & Audit Logs ---
    def save_chat_log(self, student_id: str, question: str, response: str, citations: List[str]):
        self.ensure_connected()
        log_entry = {
            "student_id": student_id,
            "question": question,
            "response": response,
            "citations": citations
        }
        if self.is_connected and self.db is not None:
            try:
                self.db.chat_history.insert_one(log_entry)
                return
            except Exception:
                self.is_connected = False
        with open(self.fallback_file, "r", encoding="utf-8") as f:
            db_data = json.load(f)
        db_data.setdefault("chat_history", []).append(log_entry)
        with open(self.fallback_file, "w", encoding="utf-8") as f:
            json.dump(db_data, f, indent=2)

    def get_chat_history(self, student_id: str) -> List[Dict]:
        self.ensure_connected()
        student_id = student_id.upper()
        if self.is_connected and self.db is not None:
            try:
                return list(self.db.chat_history.find(
                    {"student_id": {"$regex": f"^{student_id}$", "$options": "i"}},
                    {"_id": 0}
                ))
            except Exception:
                self.is_connected = False
        with open(self.fallback_file, "r", encoding="utf-8") as f:
            db_data = json.load(f)
        return [c for c in db_data.get("chat_history", []) if c.get("student_id", "").upper() == student_id]

# Singleton Database Manager
db_manager = MongoDBManager()

