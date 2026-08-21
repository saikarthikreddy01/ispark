# 🎓 Academic AI Advisor — 3D Graph-RAG Platform

> **Live Netlify Production Web App**: [https://teamispark.netlify.app](https://teamispark.netlify.app)  
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
| **Production Frontend** | Pure Web (HTML5, CSS3, JavaScript ES6+, Three.js, Vis.js) |
| **Deployment Platform** | **Netlify** (`https://teamispark.netlify.app`) |
| **Backend & Database API** | FastAPI, Python 3.11+, PyMongo |
| **Database** | MongoDB Atlas / Local MongoDB (`academic_advisor`) |
| **AI / Graph-RAG** | Google Gemini, Topological Sort DAGs |

---

## 🚀 Running the Project

### 🌐 1. Live Cloud Netlify App (No Installation Needed)
Visit: **[https://teamispark.netlify.app](https://teamispark.netlify.app)**

### 💻 2. Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/Kar93122/ispark.git
cd ispark

# 2. Run local web server
python -m http.server 3000

# 3. (Optional) Run FastAPI MongoDB Backend
uvicorn backend.server:app --host 0.0.0.0 --port 8000
```

Open:
- Web App: `http://localhost:3000`
- API Docs: `http://localhost:8000/docs`
