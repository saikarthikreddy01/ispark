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
            self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
            # Trigger server check
            self.client.admin.command('ping')
            self.db = self.client[DATABASE_NAME]
            self.is_connected = True
            print(f"[OK] Connected to MongoDB at {MONGODB_URI} [DB: {DATABASE_NAME}]")
            self._seed_initial_data()
        except Exception as e:
            print(f"[INFO] MongoDB at {MONGODB_URI} ({e}). Using local persistent database.")
            self.is_connected = False
            self._init_file_db()

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
        if not self.is_connected:
            return

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

    def _load_json(self, path: Path) -> Any:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    # --- Student Operations ---
    def get_all_students(self) -> List[Dict]:
        if self.is_connected:
            return list(self.db.students.find({}, {"_id": 0}))
        with open(self.fallback_file, "r", encoding="utf-8") as f:
            return json.load(f).get("students", [])

    def get_student_by_id(self, student_id: str) -> Optional[Dict]:
        student_id = student_id.upper()
        if self.is_connected:
            return self.db.students.find_one({"id": {"$regex": f"^{student_id}$", "$options": "i"}}, {"_id": 0})
        for s in self.get_all_students():
            if s.get("id", "").upper() == student_id:
                return s
        return None

    def create_student(self, student_data: Dict) -> Dict:
        student_data["id"] = student_data.get("id", "").upper()
        if self.is_connected:
            self.db.students.update_one(
                {"id": student_data["id"]},
                {"$set": student_data},
                upsert=True
            )
        else:
            with open(self.fallback_file, "r", encoding="utf-8") as f:
                db_data = json.load(f)
            # Remove existing if any
            db_data["students"] = [s for s in db_data["students"] if s.get("id", "").upper() != student_data["id"]]
            db_data["students"].append(student_data)
            with open(self.fallback_file, "w", encoding="utf-8") as f:
                json.dump(db_data, f, indent=2)
        return student_data

    # --- Course Operations ---
    def get_all_courses(self) -> List[Dict]:
        if self.is_connected:
            return list(self.db.courses.find({}, {"_id": 0}))
        with open(self.fallback_file, "r", encoding="utf-8") as f:
            return json.load(f).get("courses", [])

    # --- Chat History & Audit Logs ---
    def save_chat_log(self, student_id: str, question: str, response: str, citations: List[str]):
        log_entry = {
            "student_id": student_id,
            "question": question,
            "response": response,
            "citations": citations
        }
        if self.is_connected:
            self.db.chat_history.insert_one(log_entry)
        else:
            with open(self.fallback_file, "r", encoding="utf-8") as f:
                db_data = json.load(f)
            db_data.setdefault("chat_history", []).append(log_entry)
            with open(self.fallback_file, "w", encoding="utf-8") as f:
                json.dump(db_data, f, indent=2)

# Singleton Database Manager
db_manager = MongoDBManager()
