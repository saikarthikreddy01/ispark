---
name: focused-code-change
description: 'Use when implementing or debugging a code change in a repository. Guides local code routing, falsifiable hypothesis formation, minimal edits, focused validation, and iterative repair while preserving unrelated user changes.'
argument-hint: 'Describe the requested behavior, failing test, or code anchor.'
user-invocable: true
disable-model-invocation: false
---

# Focused Code Change

## Purpose

Complete a repository code change from a concrete anchor through executable verification. Keep exploration local, make the smallest testable edit, and preserve unrelated worktree changes.

## When to Use

Use this skill for:

- Fixing a reported bug or failing test
- Implementing a behavior change in an existing codebase
- Refactoring a named symbol or nearby implementation
- Debugging a local runtime, type, lint, or test failure
- Reviewing a change when an executable check can validate a finding

Do not use it for broad architecture discovery, greenfield project setup, or purely explanatory questions unless the user asks for implementation.

## Procedure

### 1. Establish the anchor

Start from the most concrete available entry point, in this order:

1. Named file, symbol, failing behavior, command, or test
2. Nearby call site or implementation that directly controls the behavior
3. A targeted repository search when no anchor is provided

Read only enough nearby code to understand the controlling path. If the starting file only forwards, wires, registers, or displays the behavior, follow one hop to the code that computes or mutates it.

### 2. State a local hypothesis

Before editing, write down internally:

- One falsifiable hypothesis explaining the behavior or failure
- The local code path supporting that hypothesis
- One cheap check that could disconfirm it
- One small edit that would test the hypothesis

If an abstraction boundary remains unresolved, take one nearby read of its test, call site, or implementation. Then choose the best current hypothesis instead of continuing broad exploration.

### 3. Check repository conditions

Inspect relevant local conventions and the worktree before editing. Preserve changes you did not make. Do not reset, check out, or otherwise discard unrelated modifications.

Use existing project helpers, APIs, test conventions, and formatting rules. Prefer structured parsers and established libraries over ad hoc string handling when the codebase already provides them.

### 4. Make the smallest edit

Edit only the files and behavior required by the hypothesis. Preserve public APIs and surrounding style unless the request requires a contract change. Avoid unrelated cleanup, metadata churn, and speculative refactors.

For a new or uncertain path, a small reversible probe is acceptable when it exposes types, control-flow gaps, or validation failures.

### 5. Validate immediately

After the first substantive edit, run the narrowest available executable check before more reading or patching:

1. The reported failing check or behavior-scoped test
2. A focused test for the touched slice
3. A narrow compile, typecheck, or lint command
4. Diff inspection only when no executable check is available

Do not widen scope between the edit and this first validation.

### 6. Repair or redirect

- If validation supports the hypothesis but exposes a local defect, repair that same slice and rerun the same check.
- If validation disproves the hypothesis, take one nearby hop to the code that more directly controls the behavior, revise the hypothesis, and make the smallest next edit.
- If validation is ambiguous, perform one nearby disambiguating read or inspect one neighboring test/call site, then decide between local repair and a one-hop redirect.
- If the check succeeds but adjacent edits remain necessary, make one small adjacent edit and rerun focused validation.

Do not attempt more than three repair cycles in one file without reassessing the approach and reporting the blocker.

### 7. Finish with executable evidence

Run at least one post-edit executable validation whenever the environment provides one. Report the exact check and its result, along with any unrelated pre-existing failures or unavailable checks.

Summarize the behavior changed, the key files touched, and residual risk. Do not claim a test passed if it was not run.

## Decision Rules

| Situation | Action |
|---|---|
| A concrete test or failure is named | Start there and rerun it after the first edit |
| The named file only forwards behavior | Follow one hop to the deciding implementation |
| Multiple paths seem plausible | Choose the path with the strongest falsifiable check and smallest edit |
| No focused test exists | Use a narrow compile, lint, typecheck, or direct behavior command |
| Commands are unavailable | Use the narrowest available validation and state the limitation |
| Worktree is dirty | Keep unrelated changes; inspect and work around them |
| Validation falsifies the hypothesis | Redirect one hop, then reassess locally |
| Three repair attempts fail | Stop, report the concrete blocker, and ask for direction |

## Completion Checklist

- [ ] The controlling implementation path was identified from a concrete anchor.
- [ ] A falsifiable hypothesis and discriminating check were established before editing.
- [ ] The change is minimal and consistent with local patterns.
- [ ] The first post-edit action was focused executable validation when available.
- [ ] Any failure was repaired or used to redirect the hypothesis.
- [ ] At least one final executable check was run, or its absence was documented.
- [ ] Unrelated worktree changes were preserved.
- [ ] The final report distinguishes verified results from residual risk.
