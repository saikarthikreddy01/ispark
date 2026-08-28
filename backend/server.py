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
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:3000"],
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

class StudentProfileUpdateRequest(BaseModel):
    academic_history: List[Dict]
    career_goals: Optional[List[str]] = None

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
    students = db_manager.get_all_students()
    for s in students:
        s.pop("password", None)
    return students

@app.get("/api/student/{student_id}")
def get_student(student_id: str):
    student = db_manager.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.pop("password", None)
    return student

@app.put("/api/student/{student_id}/profile")
def update_student_profile(student_id: str, request: StudentProfileUpdateRequest):
    student = db_manager.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Validation variables
    total_points = 0.0
    total_credits = 0
    completed_courses = []
    
    ALLOWED_GRADES = {"O", "A+", "A", "B+", "B", "C", "P", "F"}
    
    for semester in request.academic_history:
        for course in semester.get("courses", []):
            try:
                credits = float(course.get("credits", 0))
                gpa = float(course.get("gpa", 0))
                
                # Validation: Reject <0 or >10
                if gpa < 0 or gpa > 10:
                    raise HTTPException(status_code=400, detail="GPA must be between 0.0 and 10.0")
                
                # Validation: Grade required, non-empty, allowed values
                raw_grade = course.get("grade", "")
                if not raw_grade or not raw_grade.strip():
                    raise HTTPException(status_code=400, detail="Grade is required and cannot be empty")
                
                grade = raw_grade.strip().upper()
                if grade not in ALLOWED_GRADES:
                    raise HTTPException(status_code=400, detail=f"Invalid grade: {grade}. Allowed: O, A+, A, B+, B, C, P, F")
                
                course["grade"] = grade # Trimmed and uppercased
                
                total_credits += int(credits)
                total_points += credits * gpa
                if course.get("code"):
                    completed_courses.append(course.get("code"))
            except ValueError:
                continue
                
    new_gpa = round(total_points / total_credits, 2) if total_credits > 0 else student.get("gpa", 0)
    
    update_data = {
        "academic_history": request.academic_history,
        "gpa": new_gpa,
        "completed": completed_courses
    }
    
    if request.career_goals is not None:
        update_data["career_goals"] = request.career_goals
        
    updated = db_manager.update_student(student_id, update_data)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update profile")
    return {"message": "Profile updated successfully", "student": updated}

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
    if stored_pwd and req.password != stored_pwd:
        raise HTTPException(status_code=401, detail="Incorrect password.")

    student.pop("password", None)

    return {
        "success": True,
        "message": f"Welcome back, {student.get('name', regno)}!",
        "student": student
    }

@app.post("/api/auth/logout")
def logout():
    return {"success": True, "message": "Logged out successfully"}

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
    return {
        "status": "connected" if api_key else "disconnected",
        "model": "gemini-3.6-flash",
        "mode": "real_time_graph_rag",
        "live_interaction": True
    }
# --- 3. GRAPH-RAG ADVISING WITH CITATIONS ---

# Global advisor instance for caching
_advisor_instance = None

