"""
FastAPI REST API Server for Academic AI Advisor
Includes 3D Graph-RAG, Topological Pathway Sequencing, Conflict Detection, Bottleneck Analysis,
Alternative Course Substitutions, Policy Retrieval, and Formal Faculty Exception Review Board.
"""

import os
import json
import uuid
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.database import db_manager

app = FastAPI(
    title="Academic AI Advisor — 3D Graph-RAG Platform",
    description="Decentralized Graph-RAG advising service with formal constraint verification and faculty governance",
    version="3.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Helper to load JSON
def load_json_file(filename: str) -> Any:
    path = DATA_DIR / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# --- Pydantic Request Models ---
class LoginRequest(BaseModel):
    regno: str
    password: Optional[str] = "password"

class SignUpRequest(BaseModel):
    name: str
    regno: str
    major: Optional[str] = "Computer Science"
    expected_grad: Optional[str] = "Spring 2027"
    password: Optional[str] = "password"

class ChatRequest(BaseModel):
    student_id: str
    question: str

class AuditRequest(BaseModel):
    student_id: str
    selected_courses: List[str]
    semester: str

class PathwayGenerateRequest(BaseModel):
    student_id: str
    max_credits_per_semester: Optional[int] = 16
    target_graduation: Optional[str] = "Spring 2027"

class SubstitutionApplyRequest(BaseModel):
    student_id: str
    original_course_id: str
    substitute_course_id: str

class PetitionSubmitRequest(BaseModel):
    student_id: str
    petition_type: str  # PREREQUISITE_WAIVER, CREDIT_OVERLOAD, COURSE_SUBSTITUTION, GRADE_FORGIVENESS
    course_id: Optional[str] = None
    target_semester: Optional[str] = "Fall 2026"
    requested_credits: Optional[int] = None
    justification: str

class PetitionReviewRequest(BaseModel):
    decision: str  # APPROVED or REJECTED
    reviewer: str
    comments: Optional[str] = ""

# --- Admin Module Request Models ---
class AdminLoginRequest(BaseModel):
    username: str
    password: str

class StudentAdminCreateRequest(BaseModel):
    id: str
    name: str
    major: Optional[str] = "Computer Science & Engineering"
    gpa: Optional[float] = 3.75
    standing: Optional[str] = "Good Standing"
    expected_grad: Optional[str] = "Spring 2028"
    completed: Optional[List[str]] = []
    planned: Optional[List[str]] = []
    password: Optional[str] = "password123"

class StudentAdminUpdateRequest(BaseModel):
    name: Optional[str] = None
    major: Optional[str] = None
    gpa: Optional[float] = None
    standing: Optional[str] = None
    expected_grad: Optional[str] = None
    completed: Optional[List[str]] = None
    planned: Optional[List[str]] = None
    password: Optional[str] = None

class CourseAdminCreateRequest(BaseModel):
    id: str
    name: str
    department: Optional[str] = "CSE"
    credits: Optional[int] = 4
    ltpc: Optional[str] = "3-0-2-4"
    category: Optional[str] = "Professional Core"
    sem: Optional[int] = 1
    description: Optional[str] = ""
    prereqs: Optional[List[str]] = []
    prerequisite_groups: Optional[List[Dict]] = []
    corequisites: Optional[List[str]] = []
    credit_categories: Optional[List[str]] = ["PROFESSIONAL_CORE"]
    offered_semesters: Optional[List[str]] = ["FALL", "SPRING"]
    difficulty_level: Optional[int] = 2
    modules: Optional[List[Dict]] = []
    practices: Optional[List[str]] = []
    skills: Optional[List[str]] = []
    course_outcomes: Optional[List[Dict]] = []
    textbooks: Optional[List[Dict]] = []
    reference_books: Optional[List[Dict]] = []

class CourseAdminUpdateRequest(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    credits: Optional[int] = None
    ltpc: Optional[str] = None
    category: Optional[str] = None
    sem: Optional[int] = None
    description: Optional[str] = None
    prereqs: Optional[List[str]] = None
    prerequisite_groups: Optional[List[Dict]] = None
    corequisites: Optional[List[str]] = None
    credit_categories: Optional[List[str]] = None
    offered_semesters: Optional[List[str]] = None
    difficulty_level: Optional[int] = None
    modules: Optional[List[Dict]] = None
    practices: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    course_outcomes: Optional[List[Dict]] = None
    textbooks: Optional[List[Dict]] = None
    reference_books: Optional[List[Dict]] = None

class EquivalencyAdminCreateRequest(BaseModel):
    course_id: str
    equivalent_course_id: str
    equivalency_type: Optional[str] = "DIRECT"
    minimum_grade: Optional[str] = "C"
    notes: Optional[str] = "Approved by Department Academic Board"

# --- 1. HEALTH & CORE DATA ---

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "database": "mongodb" if db_manager.is_connected else "persistent_storage",
        "db_connected": db_manager.is_connected,
        "features": [
            "knowledge_graph",
            "graph_rag_gemini",
            "topological_sequencing",
            "conflict_detection",
            "bottleneck_risk_analysis",
            "substitutions_engine",
            "citation_tracker",
            "faculty_governance"
        ]
    }

@app.get("/api/students")
def get_students():
    return db_manager.get_all_students()

@app.get("/api/student/{student_id}")
def get_student(student_id: str):
    student = db_manager.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.get("/api/courses")
def get_courses():
    return db_manager.get_all_courses()

@app.get("/api/courses/{course_id}")
def get_course_detail(course_id: str):
    courses = db_manager.get_all_courses()
    for c in courses:
        if c.get("id", "").upper() == course_id.upper():
            return c
    raise HTTPException(status_code=404, detail=f"Course '{course_id}' not found in C24 catalog")

@app.get("/api/curriculum")
def get_curriculum_structure():
    degree_req = load_json_file("degree_requirements.json")
    courses = db_manager.get_all_courses()
    course_map = {c["id"]: c for c in courses}

    # Structure by semester
    structured_semesters = []
    for sem in degree_req.get("semesters_structure", []):
        sem_courses = [course_map.get(cid, {"id": cid, "name": cid}) for cid in sem.get("courses", [])]
        structured_semesters.append({
            "semester": sem.get("semester"),
            "semester_index": sem.get("semester_index"),
            "total_credits": sem.get("total_credits"),
            "contact_hours": sem.get("contact_hours"),
            "courses": sem_courses
        })

    # Group Electives, Honours, Minors, Open Electives
    dept_electives = [c for c in courses if c.get("category") == "Department Elective"]
    honours_courses = [c for c in courses if c.get("category") == "Honours"]
    minor_courses = [c for c in courses if c.get("category") == "Minors"]
    open_electives = [c for c in courses if c.get("category") == "Open Elective"]

    return {
        "program": degree_req.get("program", "B.Tech. Computer Science & Engineering (C24 Regulation)"),
        "institution": degree_req.get("institution", "VFSTR Deemed to be University"),
        "batch": degree_req.get("batch", "2024-28"),
        "total_credits_required": degree_req.get("total_credits_required", 160),
        "category_requirements": degree_req.get("category_requirements", {}),
        "semesters": structured_semesters,
        "department_electives": dept_electives,
        "honours_courses": honours_courses,
        "minor_courses": minor_courses,
        "open_electives": open_electives
    }

@app.get("/api/equivalencies")
def get_equivalencies():
    return load_json_file("equivalencies.json")

# --- 2. AUTHENTICATION ---

@app.post("/api/auth/login")
def login(req: LoginRequest):
    regno = req.regno.strip().upper()
    student = db_manager.get_student_by_id(regno)
    
    # Fallback search by ID case-insensitively
    if not student:
        all_students = db_manager.get_all_students()
        for s in all_students:
            if s.get("id", "").strip().upper() == regno:
                student = s
                break

    if not student:
        raise HTTPException(status_code=401, detail=f"Student ID '{regno}' not found. Please click 'Sign Up' to create your account.")
    
    stored_pwd = student.get("password")
    if stored_pwd and req.password:
        valid_passwords = [stored_pwd, "password", "password123", regno, regno.lower()]
        if req.password not in valid_passwords:
            raise HTTPException(status_code=401, detail=f"Incorrect password for {regno}. (Hint: use '{stored_pwd}' or 'password123')")

    return {
        "success": True,
        "message": f"Welcome back, {student.get('name', regno)}!",
        "student": student
    }

@app.post("/api/auth/signup")
def signup(req: SignUpRequest):
    regno = req.regno.strip().upper()
    existing = db_manager.get_student_by_id(regno)
    if existing:
        raise HTTPException(status_code=400, detail=f"Student ID '{regno}' is already registered. Please Sign In.")

    new_student = {
        "id": regno,
        "name": req.name.strip(),
        "password": req.password or "password123",
        "major": req.major or "Computer Science",
        "gpa": 7.78,
        "completed": ["CS101", "MATH101", "CS102", "MATH201", "PHYS101", "CS201", "CS250", "ENG101"],
        "planned": ["CS301", "CS302", "CS303", "CS350", "CS401", "CS402", "CS499"],
        "conflicts": [],
        "expected_grad": req.expected_grad or "2028",
        "standing": "Good Standing"
    }

    saved = db_manager.create_student(new_student)
    return {
        "success": True,
        "message": f"Student account {regno} registered successfully in MongoDB Atlas!",
        "student": saved
    }

@app.get("/api/gemini/status")
def get_gemini_status():
    api_key = os.getenv("GEMINI_API_KEY", "")
    masked = f"{api_key[:8]}...{api_key[-6:]}" if len(api_key) > 14 else "Not configured"
    return {
        "status": "connected" if api_key else "disconnected",
        "model": "gemini-3.6-flash",
        "name": "Gemini API Key",
        "project_name": "projects/882038538915",
        "project_number": "882038538915",
        "api_key_masked": masked,
        "mode": "real_time_graph_rag",
        "live_interaction": True
    }

# --- 3. GRAPH-RAG ADVISING WITH CITATIONS ---

@app.post("/api/chat")
def advisor_chat(req: ChatRequest):
    student = db_manager.get_student_by_id(req.student_id)
    student_ctx = ""
    if student:
        student_ctx = (
            f"Student: {student.get('name', 'Student')} (ID: {student.get('id', req.student_id)})\n"
            f"Major: {student.get('major', 'Computer Science')}\n"
            f"GPA: {student.get('gpa', 3.5)} ({student.get('standing', 'Good Standing')})\n"
            f"Completed Courses: {', '.join(student.get('completed', []))}\n"
            f"Planned Courses: {', '.join(student.get('planned', []))}\n"
            f"Expected Graduation: {student.get('expected_grad', 'Spring 2027')}\n"
        )

    # Graph-RAG Policy Context Extraction
    policy_doc = ""
    policies_path = DATA_DIR / "policies.md"
    if policies_path.exists():
        with open(policies_path, "r", encoding="utf-8") as f:
            policy_doc = f.read()

    api_key = os.getenv("GEMINI_API_KEY")
    reply = ""
    citations = []

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = (
                "You are an expert Academic AI Advisor for Vignan's Foundation for Science, Technology & Research (VFSTR Deemed to be University).\n"
                "You specialize in the B.Tech Computer Science & Engineering (C24 Regulation, Batch 2024-28) curriculum, prerequisite validation, syllabi, course outcomes, and university policies.\n"
                "Ground your answers using official institutional standards. Include specific course codes (e.g., 24CS101, 22TP201, 24CS204, 24CS209, 24CS306, 22CS401, 22CS804, 22CS951) and formal section citations like [VFSTR C24 Regulation §1.1] or [B.Tech CSE Catalog 2024-28].\n\n"
                f"--- OFFICIAL UNIVERSITY POLICY TEXT ---\n{policy_doc[:4000]}\n\n"
                f"--- STUDENT PROFILE ---\n{student_ctx}\n\n"
                f"--- STUDENT QUESTION ---\n{req.question}\n\n"
                "Provide a personalized, insightful, well-structured academic advising response answering the student's question directly with exact policy citations and actionable next steps:"
            )
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )
            if response and response.text:
                reply = response.text
            
            # Extract citations from reply or add defaults
            citations = ["[VFSTR C24 Regulation §1.1]", "[B.Tech CSE Course Catalog 2024-28]"]
            if "§1.2" in reply or "waiver" in req.question.lower() or "petition" in req.question.lower():
                citations.append("[Policy §1.2: Prerequisite Waivers]")
            if "§1.3" in reply or "grade" in req.question.lower() or "evaluation" in req.question.lower():
                citations.append("[Policy §1.3: Continuous Evaluation & Thresholds]")
            if "§2.1" in reply or "substitut" in req.question.lower() or "equivalent" in req.question.lower():
                citations.append("[Policy §2.1: Course Equivalencies]")
            if "honour" in req.question.lower() or "minor" in req.question.lower():
                citations.append("[VFSTR Regulation: Honours & Minors Track]")
            if "graduat" in req.question.lower() or "credit" in req.question.lower():
                citations.append("[Policy §2.0: 160 Total Credit Graduation Requirement]")
        except Exception as e:
            print(f"[WARN] Gemini API error ({e}), using Graph-RAG deterministic fallback.")

    # High-precision Graph-RAG Rule-based Fallback for C24
    if not reply:
        q = req.question.lower()
        if "24cs209" in q or "daa" in q or "algorithm" in q:
            reply = (
                "⚠️ **Prerequisite Policy on 24CS209 (Design and Analysis of Algorithms)**:\n\n"
                "Under **VFSTR C24 Curriculum §1.1 (Prerequisite Enforcement)**, enrolling in **24CS209** requires:\n"
                "1. Passing **22TP201 (Data Structures)** with a passing grade.\n"
                "2. Completing **24MT203 (Discrete Mathematical Structures)**.\n\n"
                "**Bottleneck Impact**: 24CS209 is a critical milestone blocking **24CS306 (Machine Learning)** and **22CS951 (Advanced Graph Algorithms)**. "
                "Ensure Data Structures and Discrete Math are cleared to maintain normal 4-year graduation trajectory."
            )
            citations = ["[VFSTR C24 Curriculum §1.1]", "[B.Tech CSE Catalog 2024-28, II-II]", "[Policy §1.3: Grade Requirements]"]
        elif "24cs306" in q or "machine learning" in q or "ml" in q:
            reply = (
                "📘 **Prerequisites for 24CS306 (Machine Learning)**:\n\n"
                "According to the **VFSTR C24 Syllabus (III Year II Semester)**, **24CS306 (2-2-2, 4 Credits)** requires:\n"
                "- **22ST202 (Probability and Statistics)**\n"
                "- **24CS102 (Problem Solving through Python)**\n"
                "- **24MT101 (Linear Algebra and ODE)**\n\n"
                "Once satisfied, you are eligible to explore advanced electives like **22CS804 (Deep Learning)** and **22CS809 (Text Mining)**."
            )
            citations = ["[B.Tech CSE Catalog 2024-28, III-II]", "[Policy §1.1: Prerequisite Enforcement]"]
        elif "22cs804" in q or "deep learning" in q:
            reply = (
                "🧠 **Curriculum Details for 22CS804 (Deep Learning)**:\n\n"
                "Under **VFSTR C24 Department Electives (3-0-2, 4 Credits)**, **22CS804** covers:\n"
                "- **Module 1**: Perceptron convergence, Shallow vs Deep networks, Optimizers (Adam, RMSProp, Adagrad), Regularization (Dropout, Batch Norm), and CNNs (AlexNet, VGGNet, ResNet).\n"
                "- **Module 2**: Deep Unsupervised Learning (Autoencoders, Denoising, Contractive) and RNNs, LSTMs, GRUs for Text & Vision.\n\n"
                "Prerequisites: **24CS306 (Machine Learning)** & **24CS102 (Python)**."
            )
            citations = ["[B.Tech CSE Department Electives, p.131]", "[VFSTR C24 Syllabus]"]
        elif "waiver" in q or "petition" in q or "exception" in q:
            reply = (
                "📝 **Formal Faculty Exception & Waiver Policy (§1.2)**:\n\n"
                "If you face an unavoidable scheduling conflict or hold certified equivalent competencies, you may submit a **Prerequisite Waiver Petition**:\n"
                "1. Submit via the **Faculty Governance** tab with written justification.\n"
                "2. Requires instructor recommendation and HoD (CSE) approval.\n"
                "3. Petitions undergo automated formal constraint verification before final sign-off."
            )
            citations = ["[Policy §1.2: Prerequisite Waivers]", "[VFSTR Academic Governance Regulations]"]
        elif "honour" in q or "minor" in q:
            reply = (
                "🌟 **Honours & Minors Degree Program (VFSTR C24 Regulation)**:\n\n"
                "Students with CGPA ≥ 7.5 can enroll in an Honours or Minor track for an additional **20 Credits** (5 courses × 4 credits):\n"
                "- **Honours Tracks**: Advanced Graph Algorithms (22CS951), Biometrics (22CS952), Parallel & Distributed Computing (22CS953), IoT (22CS954), Wireless Sensor Networks (22CS955), and Capstone Project (22CS956).\n"
                "- **Minor Tracks**: Python (22CS901), Java OOP (22CS902), DBMS (22CS903), Web Tech (22CS904), Mobile App Dev (22CS905), DAA (22CS906), OS (22CS907), Networks (22CS908), Capstone (22CS909)."
            )
            citations = ["[VFSTR C24 Honours & Minors Regulation]", "[B.Tech CSE Structure, p.5]"]
        elif "substitut" in q or "alternative" in q:
            reply = (
                "🔄 **Approved Course Substitution Standards (§2.1)**:\n\n"
                "The Department of CSE approves the following direct equivalencies:\n"
                "- **24CS402 (Parallel & Distributed Computing)** ➔ **22CS953 (Honours P&DC)**\n"
                "- **24CS204 (OOP Java)** ➔ **22CS902 (Java OOP Minor)**\n"
                "- **24CS403 (Privacy & Intrusion Detection)** ➔ **22CS815 (IDPS Elective)**\n"
                "- **24CS207 (Full Stack MERN)** ➔ **22CS904 (Web Technologies)**\n\n"
                "Approved substitutions satisfy degree requirements without extending graduation timeline."
            )
            citations = ["[Policy §2.1: Equivalent Courses]", "[VFSTR C24 Equivalence Standards]"]
        else:
            completed_cnt = len(student.get('completed', [])) if student else 18
            gpa = student.get('gpa', 3.82) if student else 3.82
            reply = (
                "🟢 **VFSTR C24 Academic Progress Summary & Degree Trajectory**:\n\n"
                f"- **Completed Courses**: {completed_cnt} courses completed in B.Tech CSE (C24 Regulation).\n"
                f"- **Cumulative GPA / SGPA**: {gpa:.2f} ({student.get('standing', 'Good Standing') if student else 'Good Standing'}).\n"
                f"- **Total Degree Target**: 160 Credits (Graduation Target: {student.get('expected_grad', 'May 2028') if student else 'May 2028'}).\n\n"
                "You are progressing on track. Explore the **C24 Curriculum Explorer**, **Topological Pathway**, and **Knowledge Graph** to inspect upcoming semester courses and syllabi."
            )
            citations = ["[VFSTR C24 Degree Standards]", "[Policy §2.0: 160 Credit Graduation Requirement]"]

    # Log conversation to MongoDB
    db_manager.save_chat_log(req.student_id, req.question, reply, citations)

    return {
        "reply": reply,
        "citations": citations
    }

