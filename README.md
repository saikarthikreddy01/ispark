# 🎓 AcadGraph AI — Agentic Academic Advising + Graph-RAG

Academic pathway planning, curriculum graph reasoning, prerequisite/readiness analysis, bottleneck detection, candidate semester planning, citation-aware advising, and faculty review for exceptional cases.

The prototype is built around the supplied VFSTR CSE C24/R22-aligned course-structure and course-content document.

## Core design principle

> **LLM proposes/explains → graph retrieves relationships → deterministic rules verify constraints → faculty approves exceptions.**

An LLM is never treated as the authority for whether a student may register, substitute a course, or graduate.

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
  database.py
  server.py

data/
  courses.json
  degree_requirements.json
  equivalencies.json
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
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload
```

Then open:

- Web app: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

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
- Some legacy FastAPI/UI paths still require security hardening before production use.
- This is a hackathon academic-planning prototype, not an official registration or degree-audit system.
