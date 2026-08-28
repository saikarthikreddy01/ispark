# VFSTR CSE Academic Source Registry for AcadGraph AI

> **Academic-integrity note:** This file is intentionally conservative. It distinguishes facts supported by the supplied CSE course-structure PDF from rules that require a separate official Academic Regulations / Registrar source. The advisor must not present an unverified project assumption as official university policy.

## Source A — Supplied CSE Course Structure & Course Contents

**Document:** `R22C24_B.Tech_(CSE)_Course_Structure_and_Contents.pdf`  
**Authority used by prototype:** VFSTR CSE curriculum/course-structure document supplied to the project  
**Status:** `CURRICULUM_SOURCE`

### [SRC-A-01] Credit transfer / flexible academic pathways
**Status:** `VERIFIED_FROM_SUPPLIED_DOCUMENT`

The salient curriculum features explicitly mention:
- lateral entry and lateral exit options;
- credit earning by credit transfer;
- Honours / Research Honours / Minor / add-on pathways and a dual B.Tech + M.Tech/MBA option;
- semester drop for innovation/incubation/entrepreneurial/advanced exploratory activities with subsequent re-entry.

### [SRC-A-02] Semester and course structure
**Status:** `VERIFIED_FROM_SUPPLIED_DOCUMENT`

The document provides semester-wise course titles/codes, L-T-P-C values, categories, Department Elective slots, Open Elective slots, Minors/Honours slots, and Internship/Project Work.

Important modelling rule: a generic **Department Elective** or **Open Elective** slot is a choice slot. A specific elective such as Deep Learning must not be treated as mandatory merely because it exists in the elective pool.

### [SRC-A-03] Artificial Intelligence prerequisite knowledge
**Status:** `VERIFIED_FROM_SUPPLIED_DOCUMENT`

`24CS302 Artificial Intelligence` lists **Probability and Statistics** under **PREREQUISITE KNOWLEDGE**.

This is modelled as `REQUIRES_KNOWLEDGE_OF`, not as a registration-blocking formal prerequisite unless a separate official registration rule is supplied.

### [SRC-A-04] Deep Learning prerequisite knowledge
**Status:** `VERIFIED_FROM_SUPPLIED_DOCUMENT`

`22CS804 Deep Learning` lists **Machine Learning, Python programming** under **PREREQUISITE KNOWLEDGE**.

This is a readiness/background relationship and is not automatically a formal registration block.

### [SRC-A-05] Machine Learning prerequisite knowledge
**Status:** `VERIFIED_FROM_SUPPLIED_DOCUMENT`

`24CS306 Machine Learning` course content identifies prerequisite knowledge in **Probability and Linear Algebra, Python programming**.

The prototype may map these concepts to relevant curriculum courses for readiness analysis, but the mapping must not be described as a formal minimum-grade registration rule without a separate authoritative regulation.

### [SRC-A-06] Department elective pool
**Status:** `VERIFIED_FROM_SUPPLIED_DOCUMENT`

The Department Elective pool includes courses such as Advanced Data Structures, Advanced Java Programming, Computer Graphics, Deep Learning, Digital Image Processing, Mobile Ad-hoc Networks, Text Mining, Numerical Algorithms, Operating System Design, and Simulation and Modeling.

## Rules requiring a separate Academic Regulations source

The following are **NOT VERIFIED by the supplied course-structure PDF** and must not be presented as official rules by AcadGraph AI until a Registrar/Academic Regulations source is added:

- minimum passing grade for prerequisite progression;
- a specific 18/21/24-credit registration cap;
- academic probation GPA/CGPA thresholds;
- a 75% attendance requirement or condonation threshold;
- prerequisite-waiver approval hierarchy;
- a formal seven-year maximum degree duration;
- an official 160-credit graduation minimum;
- automatic equivalency/substitution approval between C24, Honours, and Minor courses.

For hackathon demonstration, any such synthetic rule must be tagged `DEMO_POLICY` and displayed as **prototype logic, not official VFSTR policy**.

## Substitution governance

Course similarity may produce a **CANDIDATE** substitution. Candidate substitutions require faculty review. Only a mapping supported by an authoritative equivalency source may be tagged `APPROVED` and used automatically to satisfy a formal degree requirement.

## Human-in-the-loop principle

AcadGraph AI may:
- identify a conflict;
- collect evidence;
- generate a candidate resolution or petition draft;
- route an exceptional case for review.

AcadGraph AI must not autonomously approve a prerequisite waiver, credit exception, or course substitution that changes an academic rule.
