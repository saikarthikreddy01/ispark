# Agent Architecture — Problem Statement Alignment

## Core rule

**LLM proposes/explains. Federated sources and Graph-RAG retrieve. Deterministic rules verify. Humans approve exceptions.**

This project addresses the hackathon problem: **Decentralized Graph-RAG Academic Advising & Prerequisite Conflict Resolver**.

## End-to-end flow

```text
Student Query
   ↓
ProfileAgent
   ↓
SupervisorAgent
   ↓
FederatedSourceRouter
   ↓
GraphRAGAgent
   ↓
Conditional specialist route
   ├─ prerequisite/general → ConstraintConflictAgent
   ├─ pathway             → PathwayAgent → RiskBottleneckAgent → CareerAlignmentAgent
   ├─ risk                → RiskBottleneckAgent → CareerAlignmentAgent
   ├─ substitution        → SubstitutionAgent → FacultyEscalationAgent when needed
   ├─ career              → CareerAlignmentAgent
   └─ policy              → FormalVerificationAgent
   ↓
FormalVerificationAgent
   ↓
CitationAgent
   ↓
AdvisorSynthesisAgent
   ↓
Verified / qualified answer
```

## Agents and responsibilities

### 1. ProfileAgent
Normalizes student history: completed courses, planned courses, current semester, career goals and planning limits. This prevents every agent from interpreting the student record differently.

### 2. SupervisorAgent
Classifies intent and dynamically routes the request. It does not solve academic rules itself.

### 3. FederatedSourceRouter
Represents the **decentralized** part of the problem. It identifies academic authorities such as CSE, Mathematics and Central Academic Policy. The MVP stores these sources locally, but the routing contract allows them to become independent services or departmental graph stores later.

### 4. GraphRAGAgent
Combines graph relationships with retrieved document/course context. It distinguishes formal prerequisites from curriculum prerequisite knowledge.

### 5. ConstraintConflictAgent
Runs deterministic checks. A formal prerequisite can block; prerequisite knowledge only creates an academic-readiness warning unless a separate formal rule is sourced.

### 6. PathwayAgent
Creates candidate semester-wise pathways from required courses, semester structure and elective choice slots. It does not make a candidate plan official.

### 7. RiskBottleneckAgent
Identifies high-impact remaining courses and returns a transparent planning-risk indicator. It is not a statistical graduation prediction.

### 8. CareerAlignmentAgent
Maps curriculum courses to advisory career skills for AI/ML, Backend, Cybersecurity and Data roles. Career alignment never becomes a degree requirement.

### 9. SubstitutionAgent
Finds candidate alternatives/equivalencies. Unsourced equivalencies require faculty approval.

### 10. FacultyEscalationAgent
Creates a structured human-review packet for exceptional cases. The AI never auto-approves a waiver/substitution exception.

### 11. FormalVerificationAgent
Final deterministic safety gate. It produces decisions such as:
- `ADVISORY_OK`
- `CANDIDATE_PLAN`
- `BLOCKED_BY_FORMAL_CONSTRAINT`
- `FACULTY_REVIEW_REQUIRED`

### 12. CitationAgent
Deduplicates citations and reports evidence quality (`CURRICULUM_DERIVED`, `VERIFIED`, `UNVERIFIED`, etc.).

### 13. AdvisorSynthesisAgent
The only natural-language explanation layer. It must follow the verification decision and cannot override deterministic constraints.

## Problem-statement feature mapping

| Hackathon requirement | Implementation |
|---|---|
| Knowledge graph | `src/knowledge_graph/*` |
| Graph-RAG retrieval | `GraphRAGAgent` + `src/rag/*` |
| Decentralized academic knowledge | `FederatedSourceRouter` |
| Student-specific pathway | `ProfileAgent` + `PathwayAgent` |
| Prerequisite/credit conflict detection | `ConstraintConflictAgent` + constraint engine |
| Graduation risk/bottleneck identification | `RiskBottleneckAgent` |
| Alternative/substitution recommendation | `SubstitutionAgent` |
| Career-aware advising | `CareerAlignmentAgent` |
| Citation-traceable advice | `CitationAgent` + Graph-RAG metadata |
| Formal constraint verification | `FormalVerificationAgent` |
| Faculty approval for exceptions | `FacultyEscalationAgent` + governance API |
| Agentic orchestration | LangGraph conditional workflow |

## Trust model

Every important claim should be classified as one of:
- `VERIFIED` / `VERIFIED_FROM_COURSE_STRUCTURE`
- `CURRICULUM_DERIVED`
- `PROJECT_ADVISORY`
- `UNVERIFIED`
- `AUTHORITATIVE_RULE_REQUIRED`

The system must never silently promote weaker evidence to a stronger authority class.

## Demo query

> I failed Probability and want to become an AI engineer. Plan the rest of my degree. Can I take Machine Learning and Deep Learning?

Expected agent behavior:
1. ProfileAgent loads completed/failed history.
2. Supervisor routes to pathway.
3. SourceRouter selects CSE + Mathematics + relevant policy authority.
4. Graph-RAG retrieves ML/DL relationships and curriculum evidence.
5. PathwayAgent proposes semester slots.
6. RiskAgent identifies bottlenecks.
7. CareerAgent aligns AI/ML courses to the goal.
8. VerificationAgent distinguishes formal blocks from readiness warnings.
9. CitationAgent attaches source quality.
10. Synthesis explains the plan without inventing regulations.

This is the intended judge-facing story: **the system reasons, verifies and explains; it does not merely chat.**
