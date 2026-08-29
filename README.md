# 🎓 AcadGraph AI — Agentic Academic Advising + Graph-RAG

Academic pathway planning, curriculum graph reasoning, prerequisite/readiness analysis, bottleneck detection, candidate semester planning, citation-aware advising, and faculty review for exceptional cases.

The prototype is built around the supplied VFSTR CSE C24/R22-aligned course-structure and course-content document.

## Core design principle

> **LLM proposes/explains → graph retrieves relationships → deterministic rules verify constraints → faculty approves exceptions.**

An LLM is never treated as the authority for whether a student may register, substitute a course, or graduate.

## Student academic profile

The demo profile for student `241FA04077` contains the verified academic record supplied for four completed semesters:

- 35 subject records: subject code, name, credits, letter grade, grade points, and result month/year;
- 27 graded subjects and 8 mandatory non-graded subjects;
- 85 graded credits and a credit-weighted CGPA of `7.83 / 10`;
- semester-wise SGPA calculated from graded subjects only;
- support for `S` grades and `-` for subjects without grade points.

The same profile structure remains editable for other students. Saving a profile recalculates CGPA, normalizes course codes and grades, and updates the completed-course set used by pathway and prerequisite checks.

## Academic-integrity model

The project deliberately distinguishes two relationship types:

- `FORMAL_PREREQUISITE` — registration-blocking; may only be created from an authoritative regulation/registration source.
- `REQUIRES_KNOWLEDGE_OF` — academic-readiness/background relationship derived from syllabus fields such as **PREREQUISITE KNOWLEDGE**; non-blocking by itself.

Example source-backed relationships:

- `24CS302 Artificial Intelligence` → prerequisite knowledge: Probability & Statistics.
- `22CS804 Deep Learning` → prerequisite knowledge: Machine Learning and Python programming.
- `24CS306 Machine Learning` → prerequisite knowledge: Probability/Linear Algebra and Python programming.

The supplied curriculum does **not by itself prove** a minimum grade or formal registration block for those readiness statements, so AcadGraph does not silently convert them into hard prerequisites.

## Source-status labels

Every important rule should be interpreted through one of these statuses:

- `VERIFIED` / `VERIFIED_FROM_SUPPLIED_DOCUMENT`
- `CURRICULUM_DERIVED`
- `CANDIDATE`
- `DEMO_POLICY`
- `UNVERIFIED`

Candidate course substitutions require faculty review unless an authoritative equivalency source explicitly marks them `APPROVED`.

## Implemented architecture

```text
Student UI
   │
   ▼
FastAPI
   │
   ▼
LangGraph Academic Advisor
   ├── query classifier
   ├── Graph-RAG retriever
   ├── conflict/readiness agent
   ├── pathway agent
   ├── planning-risk agent
   ├── substitution agent
   └── answer synthesis
            │
            ├── NetworkX academic graph
            ├── lexical/TF-IDF document retrieval
            ├── deterministic constraint engine
            └── curriculum / source registry
```

### Important retrieval note

The current `AcademicVectorStore` is a lightweight **lexical TF-IDF/cosine retriever**, not a neural embedding store. The system therefore describes itself as hybrid **graph + document retrieval**. FAISS/embedding dependencies are available for a later semantic-retrieval upgrade, but the README does not claim neural embeddings are already the active production retriever.

## Repository layout

```text
backend/
  app.py
  database.py
  security.py
  server.py

data/
  courses.json
  degree_requirements.json
  equivalencies.json
  faculty_accounts.json
  policies.md
  sample_students.json

src/
  agents/
    orchestrator.py
    conflict_agent.py
    pathway_agent.py
    risk_agent.py
    substitution_agent.py
    state.py
  constraint_engine/
    prerequisite_checker.py
    credit_validator.py
    schedule_feasibility.py
  knowledge_graph/
    graph_builder.py
    graph_queries.py
    graph_visualizer.py
  models/
  rag/

web/
  advisor.html
  conflicts.html
  curriculum.html
  governance.html
  graph.html
  pathway.html
  risk.html
  substitutions.html
```

## Knowledge graph

The NetworkX graph represents courses, departments, credit categories and academic relationships. It supports:

- formal prerequisite traversal;
- non-blocking prerequisite-knowledge traversal;
- recursive dependency inspection;
- cycle detection;
- topological ordering of formal dependencies;
- bottleneck scoring using downstream impact;
- candidate equivalency relationships with approval status.

A specific elective is **not** automatically a mandatory course. The degree-requirement schema represents Department Elective/Open Elective requirements as choice slots and treats Honours/Minors as an optional track in the base-degree planner.

## Constraint behavior

The deterministic constraint engine checks:

- already-completed courses;
- sourced formal prerequisites;
- corequisites;
- semester availability metadata;
- prerequisite-knowledge/readiness gaps as warnings;
- source-aware credit requirements;
- **Subject GPA must use a 0.00–10.00 scale and a valid Grade (O, A+, A, B+, B, C, P, F) is required.**

