# 🎓 Academic AI Advisor — 3D Graph-RAG Platform

> **GitHub Repository**: [https://github.com/Kar93122/ispark](https://github.com/Kar93122/ispark)

---

## 💡 Overview
**Academic AI Advisor** is a decentralized, Graph-RAG-powered academic advising platform designed to eliminate graduation delays. It automates multi-semester degree sequencing, detects hidden prerequisite bottlenecks, audits schedules in real-time, and provides citation-grounded advising chat.

---

## ✨ Core Features

1. **🔮 3D Interactive Geodesic Neural Hero**:
   - Modern Three.js rotating lattice with organic vertex wave physics and real-time cursor parallax.
   - Side-by-side landing layout: 3D diagram on the left, student authentication on the right.

2. **🔐 Student Portal Authentication**:
   - Tabbed Login and Sign Up with automatic profile, transcript, and degree pathway initialization.

3. **🗺️ 8-Semester Kanban Timeline**:
   - Horizontal semester-by-semester course sequencing with traffic-light status indicators (🟢 Passed, 🔵 Planned, 🔴 At-Risk).

4. **🕸️ 2D Prerequisite Knowledge Graph (Vis.js)**:
   - Interactive dependency network DAG with bottleneck detection, physics simulation, and course search.

5. **💬 Citation-Traceable Graph-RAG Advisor**:
   - Intelligent advisor grounded in institutional catalogs with verifiable citations (`[Course Catalog §4.2]`).

6. **⚠️ Schedule Conflict & Overload Auditor**:
   - Real-time constraint checking with 1-click approved course substitutions and waiver requests.

7. **🍃 MongoDB Permanent Database**:
   - High-performance persistence for student accounts, transcripts, course graph catalog, and chat logs.

---

## 🛠️ Architecture & Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Pure Web (HTML5, CSS3, JavaScript ES6+, Three.js, Vis.js) |
| **Backend & Database API** | FastAPI, Python 3.11+, PyMongo |
| **Database** | MongoDB Atlas / Local MongoDB (`academic_advisor`) |
| **AI / Graph-RAG** | Google Gemini, Topological Sort DAGs |

---

## 🚀 Running the Project

### 💻 Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/Kar93122/ispark.git
cd ispark

# 2. Activate virtual environment & install requirements
pip install -r requirements.txt

# 3. Run FastAPI Backend & Full-Stack Server
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000
```

Open:
- Web App: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