@app.post("/api/chat")
def advisor_chat(req: ChatRequest):
    global _advisor_instance
    student = db_manager.get_student_by_id(req.student_id)
    
    try:
        if _advisor_instance is None:
            from src.agents.orchestrator import AcademicAdvisor
            _advisor_instance = AcademicAdvisor()
            
        result = _advisor_instance.chat_sync(req.question, student=student)
        
        reply = result.get("response", "I could not generate a response.")
        citations = result.get("citations", [])
        tool = result.get("query_type", "general")
        
        # Log to DB
        db_manager.save_chat_log(
            req.student_id, req.question, reply, 
            [c.get("reference") if isinstance(c, dict) else c for c in citations]
        )

        return {
            "reply": reply,
            "citations": citations,
            "tool_executed": tool
        }
    except Exception as e:
        print(f"[ERROR] Graph-RAG failure: {e}")
        return {
            "reply": f"⚠️ An error occurred during Graph-RAG verification: {e}",
            "citations": [],
            "tool_executed": "error"
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

    # All required core and elective courses from catalog structure
    req_file = load_json_file("degree_requirements.json")
    
    structure_required = []
    for sem in req_file.get("semesters_structure", []):
        structure_required.extend(sem.get("courses", []))
    
    required_ids = structure_required
    
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

    # Schedule across remaining semesters dynamically
    semesters = []
    current_pool = set(completed)
    to_schedule = list(remaining)
    
    import datetime
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    
    # Start next available major semester
    start_season = "FALL" if current_month >= 6 else "SPRING"
    start_year = current_year if current_month >= 6 else current_year
    
    sem_idx = 0
    max_semesters = 12
    
    while to_schedule and sem_idx < max_semesters:
        if start_season == "FALL":
            sem_season = "FALL" if sem_idx % 2 == 0 else "SPRING"
            sem_year = start_year + (sem_idx // 2) if sem_season == "FALL" else start_year + (sem_idx // 2) + 1
        else:
            sem_season = "SPRING" if sem_idx % 2 == 0 else "FALL"
            sem_year = start_year + (sem_idx // 2) if sem_season == "SPRING" else start_year + (sem_idx // 2)

        s_name = f"{sem_season.capitalize()} {sem_year}"
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

        # If no courses could be scheduled this semester, we might be stuck in a prerequisite deadlock, but we shouldn't infinite loop. 
        # Actually, advancing the semester season might unlock spring-only or fall-only courses, so we let it continue until max_semesters.
        
        # Update current_pool with courses completed in this scheduled semester
        current_pool.update(sem_courses)

        if sem_courses:
            semesters.append({
                "semester_index": sem_idx + 1,
                "name": s_name,
                "season": sem_season,
                "courses": [course_map[cid] for cid in sem_courses if cid in course_map],
                "total_credits": sem_credits,
                "status": "Optimal"
            })
        sem_idx += 1

    # Save newly planned list to student
    all_planned = [c["id"] for s in semesters for c in s["courses"]]
    student["planned"] = all_planned
    db_manager.create_student(student)

    return {
        "success": len(to_schedule) == 0,
        "student_id": student["id"],
        "pathway": semesters,
        "total_semesters": len(semesters),
        "total_planned_credits": sum(s["total_credits"] for s in semesters),
        "target_graduation": req.target_graduation,
        "unscheduled_courses": to_schedule
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
        # Each group in prerequisite_groups is an AND condition.
        # Within a group, the prerequisites are OR conditions.
        prereq_groups = c.get("prerequisite_groups", [])
        
        # Fallback if old format is used
        if not prereq_groups and "prereqs" in c:
            prereq_groups = [{"prerequisites": [{"course_id": p, "min_grade": "D"}]} for p in c["prereqs"]]

        petitions = db_manager.get_all_petitions()

        for group_idx, g in enumerate(prereq_groups):
            group_satisfied = False
            missing_options = []
            
            for p in g.get("prerequisites", []):
                pid = p.get("course_id")
                min_g = p.get("min_grade", "D")
                
                # Check for waiver
                has_waiver = any(
                    pt.get("student_id") == req.student_id and 
                    pt.get("status") == "APPROVED" and 
                    pt.get("course_id") == cid and 
                    pt.get("petition_type") == "PREREQUISITE_WAIVER" and 
                    (pid in pt.get("justification", "") or pid in pt.get("waived_rule", ""))
                    for pt in petitions
                )
                
                if has_waiver:
                    group_satisfied = True
                    break
                    
                if pid in completed_set:
                    # Check achieved grade if academic_history is present
                    achieved_grade = None
                    for sem in student.get("academic_history", []):
                        for c_hist in sem.get("courses", []):
                            if c_hist.get("course_id") == pid:
                                achieved_grade = c_hist.get("grade")
                                break
                    
                    if achieved_grade and min_g:
                        # Simple grade comparison (A, B, C, D, E, F)
                        grade_rank = {"O": 10, "S": 9, "A": 8, "B": 7, "C": 6, "D": 5, "E": 4, "F": 0, "P": 5}
                        if grade_rank.get(achieved_grade, 0) >= grade_rank.get(min_g, 0):
                            group_satisfied = True
                            break
                        else:
                            # They took it but failed to meet the minimum grade
                            pass
                    else:
                        # If no history is present, we assume it's passed since it's in completed
                        group_satisfied = True
                        break
                
                if p.get("can_be_concurrent") and pid in selected_set:
                    group_satisfied = True
                    break
                    
                missing_options.append(f"{pid} (min grade {min_g})")
            
            if not group_satisfied:
                if len(missing_options) == 1:
                    issues.append(f"❌ {cid} missing prerequisite: requires {missing_options[0]} prior to enrollment (Policy §1.1).")
                else:
                    options_str = " OR ".join(missing_options)
                    issues.append(f"❌ {cid} missing prerequisite group: requires one of [{options_str}] prior to enrollment (Policy §1.1).")

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
    if req.original_course_id not in planned:
        raise HTTPException(status_code=400, detail=f"Original course {req.original_course_id} is not in your planned pathway.")

    # Verify approved petition exists for this substitution
    petitions = db_manager.get_all_petitions()
    is_approved = any(
        pt.get("student_id") == req.student_id and 
        pt.get("status") == "APPROVED" and 
        pt.get("petition_type") == "COURSE_SUBSTITUTION" and 
        (req.original_course_id in pt.get("justification", "") or req.original_course_id == pt.get("course_id"))
        for pt in petitions
    )

    if not is_approved:
        raise HTTPException(status_code=403, detail="Substitution denied: Requires an approved faculty petition.")

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
        
    raise HTTPException(status_code=401, detail="Invalid admin username or password.")

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