If an official credit minimum or semester cap is not verified by the currently loaded source set, the engine does not fabricate a blocking rule.

## Planning risk

`RiskAgent` returns a **Planning Risk Indicator**, not a statistical prediction that a student will or will not graduate. It uses transparent signals such as remaining source-defined required courses and high-impact dependency bottlenecks. Unverified credit rules do not create hard penalties.

## Degree requirements

`data/degree_requirements.json` separates:

- explicitly named required courses;
- elective choice pools;
- Open Elective slots;
- optional Honours/Minors slots;
- source status for numeric graduation/credit rules.

The historical `160 credits` project target is retained only as an **UNVERIFIED planning assumption** until a separate official Academic Regulations source is added. It must not be presented as a verified university graduation minimum based only on the supplied course-structure PDF.

## Substitutions and faculty governance

Entries in `data/equivalencies.json` are now `CANDIDATE` or `READINESS_BRIDGE` unless an authoritative equivalency source exists. They may be recommended for review but cannot automatically satisfy a formal requirement.

Exceptional cases should follow:

```text
Student request
   ↓
Automated evidence + constraint pre-check
   ↓
Candidate resolution
   ↓
Faculty / HoD review
   ↓
Approve or reject
```

## Run locally

```bash
git clone https://github.com/saikarthikreddy01/ispark.git
cd ispark
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source venv/bin/activate
```

Install and run:

```bash
pip install -r requirements.txt
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

Then open:

- Web app: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

The opening page presents the **AcadGraph AI** project name and three clickable
choices:

- **Features** opens the complete prototype capability list.
- **How it works** opens the six-stage agent and verification workflow.
- **Login** opens the separate `login.html` authentication page.

After authentication:

- Student accounts open `home.html`, the personalized advising dashboard.
- Faculty accounts open `governance.html`, the exception-review workspace.

### Authentication and demo accounts

Authentication uses one signed, HTTP-only `acadgraph_session` cookie. The
browser does not store a student ID, role, password, or login flag in
`localStorage`/`sessionStorage`. Login, session verification, protected faculty
actions, and logout are handled by FastAPI. Logout also sends `Clear-Site-Data`
and protected pages re-check the server session after a browser back-button
restore.

Seeded hackathon demo accounts:

- Student: `241FA04077` / `password123`
- Faculty reviewer: `faculty` / `faculty123`

Only salted PBKDF2 password hashes are committed. These accounts are for the
prototype demonstration and must be replaced for a real institutional rollout.

For Render, add a long random `SESSION_SECRET` environment variable so signed
sessions remain valid across service restarts. An optional single faculty
account override can be supplied with `FACULTY_USERNAME`,
`FACULTY_PASSWORD_HASH`, `FACULTY_TITLE`, `FACULTY_DEPARTMENT`, and
`FACULTY_INSTITUTION`. Generate a password hash locally without printing the
password itself:

```bash
python -c "from backend.security import hash_password; import getpass; print(hash_password(getpass.getpass()))"
```

The **Degree Pathway** screen now supports configurable 14/16/18-credit loads,
target-graduation input, credit-progress metrics, prerequisite-safe term cards,
constraint status, and unscheduled-course warnings. The **AI Advisor** displays
the active student context, request type, formal verification decision, detected
academic signals, citation evidence, faculty-review requirements, and the full
multi-agent execution trace.

Run the agent regression suite:

```bash
python -m unittest discover -s tests -v
```

The suite contains 22 checks covering authentication/session/logout behavior,
the agent workflow, student transcript,
10-point GPA/grades, pathways, bottlenecks, substitutions, faculty escalation,
citations, landing/login routing, and the enhanced advising UI.

If no OpenAI or Gemini API key is configured, the deterministic Graph-RAG,
constraint, pathway, risk, substitution, citation, and faculty-escalation
agents still run. The API reports `workflow_mode` so the UI does not claim
LangGraph execution when the deterministic fallback is active.

## Docker

```bash
docker build -t acadgraph-ai .
docker run -p 8080:8080 --env-file .env acadgraph-ai
```

## Recommended hackathon demo

Use a synthetic student record and ask:

> “I want an AI-focused pathway. What happens if I have not completed Probability & Statistics, and can I choose Deep Learning?”

A good response should demonstrate:

1. curriculum entity resolution;
2. graph retrieval;
3. `REQUIRES_KNOWLEDGE_OF` warnings rather than fabricated hard blocks;
4. candidate semester pathway;
5. bottleneck/planning-risk analysis;
6. source-status-aware citations;
7. faculty escalation when an actual exception/substitution is requested.

## Known prototype limitations

- The active document retriever is lexical rather than neural-embedding based.
- The supplied course-structure PDF is not a complete replacement for official Registrar/Academic Regulations documents.
- Seeded student/faculty accounts are demo fixtures and are not an institutional identity provider.
- This is a hackathon academic-planning prototype, not an official registration or degree-audit system.