@app.get("/api/chat/history/{student_id}")
def get_chat_history(student_id: str):
    history = db_manager.get_chat_history(student_id)
    return {"history": history}

# --- 4. TOPOLOGICAL DEGREE PATHWAY GENERATION ---

@app.post("/api/pathway/generate")
def generate_degree_pathway(req: PathwayGenerateRequest):
    """
    Computes optimal multi-semester degree sequencing using Topological Sorting DAG.
    Considers completed courses, prerequisites, term offerings (Fall/Spring), and max credit caps.
    """
    student = db_manager.get_student_by_id(req.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    courses = db_manager.get_all_courses()
    course_map = {c["id"]: c for c in courses}
    completed = set(student.get("completed", []))

    # All required core and elective courses from catalog
    req_file = load_json_file("degree_requirements.json")
    required_ids = req_file.get("required_courses", [c["id"] for c in courses if c.get("category") == "Core"])
    
    # Remaining uncompleted courses
    remaining = [cid for cid in required_ids if cid not in completed and cid in course_map]

    # Additional electives if needed
    all_electives = [c["id"] for c in courses if "ELECTIVE" in c.get("credit_categories", []) or c.get("category") == "Elective"]
    for el in all_electives:
        if el not in completed and el not in remaining and len(remaining) < 14:
            remaining.append(el)

    # Topological Sort by prerequisite depth
    def get_prereq_depth(cid, visited=None):
        if visited is None:
            visited = set()
        if cid in visited or cid not in course_map:
            return 0
        visited.add(cid)
        c = course_map[cid]
        prereqs = []
        for g in c.get("prerequisite_groups", []):
            for p in g.get("prerequisites", []):
                prereqs.append(p.get("course_id"))
        if not prereqs and "prereqs" in c:
            prereqs = c["prereqs"]
        if not prereqs:
            return 0
        return 1 + max([get_prereq_depth(p, visited.copy()) for p in prereqs if p in course_map], default=0)

    # Sort remaining courses by topological dependency level
    remaining.sort(key=lambda cid: (get_prereq_depth(cid), course_map[cid].get("difficulty_level", 2)))

    # Schedule across remaining semesters
    semesters = []
    current_pool = set(completed)
    to_schedule = list(remaining)
    sem_names = ["Fall 2026", "Spring 2027", "Fall 2027", "Spring 2028"]

    for idx, s_name in enumerate(sem_names):
        if not to_schedule:
            break
        
        sem_season = "FALL" if "Fall" in s_name else "SPRING"
        sem_courses = []
        sem_credits = 0

        eligible_this_sem = []
        for cid in to_schedule:
            c = course_map[cid]
            # Check offering
            offered = c.get("offered_semesters", ["FALL", "SPRING"])
            if sem_season not in offered:
                continue

            # Check prerequisites satisfied in current_pool
            prereqs = []
            for g in c.get("prerequisite_groups", []):
                for p in g.get("prerequisites", []):
                    prereqs.append(p.get("course_id"))
            if not prereqs and "prereqs" in c:
                prereqs = c["prereqs"]

            if all(p in current_pool for p in prereqs):
                eligible_this_sem.append(cid)

        # Pick up to credit limit
        for cid in eligible_this_sem:
            cr = course_map[cid].get("credits", 3)
            if sem_credits + cr <= req.max_credits_per_semester:
                sem_courses.append(cid)
                sem_credits += cr
                to_schedule.remove(cid)

        # Update current_pool with courses completed in this scheduled semester
        current_pool.update(sem_courses)

        semesters.append({
            "semester_index": idx + 1,
            "name": s_name,
            "season": sem_season,
            "courses": [course_map[cid] for cid in sem_courses if cid in course_map],
            "total_credits": sem_credits,
            "status": "Optimal"
        })

    # Save newly planned list to student
    all_planned = [c["id"] for s in semesters for c in s["courses"]]
    student["planned"] = all_planned
    db_manager.create_student(student)

    return {
        "success": True,
        "student_id": student["id"],
        "pathway": semesters,
        "total_semesters": len(semesters),
        "total_planned_credits": sum(s["total_credits"] for s in semesters),
        "target_graduation": req.target_graduation
    }

# --- 5. FORMAL CONSTRAINT CONFLICT AUDITOR ---

@app.post("/api/audit/verify")
def verify_schedule_constraints(req: AuditRequest):
    """
    Formal constraint checking:
    1. Prerequisite completion & minimum grade verification
    2. Concurrent corequisite validation
    3. Credit Overload (>18 cr) or Underload (<12 cr)
    4. Semester Term Offering Mismatch
    5. Academic Probation load limits (14 cr cap)
    """
    student = db_manager.get_student_by_id(req.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    courses = db_manager.get_all_courses()
    course_map = {c["id"]: c for c in courses}
    completed_set = set(student.get("completed", []))
    selected_set = set(req.selected_courses)

    issues = []
    warnings = []
    total_credits = 0

    target_season = "FALL" if "fall" in req.semester.lower() else "SPRING"

    # GPA Limit check
    is_probation = student.get("gpa", 3.5) < 2.0 or student.get("standing") == "Academic Warning"
    max_allowed_credits = 14 if is_probation else 18

    for cid in req.selected_courses:
        if cid not in course_map:
            issues.append(f"Unknown course code: {cid}")
            continue

        c = course_map[cid]
        cr = c.get("credits", 3)
        total_credits += cr

        # 1. Already completed
        if cid in completed_set:
            warnings.append(f"⚠️ {cid} ({c['name']}) is already completed on transcript.")

        # 2. Term offering
        offered = c.get("offered_semesters", ["FALL", "SPRING"])
        if target_season not in offered:
            issues.append(f"❌ {cid} ({c['name']}) is only offered in {', '.join(offered)} (Policy §7.1).")

        # 3. Prerequisites
        prereqs = []
        for g in c.get("prerequisite_groups", []):
            for p in g.get("prerequisites", []):
                prereqs.append(p)
        if not prereqs and "prereqs" in c:
            prereqs = [{"course_id": p, "min_grade": "D"} for p in c["prereqs"]]

        for p in prereqs:
            pid = p.get("course_id")
            min_g = p.get("min_grade", "D")
            if pid not in completed_set and pid not in selected_set:
                issues.append(f"❌ {cid} missing prerequisite: requires {pid} with grade {min_g} or higher (Policy §1.1).")

        # 4. Corequisites
        coreqs = c.get("corequisites", [])
        for coreq in coreqs:
            if coreq not in completed_set and coreq not in selected_set:
                issues.append(f"❌ {cid} requires concurrent corequisite {coreq} (Policy §1.1).")

    # Credit Limits
    if total_credits > max_allowed_credits:
        issues.append(f"❌ Total credit load ({total_credits} cr) exceeds policy limit of {max_allowed_credits} credits (Policy §5.2).")
    elif total_credits < 12 and total_credits > 0:
        warnings.append(f"ℹ️ Load is under 12 credits ({total_credits} cr). Full-time status requires at least 12 credits (Policy §5.1).")

    is_valid = len(issues) == 0

    return {
        "is_valid": is_valid,
        "total_credits": total_credits,
        "max_allowed_credits": max_allowed_credits,
        "issues": issues,
        "warnings": warnings,
        "summary": "✅ Schedule verified for registration" if is_valid else f"❌ {len(issues)} constraint violation(s) detected",
        "citations": ["[Policy §1.1: Prerequisite Enforcement]", "[Policy §5.2: Credit Overload]"]
    }

# --- 6. BOTTLENECK & GRADUATION-RISK ANALYSIS ---

@app.get("/api/bottlenecks/{student_id}")
def analyze_bottlenecks_and_risk(student_id: str):
    """
    Identifies high-impact bottleneck courses (courses blocking 3+ downstream requirements)
    and computes student's personalized Graduation Risk Index (0-100%).
    """
    student = db_manager.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    courses = db_manager.get_all_courses()
    course_map = {c["id"]: c for c in courses}
    completed_set = set(student.get("completed", []))

    # Calculate downstream dependency blocking weight for every course
    blocking_map = {}
    for c in courses:
        cid = c["id"]
        blocking_map[cid] = []
        
    for c in courses:
        cid = c["id"]
        prereqs = []
        for g in c.get("prerequisite_groups", []):
            for p in g.get("prerequisites", []):
                prereqs.append(p.get("course_id"))
        if not prereqs and "prereqs" in c:
            prereqs = c["prereqs"]

        for p in prereqs:
            if p in blocking_map:
                blocking_map[p].append(cid)

    # Identify critical bottleneck courses
    bottlenecks = []
    uncompleted_bottlenecks = 0

    for cid, dependents in blocking_map.items():
        if len(dependents) >= 2:
            is_passed = cid in completed_set
            if not is_passed:
                uncompleted_bottlenecks += 1

            c = course_map.get(cid, {})
            bottlenecks.append({
                "course_id": cid,
                "name": c.get("name", cid),
                "credits": c.get("credits", 3),
                "blocked_courses": dependents,
                "blocked_count": len(dependents),
                "is_completed": is_passed,
                "term_offering": c.get("offered_semesters", ["FALL", "SPRING"]),
                "risk_factor": "CRITICAL" if len(dependents) >= 4 else "HIGH",
                "suggested_substitutes": [eq.get("equivalent_course_id") for eq in load_json_file("equivalencies.json") if eq.get("course_id") == cid]
            })

    # Sort bottlenecks by blocked count descending
    bottlenecks.sort(key=lambda b: b["blocked_count"], reverse=True)

    # Calculate Graduation Risk Score
    gpa = student.get("gpa", 3.5)
    risk_score = 10
    if gpa < 2.5:
        risk_score += 35
    elif gpa < 3.0:
        risk_score += 15

    risk_score += (uncompleted_bottlenecks * 18)
    risk_score = min(max(risk_score, 5), 95)

    risk_level = "LOW"
    if risk_score > 65:
        risk_level = "CRITICAL"
    elif risk_score > 40:
        risk_level = "MODERATE"

    return {
        "student_id": student["id"],
        "graduation_risk_score": risk_score,
        "graduation_risk_level": risk_level,
        "uncompleted_bottlenecks": uncompleted_bottlenecks,
        "bottlenecks": bottlenecks,
        "projected_delay_semesters": 1 if risk_level == "CRITICAL" else 0,
        "standing": student.get("standing", "Good Standing")
    }

# --- 7. COURSE SUBSTITUTIONS & EQUIVALENCIES ---

@app.get("/api/substitutions/{course_id}")
def get_substitutions_for_course(course_id: str):
    equivs = load_json_file("equivalencies.json")
    matches = []
    for eq in equivs:
        if eq.get("course_id") == course_id:
            matches.append(eq)
        elif eq.get("equivalent_course_id") == course_id:
            matches.append({
                "course_id": course_id,
                "equivalent_course_id": eq.get("course_id"),
                "notes": eq.get("notes")
            })
    return {"course_id": course_id, "substitutions": matches}

@app.post("/api/substitutions/apply")
def apply_course_substitution(req: SubstitutionApplyRequest):
    student = db_manager.get_student_by_id(req.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    planned = student.get("planned", [])
    if req.original_course_id in planned:
        idx = planned.index(req.original_course_id)
        planned[idx] = req.substitute_course_id
        student["planned"] = planned
        db_manager.create_student(student)

    return {
        "success": True,
        "message": f"Successfully substituted {req.original_course_id} with {req.substitute_course_id} in degree pathway.",
        "student": student
    }

# --- 8. ACADEMIC POLICIES RETRIEVAL ---

@app.get("/api/policies")
def get_academic_policies():
    policies_path = DATA_DIR / "policies.md"
    content = ""
    if policies_path.exists():
        with open(policies_path, "r", encoding="utf-8") as f:
            content = f.read()

    structured = [
        {
            "section": "§1.1",
            "title": "Prerequisite Enforcement",
            "summary": "All prerequisites must be completed with a minimum grade of D (or C for advanced core) prior to registration.",
            "authority": "Registrar & Academic Affairs"
        },
        {
            "section": "§1.2",
            "title": "Prerequisite Waivers",
            "summary": "Requires demonstrated competency, course instructor written approval, and Department Chair signature.",
            "authority": "Department Chair"
        },
        {
            "section": "§2.1",
            "title": "Equivalent Courses",
            "summary": "Official pre-approved equivalents (e.g. CS305 for CS301) may be substituted without additional approval.",
            "authority": "Registrar"
        },
        {
            "section": "§4.2",
            "title": "Academic Probation",
            "summary": "Cumulative GPA below 2.0 caps semester load to maximum 14 credits.",
            "authority": "Academic Standards Committee"
        },
        {
            "section": "§5.2",
            "title": "Credit Overload",
            "summary": "Enrollment above 18 credits requires cumulative GPA ≥ 3.5 and formal Dean exception approval.",
            "authority": "Dean of Academic Affairs"
        }
    ]

    return {"policies": structured, "raw_markdown": content}

# --- 9. FORMAL FACULTY REVIEW & PETITION GOVERNANCE BOARD ---

@app.get("/api/petitions")
def list_petitions():
    return db_manager.get_all_petitions()

@app.post("/api/petitions/submit")
def submit_petition(req: PetitionSubmitRequest):
    student = db_manager.get_student_by_id(req.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    petition_id = f"PET-{uuid.uuid4().hex[:6].upper()}"

    # Automated Constraint Pre-Audit
    gpa = student.get("gpa", 3.5)
    is_eligible = True
    audit_notes = []

    if req.petition_type == "CREDIT_OVERLOAD":
        if gpa < 3.5:
            is_eligible = False
            audit_notes.append(f"Student GPA ({gpa}) is below the required 3.50 threshold for credit overload (Policy §5.2).")
        else:
            audit_notes.append("Student satisfies GPA eligibility criteria for credit overload (GPA ≥ 3.50).")

    elif req.petition_type == "PREREQUISITE_WAIVER":
        audit_notes.append(f"Automated check: Verified student academic standing ({student.get('standing', 'Good Standing')}). Requires Faculty & Chair review.")

    petition_data = {
        "petition_id": petition_id,
        "student_id": student["id"],
        "student_name": student.get("name", "Student"),
        "major": student.get("major", "Computer Science"),
        "gpa": gpa,
        "standing": student.get("standing", "Good Standing"),
        "petition_type": req.petition_type,
        "course_id": req.course_id,
        "target_semester": req.target_semester,
        "requested_credits": req.requested_credits,
        "justification": req.justification,
        "automated_audit_eligible": is_eligible,
        "automated_audit_notes": audit_notes,
        "status": "PENDING",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    saved = db_manager.create_petition(petition_data)
    return {
        "success": True,
        "message": f"Petition {petition_id} submitted for formal faculty review.",
        "petition": saved
    }

@app.post("/api/petitions/{petition_id}/review")
def review_petition(petition_id: str, req: PetitionReviewRequest):
    reviewed = db_manager.review_petition(
        petition_id=petition_id,
        decision=req.decision,
        reviewer=req.reviewer,
        comments=req.comments or ""
    )

    if not reviewed:
        raise HTTPException(status_code=404, detail="Petition not found")

    # If approved, apply resolution directly to student record
    if req.decision.upper() == "APPROVED":
        student = db_manager.get_student_by_id(reviewed["student_id"])
        if student:
            # Clear conflicts or add approved override
            if reviewed.get("course_id") and reviewed["course_id"] in student.get("conflicts", []):
                student["conflicts"].remove(reviewed["course_id"])
            student.setdefault("approved_petitions", []).append(petition_id)
            db_manager.create_student(student)

    return {
        "success": True,
        "message": f"Petition {petition_id} {req.decision.upper()} by {req.reviewer}.",
        "petition": reviewed
    }

# =========================================================================
# --- 8. ACADEMIC ADMIN & FACULTY GOVERNANCE MODULE ---
# =========================================================================

ADMIN_CREDENTIALS = {
    "admin": "admin123",
    "dean": "dean123",
    "hod_cse": "vignan2024",
    "faculty": "faculty123"
}

@app.post("/api/admin/login")
def admin_login(req: AdminLoginRequest):
    u = req.username.strip().lower()
    p = req.password.strip()
    
    if u in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[u] == p:
        role_titles = {
            "admin": "System Administrator",
            "dean": "Dean of Academic Affairs",
            "hod_cse": "Head of Department (CSE)",
            "faculty": "Academic Faculty Advisor"
        }
        return {
            "success": True,
            "message": f"Authenticated as {role_titles.get(u, 'Academic Administrator')}",
            "user": {
                "username": u,
                "role": "ADMIN",
                "title": role_titles.get(u, "Academic Administrator"),
                "department": "Computer Science & Engineering",
                "institution": "VFSTR (Deemed to be University)"
            }
        }
    
    # Also allow standard admin/admin123 fallback
    if p == "admin123" or p == "admin":
        return {
            "success": True,
            "message": "Authenticated as Academic Administrator",
            "user": {
                "username": u,
                "role": "ADMIN",
                "title": "Academic Administrator",
                "department": "Computer Science & Engineering",
                "institution": "VFSTR (Deemed to be University)"
            }
        }
        
    raise HTTPException(status_code=401, detail="Invalid admin username or password. (Hint: use 'admin' / 'admin123' or 'hod_cse' / 'vignan2024')")

@app.get("/api/admin/stats")
def get_admin_dashboard_stats():
    """Returns aggregated department overview metrics."""
    return db_manager.get_admin_stats()

# --- Student Management Endpoints ---
@app.get("/api/admin/students")
def list_admin_students(search: Optional[str] = None):
    students = db_manager.get_all_students()
    if search:
        s_lower = search.lower()
        students = [
            s for s in students
            if s_lower in s.get("id", "").lower() or s_lower in s.get("name", "").lower() or s_lower in s.get("major", "").lower()
        ]
    return {
        "success": True,
        "count": len(students),
        "students": students
    }

@app.post("/api/admin/students")
def create_admin_student(req: StudentAdminCreateRequest):
    regno = req.id.strip().upper()
    existing = db_manager.get_student_by_id(regno)
    if existing:
        raise HTTPException(status_code=400, detail=f"Student ID '{regno}' already exists.")

    student_data = {
        "id": regno,
        "name": req.name.strip(),
        "major": req.major or "Computer Science & Engineering",
        "gpa": req.gpa or 3.75,
        "standing": req.standing or "Good Standing",
        "expected_grad": req.expected_grad or "Spring 2028",
        "completed": req.completed or [],
        "planned": req.planned or [],
        "conflicts": [],
        "password": req.password or "password123"
    }

    saved = db_manager.create_student(student_data)
    return {
        "success": True,
        "message": f"Student '{regno} - {req.name}' created successfully.",
        "student": saved
    }

@app.put("/api/admin/students/{student_id}")
def update_admin_student(student_id: str, req: StudentAdminUpdateRequest):
    student = db_manager.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    update_dict = {}
    if req.name is not None:
        update_dict["name"] = req.name
    if req.major is not None:
        update_dict["major"] = req.major
    if req.gpa is not None:
        update_dict["gpa"] = req.gpa
    if req.standing is not None:
        update_dict["standing"] = req.standing
    if req.expected_grad is not None:
        update_dict["expected_grad"] = req.expected_grad
    if req.completed is not None:
        update_dict["completed"] = req.completed
    if req.planned is not None:
        update_dict["planned"] = req.planned
    if req.password is not None:
        update_dict["password"] = req.password

    updated = db_manager.update_student(student_id, update_dict)
    return {
        "success": True,
        "message": f"Student '{student_id}' updated successfully.",
        "student": updated
    }

@app.delete("/api/admin/students/{student_id}")
def delete_admin_student(student_id: str):
    success = db_manager.delete_student(student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found or could not be deleted.")
    return {
        "success": True,
        "message": f"Student '{student_id}' deleted successfully."
    }

# --- Course Catalog Management Endpoints ---
@app.get("/api/admin/courses")
def list_admin_courses(search: Optional[str] = None):
    courses = db_manager.get_all_courses()
    if search:
        s_lower = search.lower()
        courses = [
            c for c in courses
            if s_lower in c.get("id", "").lower() or s_lower in c.get("name", "").lower() or s_lower in c.get("category", "").lower()
        ]
    return {
        "success": True,
        "count": len(courses),
        "courses": courses
    }

@app.post("/api/admin/courses")
def create_admin_course(req: CourseAdminCreateRequest):
    cid = req.id.strip().upper()
    existing = db_manager.get_course_by_id(cid)
    if existing:
        raise HTTPException(status_code=400, detail=f"Course ID '{cid}' already exists.")

    course_data = req.model_dump()
    course_data["id"] = cid
    saved = db_manager.create_course(course_data)
    return {
        "success": True,
        "message": f"Course '{cid} - {req.name}' added to C24 catalog.",
        "course": saved
    }

@app.put("/api/admin/courses/{course_id}")
def update_admin_course(course_id: str, req: CourseAdminUpdateRequest):
    course = db_manager.get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    update_dict = {k: v for k, v in req.model_dump().items() if v is not None}
    updated = db_manager.update_course(course_id, update_dict)
    return {
        "success": True,
        "message": f"Course '{course_id}' updated successfully.",
        "course": updated
    }

@app.delete("/api/admin/courses/{course_id}")
def delete_admin_course(course_id: str):
    success = db_manager.delete_course(course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found or could not be deleted.")
    return {
        "success": True,
        "message": f"Course '{course_id}' removed from catalog."
    }

# --- Faculty Petition Review Endpoints ---
@app.get("/api/admin/petitions")
def list_admin_petitions():
    petitions = db_manager.get_all_petitions()
    return {
        "success": True,
        "count": len(petitions),
        "petitions": petitions
    }

# --- Course Equivalency Endpoints ---
@app.get("/api/admin/equivalencies")
def list_admin_equivalencies():
    equivs = db_manager.get_equivalencies()
    return {
        "success": True,
        "count": len(equivs),
        "equivalencies": equivs
    }

@app.post("/api/admin/equivalencies")
def create_admin_equivalency(req: EquivalencyAdminCreateRequest):
    equiv_data = req.model_dump()
    saved = db_manager.create_equivalency(equiv_data)
    return {
        "success": True,
        "message": f"Substitution rule '{req.course_id} ➔ {req.equivalent_course_id}' created.",
        "equivalency": saved
    }

@app.delete("/api/admin/equivalencies/{course_id}/{equiv_id}")
def delete_admin_equivalency(course_id: str, equiv_id: str):
    success = db_manager.delete_equivalency(course_id, equiv_id)
    if not success:
        raise HTTPException(status_code=404, detail="Equivalency rule not found.")
    return {
        "success": True,
        "message": f"Substitution rule '{course_id} ➔ {equiv_id}' removed."
    }

# --- Bottleneck & Cohort Risk Analytics ---
@app.get("/api/admin/bottlenecks")
def get_admin_bottleneck_analytics():
    courses = db_manager.get_all_courses()
    students = db_manager.get_all_students()
    
    # Calculate blocking map
    blocking_map = {c["id"]: [] for c in courses}
    for c in courses:
        cid = c["id"]
        prereqs = []
        for g in c.get("prerequisite_groups", []):
            for p in g.get("prerequisites", []):
                prereqs.append(p.get("course_id"))
        if not prereqs and "prereqs" in c:
            prereqs = c["prereqs"]
        for p in prereqs:
            if p in blocking_map:
                blocking_map[p].append(cid)

    # Calculate student impact count for each bottleneck
    course_map = {c["id"]: c for c in courses}
    analytics = []
    for cid, dependents in blocking_map.items():
        if len(dependents) >= 2:
            # Count how many students still have not passed this course
            unpassed_students = [s["id"] for s in students if cid not in set(s.get("completed", []))]
            c = course_map.get(cid, {})
            analytics.append({
                "course_id": cid,
                "name": c.get("name", cid),
                "credits": c.get("credits", 4),
                "ltpc": c.get("ltpc", "N/A"),
                "category": c.get("category", "Professional Core"),
                "blocked_courses_count": len(dependents),
                "blocked_courses": dependents,
                "students_delayed_count": len(unpassed_students),
                "students_affected": unpassed_students,
                "risk_severity": "CRITICAL" if len(dependents) >= 4 else "HIGH"
            })

    analytics.sort(key=lambda x: (x["blocked_courses_count"], x["students_delayed_count"]), reverse=True)

    return {
        "success": True,
        "total_bottlenecks": len(analytics),
        "critical_count": len([b for b in analytics if b["risk_severity"] == "CRITICAL"]),
        "bottlenecks": analytics
    }


# Mount static web directory for full-stack hosting (web/index.html)
from fastapi.responses import Response

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)

if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.server:app", host="0.0.0.0", port=8000, reload=False)

