# AcadGraph AI

**Decentralized Graph-RAG Academic Advising & Prerequisite Conflict Resolver**

AcadGraph AI converts a university curriculum into an explainable academic reasoning system. It combines a curriculum knowledge graph, source-aware retrieval, specialized LangGraph agents, deterministic constraint verification, career-aware advising, bottleneck analysis, and faculty governance.

> **Graph retrieves. RAG grounds. Rules verify. Gemini explains. Faculty approves exceptions.**

## What the prototype demonstrates

The hackathon build is intentionally focused on the expected prototype:

- student-specific academic advising
- semester-wise degree pathway visualization
- formal prerequisite vs prerequisite-knowledge distinction
- prerequisite and readiness conflict detection
- bottleneck / planning-risk analysis
- advisory career alignment
- candidate course substitutions
- source provenance and citation quality
- deterministic final verification
- human-in-the-loop faculty approval for exceptions
- provenance-aware academic knowledge graph

## Unified application

The project now runs as one application instead of separate disconnected pages and backend paths.

```text
Browser SPA
   ↓
FastAPI backend.app:app
   ├─ Student / curriculum overview
   ├─ Provenance-aware knowledge graph
   ├─ LangGraph AcademicAdvisor
   ├─ Graph-RAG retrieval
   ├─ Deterministic verification
   ├─ Faculty petition workflow
   └─ Persistent data repository
         ├─ Local JSON by default
         └─ MongoDB when MONGODB_URI is configured
```

### Frontend workspace

The single-page UI contains five judge-friendly views:

1. **Overview** — student context, observed progress, system trust architecture, and demo scenarios.
2. **AI Advisor** — natural-language advising with verification decision, agent trace, and evidence panel.
3. **Degree Pathway** — semester-by-semester curriculum with completed/planned/remaining status and flexible elective slots.
4. **Knowledge Graph** — interactive visualization distinguishing formal prerequisite, readiness knowledge, and candidate equivalency edges.
5. **Faculty Review** — pending exception/substitution requests with explicit human approval/rejection.

## Agent architecture

```text
Student question
   ↓
ProfileAgent
   ↓
SupervisorAgent
   ↓
FederatedSourceRouter
   ↓
GraphRAGAgent
   ↓
┌──────────────────────────────────────────┐
│ ConstraintConflictAgent                 │
│ PathwayAgent                            │
│ RiskBottleneckAgent                     │
│ CareerAlignmentAgent                    │
│ SubstitutionAgent                       │
└──────────────────────────────────────────┘
   ↓
FacultyEscalationAgent (when needed)
   ↓
FormalVerificationAgent
   ↓
CitationAgent
   ↓
AdvisorSynthesisAgent / Gemini explanation
```

The LLM is not the academic authority. Formal blocking decisions come from verified deterministic rules. Syllabus **PREREQUISITE KNOWLEDGE** is represented as non-blocking readiness context and is never silently converted into a registration rule.

## Run locally

### 1. Clone

```bash
git clone https://github.com/saikarthikreddy01/ispark.git
cd ispark
```

### 2. Create a Python environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Gemini

Create `.env` in the project root:

```env
GEMINI_API_KEY=your_key_here
MODEL_NAME=gemini-3.6-flash
```

MongoDB is optional. Without `MONGODB_URI`, AcadGraph AI uses `data/persistent_db.json` automatically.

### 5. Start the complete app

```bash
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/api/health
```

## Judge demo

Use the built-in one-click scenarios or ask:

```text
I want to become an AI/ML engineer. Check my readiness for Machine Learning and Deep Learning and explain any academic risks.
```

Then demonstrate:

```text
Student context
 → Supervisor routing
 → Federated source selection
 → Graph-RAG evidence
 → Pathway / risk / career reasoning
 → Formal verification
 → Citations
 → Gemini explanation
```

Second demo:

```text
Can I substitute an equivalent course for one of my remaining courses? Show only supported candidates and escalate anything unverified to faculty.
```

When faculty approval is required, send the generated packet to **Faculty Review** and make the human decision there.

## Academic trust model

| Status | Meaning |
|---|---|
| `VERIFIED` / `CURRICULUM_DERIVED` | Supported by a supplied curriculum/source |
| `REQUIRES_KNOWLEDGE_OF` | Non-blocking academic readiness relationship |
| `FORMAL_PREREQUISITE` | Blocking only when an authoritative formal rule exists |
| `PROJECT_ADVISORY` | Career or planning recommendation, not a degree requirement |
| `UNVERIFIED` | Must not be presented as an official academic rule |
| `PENDING_HUMAN_REVIEW` | AI may recommend review but cannot approve the exception |

The project intentionally does **not** present the retained 160-credit planning target as a verified graduation rule because the supplied course-structure source does not establish that policy by itself.

## Technology

- **Frontend:** HTML5, CSS3, vanilla JavaScript, SVG knowledge graph
- **Backend:** FastAPI + Uvicorn
- **Agent orchestration:** LangGraph
- **LLM explanation:** Gemini (optional deterministic fallback remains)
- **Knowledge graph:** NetworkX
- **RAG:** curriculum/document retrieval + graph context
- **Persistence:** local JSON by default; optional MongoDB
- **Testing:** Pytest + GitHub Actions
- **Deployment:** Docker-ready

## Core project rule

**The system reasons, verifies, and explains; it does not merely chat.**
