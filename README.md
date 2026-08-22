# 🎓 Academic AI Advisor — 3D Graph-RAG Platform
### Decentralized Academic Advising, Multi-Semester Degree Sequencing & Prerequisite Constraint Auditor
#### *Powered by VFSTR Deemed to be University C24 Curriculum (B.Tech Computer Science & Engineering)*

> **GitHub Repository**: [https://github.com/saikarthikreddy01/ispark](https://github.com/saikarthikreddy01/ispark)

---

## 📌 Executive Summary

**Academic AI Advisor** is an intelligent academic advising platform engineered to eliminate graduation delays, curriculum bottlenecks, and manual scheduling conflicts. Built upon the official **VFSTR C24 Regulation Curriculum (160 Credits)**, the system combines **3D Interactive Visualizations**, **Prerequisite Knowledge Graph DAGs (Directed Acyclic Graphs)**, **Topological Multi-Semester Pathway Sequencing**, and **Citation-Grounded Graph-RAG AI Advising** powered by Google Gemini and MongoDB Atlas.

---

## 🛠️ Complete Technology Stack

`
                                  TECH STACK OVERVIEW
┌───────────────────────────────────────────────────────────────────────────────────┐
│  FRONTEND PRESENTATION & VISUALIZATION LAYER                                      │
│  ├── HTML5 / Modern CSS3 (Glassmorphism, CSS Grid, Responsive Flexbox)            │
│  ├── JavaScript ES6+ (Fetch API, Web Storage, Canvas 2D / WebGL)                  │
│  ├── Three.js r128 (3D Geodesic Lattice, Vertex Wave Shaders, Parallax Physics)   │
│  └── Vis.js Network v9.1.2 (Interactive Prerequisite DAGs & Physics Simulation)   │
├───────────────────────────────────────────────────────────────────────────────────┤
│  BACKEND APPLICATION & REST API LAYER                                             │
│  ├── Python 3.11+                                                                 │
│  ├── FastAPI 0.115+ (Asynchronous High-Throughput REST Framework)                 │
│  ├── Uvicorn 0.30+ (Lightning-fast ASGI Web Server)                               │
│  └── Pydantic v2 (Strict Request/Response Validation & Data Serialization)        │
├───────────────────────────────────────────────────────────────────────────────────┤
│  GRAPH ALGORITHMS, CONSTRAINTS & MULTI-AGENT LAYER                                │
│  ├── NetworkX 3.3 (Topological Sort, Ancestor/Descendant Closures, DAG Validation)│
│  ├── Formal Constraint Engine (Prerequisite, Corequisite, Credit Overload Caps)   │
│  └── Multi-Agent Framework (Pathway Agent, Conflict Auditor, Risk Evaluator)      │
├───────────────────────────────────────────────────────────────────────────────────┤
│  KNOWLEDGE-GRAPH RAG (RETRIEVAL-AUGMENTED GENERATION) & AI ADVISOR                │
│  ├── Google Gemini 2.5 / 1.5 Flash via google-genai SDK                         │
│  ├── Graph-RAG Hybrid Context Injector (Combines Graph Traversal + Vector Chunks) │
│  └── Policy Citation Verifier (Grounded in VFSTR Vision, PEOs, PSOs & Policies)   │
├───────────────────────────────────────────────────────────────────────────────────┤
│  PERSISTENT DATA & DEPLOYMENT INFRASTRUCTURE                                      │
│  ├── MongoDB Atlas / Local MongoDB 7.0+ via pymongo                             │
│  ├── Docker (Containerized Microservice Runtime)                                  │
│  └── Cloud-Ready (GCP Cloud Run, Render, Railway, AWS ECS)                        │
└───────────────────────────────────────────────────────────────────────────────────┘
`

---

## 🌟 Core System Modules & Features

### 1. 🔮 3D Interactive Geodesic Neural Hero (Three.js)
- Real-time rotating icosahedron lattice with organic vertex oscillation.
- Dynamic mouse cursor parallax tracking with ambient lighting.
- Zero-external CDN latency (bundled local minified engine).

### 2. 🔐 Student Authentication & Transcript Management
- Secure Sign In & Sign Up with persistent MongoDB storage.
- Auto-initialization of student transcripts, completed credits, CGPA, and semester standing.
- Pre-configured with official VFSTR student profile: 241FA04077 - SAI KARTHIK REDDY.

### 3. 🗺️ 8-Semester Interactive Kanban Timeline
- Full visual roadmap of the entire 160-credit degree program (Semesters I-I to IV-II).
- Traffic-light status badges: 🟢 Passed (with grades), 🔵 Planned, 🟡 In-Progress, 🔴 At-Risk.
- Dynamic credit accumulator and graduation progress bar.

### 4. 🕸️ 2D Prerequisite Knowledge Graph DAG (Vis.js + NetworkX)
- Directed Graph visualization connecting 82 C24 courses across Basic Sciences, Core, Electives, Honours, and Minors.
- Real-time bottleneck detection (identifies courses that block >= 3 downstream graduation requirements).
- Live physics simulation, node clustering, and instant course code highlighting.

### 5. 📚 Interactive C24 Curriculum & Syllabus Explorer
- Complete course catalog extracted from the official 202-page VFSTR C24 curriculum document.
- Live category pills: **All**, **I-I** through **IV-II**, **PE** (Professional Electives), **HN** (Honours Track), **MN** (Minors Track), **OE** (Open Electives).
- Rich Course Modal displaying:
  - **L-T-P-C** breakdown (e.g. 2-0-4-4, 3-0-2-4)
  - **Module 1 & Module 2** units with contact hours
  - **Laboratory Practice Experiments**
  - **Bloom's Taxonomy Course Outcomes** (CO1–CO5) mapped to Program Outcomes (POs)
  - **Prescribed Textbooks and Reference Books**

### 6. ⚠️ Formal Constraint & Conflict Auditor
- Enforces institutional rules:
  - **Prerequisite Validation**: Prevents enrollment if prerequisite course or minimum grade is missing.
  - **Credit Load Caps**: Flags overloads (>18 credits/sem) and underloads (<12 credits/sem). Academic probation cap at 14 credits.
  - **Semester Term Matching**: Validates Fall vs. Spring term course offerings.
  - **Automated Equivalency Suggestions**: Suggests approved substitutions (24CS402 -> 22CS953, 24CS204 -> 22CS902).

### 7. 💬 Citation-Traceable Graph-RAG AI Advisor
- Hybrid Retrieval: Combines knowledge graph neighbor subgraphs + vector policy chunks (policies.md).
- Fully grounded responses with verifiable citations (e.g. [VFSTR C24 Regulation §1.1], [Policy §5.2]).
- Auto-generates formal faculty exception memos and waiver petitions.

---

## 🏛️ Official Academic Dataset: VFSTR C24 CSE

- **University**: Vignan's Foundation for Science, Technology & Research (VFSTR Deemed to be University)
- **Program**: B.Tech. Computer Science & Engineering (M.P.C Stream)
- **Regulation**: C24 Curriculum (w.e.f. 2024–28 batch)
- **Graduation Requirement**: **160 Credits**

### Credit Category Breakdown

| Category | Description | Required Credits |
|---|---|:---:|
| **BS** | Basic Sciences (Math, Physics, Chemistry) | 23 |
| **BE** | Basic Engineering (EEE, Graphics, Python, Cyber Security) | 20 |
| **PC** | Professional Core (C, Java, Data Structures, DBMS, DAA, OS, Networks, AI, ML) | 48 |
| **PE** | Department Professional Electives (Deep Learning, Forensics, Security) | 16 |
| **OE** | Open Electives | 9 |
| **HS** | Humanities & Social Sciences (English, Management, Aptitude) | 15 |
| **PR** | Projects & Industrial Internship (Field Project, IDP, Capstone) | 15 |
| **BG** | Binary Grade Mandatory Non-Credit Courses (Induction, UHV, Constitution) | 6 |
| **HN / MN** | Optional Honours Track / Minor Specialization Track | 20 |
| **Total** | **Minimum Degree Credits Required for Graduation** | **160** |

---

## 📂 Project Architecture & Directory Structure

`
├── backend/
│   ├── server.py              # FastAPI application & REST endpoints
│   └── database.py            # MongoDB Atlas connection & dataset seeding
├── data/
│   ├── courses.json           # 82 C24 courses with full module syllabi & outcomes
│   ├── degree_requirements.json # 160-credit B.Tech CSE degree requirements
│   ├── equivalencies.json     # Approved course equivalencies & substitutions
│   ├── policies.md            # VFSTR institutional regulations, vision, PEOs, PSOs
│   └── sample_students.json   # Seed student profiles (e.g., 241FA04077)
├── src/
│   ├── agents/                # Multi-agent orchestrator, conflict & risk agents
│   ├── constraint_engine/     # Prerequisite checker & credit load validator
│   ├── knowledge_graph/       # NetworkX DAG graph builder, queries & visualizer
│   ├── models/                # Pydantic schemas (Course, Student, Pathway)
│   ├── rag/                   # Document loader, vector store, Graph-RAG retriever
│   └── utils/                 # Configuration & environment loader
├── web/ & root:
│   ├── index.html             # Single-page full-stack UI
│   ├── app.js                 # Frontend application logic & API client
│   ├── style.css              # Glassmorphic dark theme stylesheet
│   ├── three.min.js           # Three.js 3D library (bundled)
│   └── vis-network.min.js     # Vis.js network graph library (bundled)
├── Dockerfile                 # Docker container specification
├── requirements.txt           # Python package dependencies
├── .env.example               # Environment variables template
└── README.md                  # System documentation
`

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/courses | Returns all 82 C24 courses with full syllabus details |
| GET | /api/courses/{course_id} | Returns single course syllabus (modules, labs, COs, books) |
| GET | /api/curriculum | Returns 8-semester sequence, electives, honours, minors, requirements |
| GET | /api/equivalencies | Returns approved course equivalency mappings |
| POST | /api/auth/login | Student login authentication |
| POST | /api/auth/signup | New student registration and transcript creation |
| GET | /api/students/{id} | Fetches student profile, transcript, and GPA |
| POST | /api/pathway/generate | Generates optimal topological 8-semester graduation pathway |
| POST | /api/audit/verify | Formal constraint verification (prerequisites, overload, term offerings) |
| GET | /api/bottlenecks/{id} | Calculates critical blocking courses & Graduation Risk Index |
| POST | /api/chat | Citation-grounded Graph-RAG AI advising assistant |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Clone and Setup Environment
`ash
# Clone the repository
git clone https://github.com/saikarthikreddy01/ispark.git
cd ispark

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.env\Scripts\Activate.ps1
# On Linux / macOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
`

### 3. Configure Environment Variables
Copy .env.example to .env and provide your API keys (optional, default fallbacks included):
`ash
cp .env.example .env
`
Contents of .env:
`ini
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-2.5-flash
MONGODB_URI=mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB=academic_advisor
`

### 4. Start the Application Server
`ash
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload
`

### 5. Access the Platform
- 🌐 **Web Interface**: http://localhost:8000
- 📖 **Interactive Swagger API Docs**: http://localhost:8000/docs
- 🧪 **ReDoc Documentation**: http://localhost:8000/redoc

---

## 🐳 Docker Deployment

`ash
# Build Docker image
docker build -t academic-ai-advisor .

# Run container
docker run -p 8080:8080 --env-file .env academic-ai-advisor
`

Access at http://localhost:8080.

---

## 🛡️ License & Institutional Rights

Developed for the **Department of Computer Science & Engineering, VFSTR (Deemed to be University)**.  
Curriculum contents referenced from VFSTR Academic Regulations (C24 / R22 aligned).