"""
MongoDB Database Connection & Repository for Academic AI Advisor
Connects to local or MongoDB Atlas cluster, with automatic seeding and resilient persistence.
"""

import os
import json
import time
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
        self.fallback_file = DATA_DIR / "persistent_db.json"
        self.client = None
        self.db = None
        self.is_connected = False
        self._last_connection_attempt = 0.0
        self._reconnect_cooldown_seconds = int(os.getenv("MONGODB_RECONNECT_COOLDOWN", "30"))
        self._init_connection()

    def _init_connection(self):
        self._last_connection_attempt = time.monotonic()
        try:
            from pymongo import MongoClient
            timeout_ms = int(os.getenv("MONGODB_TIMEOUT_MS", "2000"))
            client_kwargs = {
                "serverSelectionTimeoutMS": timeout_ms,
                "connectTimeoutMS": timeout_ms,
            }
            if "mongodb+srv" in MONGODB_URI:
                try:
                    import certifi
                    client_kwargs["tlsCAFile"] = certifi.where()
                except Exception:
                    # Do not allow invalid certs
                    pass
            
            self.client = MongoClient(MONGODB_URI, **client_kwargs)
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

    def ensure_connected(self):
        """Attempts to reconnect if connection dropped or failed earlier."""
        retry_due = time.monotonic() - self._last_connection_attempt >= self._reconnect_cooldown_seconds
        if not self.is_connected and retry_due:
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
        """Seed and synchronize MongoDB collections with latest C24 dataset only if empty"""
        if not self.is_connected or self.db is None:
            return

        try:
            # 1. Students
            if self.db.students.count_documents({}) == 0:
                students = self._load_json(DATA_DIR / "sample_students.json")
                if students:
                    self.db.students.insert_many(students)
                    print(f"[SEED] Synced {len(students)} C24 students to MongoDB.")

            # 2. Courses
            if self.db.courses.count_documents({}) == 0:
                courses = self._load_json(DATA_DIR / "courses.json")
                if courses:
                    self.db.courses.insert_many(courses)
                    print(f"[SEED] Synced {len(courses)} C24 courses to MongoDB.")

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
        if "academic_history" not in s:
            s["academic_history"] = []
        
        # Make a sanitized copy for public return, we'll keep password only when explicitly needed
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

    def update_student(self, student_id: str, update_data: Dict) -> Optional[Dict]:
        self.ensure_connected()
        student_id = student_id.upper()
        if "id" in update_data:
            update_data["id"] = update_data["id"].upper()
        if self.is_connected and self.db is not None:
            try:
                self.db.students.update_one(
                    {"$or": [
                        {"id": {"$regex": f"^{student_id}$", "$options": "i"}},
                        {"student_id": {"$regex": f"^{student_id}$", "$options": "i"}}
                    ]},
                    {"$set": update_data}
                )
                return self.get_student_by_id(student_id)
            except Exception:
                self.is_connected = False
        with open(self.fallback_file, "r", encoding="utf-8") as f:
            db_data = json.load(f)
        for s in db_data.get("students", []):
            if s.get("id", "").upper() == student_id or s.get("student_id", "").upper() == student_id:
                s.update(update_data)
                with open(self.fallback_file, "w", encoding="utf-8") as f:
                    json.dump(db_data, f, indent=2)
                return self._normalize_student(s)
        return None

    def delete_student(self, student_id: str) -> bool:
        self.ensure_connected()
        student_id = student_id.upper()
        if self.is_connected and self.db is not None:
            try:
                res = self.db.students.delete_one({
                    "$or": [
                        {"id": {"$regex": f"^{student_id}$", "$options": "i"}},
                        {"student_id": {"$regex": f"^{student_id}$", "$options": "i"}}
                    ]
                })
                return res.deleted_count > 0
            except Exception:
                self.is_connected = False
        with open(self.fallback_file, "r", encoding="utf-8") as f:
            db_data = json.load(f)
        initial_count = len(db_data.get("students", []))
        db_data["students"] = [s for s in db_data.get("students", []) if s.get("id", "").upper() != student_id and s.get("student_id", "").upper() != student_id]
        if len(db_data["students"]) < initial_count:
            with open(self.fallback_file, "w", encoding="utf-8") as f:
                json.dump(db_data, f, indent=2)
            return True
        return False

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

    def get_course_by_id(self, course_id: str) -> Optional[Dict]:
        self.ensure_connected()
        course_id = course_id.upper()
        if self.is_connected and self.db is not None:
            try:
                return self.db.courses.find_one({"id": {"$regex": f"^{course_id}$", "$options": "i"}}, {"_id": 0})
            except Exception:
                self.is_connected = False
        courses = self.get_all_courses()
        for c in courses:
            if c.get("id", "").upper() == course_id:
                return c
        return None

    def create_course(self, course_data: Dict) -> Dict:
        self.ensure_connected()
        course_data["id"] = course_data.get("id", "").upper()
        if self.is_connected and self.db is not None:
            try:
                self.db.courses.update_one(
                    {"id": course_data["id"]},
                    {"$set": course_data},
                    upsert=True
                )
                return course_data
            except Exception:
                self.is_connected = False
        with open(self.fallback_file, "r", encoding="utf-8") as f:
            db_data = json.load(f)
        db_data.setdefault("courses", [])
        db_data["courses"] = [c for c in db_data["courses"] if c.get("id", "").upper() != course_data["id"]]
        db_data["courses"].append(course_data)
        with open(self.fallback_file, "w", encoding="utf-8") as f:
            json.dump(db_data, f, indent=2)
        return course_data

    def update_course(self, course_id: str, update_data: Dict) -> Optional[Dict]:
        self.ensure_connected()
        course_id = course_id.upper()
        if "id" in update_data:
            update_data["id"] = update_data["id"].upper()
        if self.is_connected and self.db is not None:
            try:
                self.db.courses.update_one(
                    {"id": {"$regex": f"^{course_id}$", "$options": "i"}},
                    {"$set": update_data}
                )
                return self.get_course_by_id(course_id)
            except Exception:
                self.is_connected = False
        with open(self.fallback_file, "r", encoding="utf-8") as f:
            db_data = json.load(f)
        for c in db_data.get("courses", []):
            if c.get("id", "").upper() == course_id:
                c.update(update_data)
                with open(self.fallback_file, "w", encoding="utf-8") as f:
                    json.dump(db_data, f, indent=2)
                return c
        return None

    def delete_course(self, course_id: str) -> bool:
        self.ensure_connected()
        course_id = course_id.upper()
        if self.is_connected and self.db is not None:
            try:
                res = self.db.courses.delete_one({"id": {"$regex": f"^{course_id}$", "$options": "i"}})
                return res.deleted_count > 0
            except Exception:
                self.is_connected = False
        with open(self.fallback_file, "r", encoding="utf-8") as f:
            db_data = json.load(f)
        initial = len(db_data.get("courses", []))
        db_data["courses"] = [c for c in db_data.get("courses", []) if c.get("id", "").upper() != course_id]
        if len(db_data["courses"]) < initial:
            with open(self.fallback_file, "w", encoding="utf-8") as f:
                json.dump(db_data, f, indent=2)
            return True
        return False

    # --- Course Equivalency Operations ---
    def get_equivalencies(self) -> List[Dict]:
        self.ensure_connected()
        if self.is_connected and self.db is not None:
            try:
                doc = self.db.equivalencies.find_one({"_id": "course_equivalencies"})
                if doc and "data" in doc:
                    return doc["data"]
            except Exception:
                self.is_connected = False
        with open(self.fallback_file, "r", encoding="utf-8") as f:
            return json.load(f).get("equivalencies", [])

    def create_equivalency(self, equiv_data: Dict) -> Dict:
        self.ensure_connected()
        equiv_data["course_id"] = equiv_data.get("course_id", "").upper()
        equiv_data["equivalent_course_id"] = equiv_data.get("equivalent_course_id", "").upper()
        equivs = self.get_equivalencies()
        equivs = [eq for eq in equivs if not (eq.get("course_id") == equiv_data["course_id"] and eq.get("equivalent_course_id") == equiv_data["equivalent_course_id"])]
        equivs.append(equiv_data)
        if self.is_connected and self.db is not None:
            try:
                self.db.equivalencies.update_one(
                    {"_id": "course_equivalencies"},
                    {"$set": {"data": equivs}},
                    upsert=True
                )
                return equiv_data
            except Exception:
                self.is_connected = False
        if self.fallback_file and self.fallback_file.exists():
            with open(self.fallback_file, "r", encoding="utf-8") as f:
                db_data = json.load(f)
            db_data["equivalencies"] = equivs
            with open(self.fallback_file, "w", encoding="utf-8") as f:
                json.dump(db_data, f, indent=2)
        return equiv_data

    def delete_equivalency(self, course_id: str, equiv_course_id: str) -> bool:
        self.ensure_connected()
        course_id = course_id.upper()
        equiv_course_id = equiv_course_id.upper()
        equivs = self.get_equivalencies()
        new_equivs = [eq for eq in equivs if not (eq.get("course_id") == course_id and eq.get("equivalent_course_id") == equiv_course_id)]
        if len(new_equivs) == len(equivs):
            return False
        if self.is_connected and self.db is not None:
            try:
                self.db.equivalencies.update_one(
                    {"_id": "course_equivalencies"},
                    {"$set": {"data": new_equivs}},
                    upsert=True
                )
                return True
            except Exception:
                self.is_connected = False
        if self.fallback_file and self.fallback_file.exists():
            with open(self.fallback_file, "r", encoding="utf-8") as f:
                db_data = json.load(f)
            db_data["equivalencies"] = new_equivs
            with open(self.fallback_file, "w", encoding="utf-8") as f:
                json.dump(db_data, f, indent=2)
        return True

    # --- Department Dean & Admin Aggregated Analytics ---
    def get_admin_stats(self) -> Dict:
        self.ensure_connected()
        students = self.get_all_students()
        courses = self.get_all_courses()
        petitions = self.get_all_petitions()
        
        total_students = len(students)
        total_courses = len(courses)
        pending_petitions = len([p for p in petitions if p.get("status", "PENDING").upper() == "PENDING"])
        approved_petitions = len([p for p in petitions if p.get("status").upper() == "APPROVED"])
        
        at_risk_students = 0
        gpas = []
        for s in students:
            gpa = s.get("gpa", 3.0)
            gpas.append(gpa)
            if gpa < 2.5 or s.get("standing") == "Probation" or len(s.get("conflicts", [])) > 0:
                at_risk_students += 1
                
        avg_gpa = round(sum(gpas) / len(gpas), 2) if gpas else 3.5

        return {
            "total_students": total_students,
            "total_courses": total_courses,
            "pending_petitions": pending_petitions,
            "approved_petitions": approved_petitions,
            "total_petitions": len(petitions),
            "at_risk_students": at_risk_students,
            "average_gpa": avg_gpa,
            "institution": "VFSTR (Deemed to be University)",
            "department": "Computer Science & Engineering",
            "regulation": "C24 Regulation (160 Credits)"
        }

    # --- Petition Operations & Faculty Governance ---
    def get_all_petitions(self) -> List[Dict]:
        self.ensure_connected()
        if self.is_connected and self.db is not None:
            try:
                return list(self.db.petitions.find({}, {"_id": 0}))
            except Exception:
                self.is_connected = False
        with open(self.fallback_file, "r", encoding="utf-8") as f:
            db_data = json.load(f)
            return db_data.get("petitions", [])

    def create_petition(self, petition_data: Dict) -> Dict:
        self.ensure_connected()
        import datetime
        petition_data["created_at"] = petition_data.get("created_at") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        petition_data["status"] = petition_data.get("status") or "PENDING"
        if self.is_connected and self.db is not None:
            try:
                self.db.petitions.update_one(
                    {"petition_id": petition_data["petition_id"]},
                    {"$set": petition_data},
                    upsert=True
                )
                return petition_data
            except Exception:
                self.is_connected = False
        with open(self.fallback_file, "r", encoding="utf-8") as f:
            db_data = json.load(f)
        db_data.setdefault("petitions", [])
        db_data["petitions"] = [p for p in db_data["petitions"] if p.get("petition_id") != petition_data["petition_id"]]
        db_data["petitions"].append(petition_data)
        with open(self.fallback_file, "w", encoding="utf-8") as f:
            json.dump(db_data, f, indent=2)
        return petition_data

    def review_petition(self, petition_id: str, decision: str, reviewer: str, comments: str = "") -> Optional[Dict]:
        self.ensure_connected()
        import datetime
        stamp = f"SIG-{petition_id}-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
        update_fields = {
            "status": decision.upper(),
            "reviewer": reviewer,
            "review_comments": comments,
            "reviewed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "audit_stamp": stamp
        }
        if self.is_connected and self.db is not None:
            try:
                self.db.petitions.update_one(
                    {"petition_id": petition_id},
                    {"$set": update_fields}
                )
                doc = self.db.petitions.find_one({"petition_id": petition_id}, {"_id": 0})
                return doc
            except Exception:
                self.is_connected = False
        with open(self.fallback_file, "r", encoding="utf-8") as f:
            db_data = json.load(f)
        petitions = db_data.get("petitions", [])
        for p in petitions:
            if p.get("petition_id") == petition_id:
                p.update(update_fields)
                with open(self.fallback_file, "w", encoding="utf-8") as f:
                    json.dump(db_data, f, indent=2)
                return p
        return None

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
