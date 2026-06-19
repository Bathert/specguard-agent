# SpecGuard — Video Script (5–7 minutes)

## Scene 1: Problem (0:00–0:45)
**Visual**: Screen showing a messy codebase with crossed-out comments, hallucinated imports highlighted in red.

**Narration**:
"Vibe coding lets you generate prototypes in seconds. But those prototypes rot fast. Hallucinated packages that don't exist. Missing input validation. Code that nobody can trace back to what it was supposed to do. The spec gets written once and never looked at again."

**Visual**: Switch to a clean Gherkin .feature file.

"The solution is Spec-Driven Development. The Gherkin spec is permanent. The code is disposable. And an agent enforces this cycle end-to-end."

## Scene 2: Architecture Overview (0:45–2:00)
**Visual**: Diagram of the pipeline — boxes connected by arrows.

```
SPEC (.feature)
    ↓
[spec-analyzer] → validates, extracts plan
    ↓
[code-generator] → generates implementation
    ↓
[security-scanner] → 7-pillar security audit
    ↓
[progress-tracker] → coverage dashboard
```

**Narration**:
"SpecGuard is a modular agent built as a set of portable skills. Each skill is a directory with its own SKILL.md — following the Agent Skills pattern from Day 3 of the course."

"Walk through each box:
- spec-analyzer parses Gherkin, validates completeness, builds an ordered implementation plan
- code-generator produces code where every function traces back to a specific scenario
- security-scanner runs 7 automated checks: package verification against real registries, secret detection, injection audit, input validation gaps
- progress-tracker maintains coverage metrics across sessions in long-term memory"

## Scene 3: Demo — Task Manager API (2:00–4:30)
**Visual**: Open `specs/task-manager.feature` in editor.

**Narration**:
"Let me show you a real example. Here's a Gherkin spec for a Task Manager API — 9 scenarios covering create, assign, complete, list, search, delete, plus edge cases like duplicate prevention and business rule enforcement."

**Visual**: Switch to `src/task_manager.py`, scroll through.

"This is the generated implementation. Notice every method has a comment tracing it to its source scenario. `create_task` traces to 'Create a new task' and 'Prevent duplicate task titles'. `assign_task` traces to 'Assign a task to a user' and 'Cannot assign a completed task'."

**Visual**: Highlight input validation: `if not title or not title.strip()`, `if priority not in VALID_PRIORITIES`.

"Every external input is validated. No raw user strings flow into the system unchecked."

**Visual**: Switch to terminal, run `python3 -m pytest evals/test_task_manager.py -v`.

"Now the evaluation. 16 automated tests — one per scenario plus edge cases."

**Visual**: Terminal output scrolling — all green PASSED.

```
evals/test_task_manager.py::test_create_new_task PASSED
evals/test_task_manager.py::test_assign_task PASSED
...
============================== 16 passed in 0.02s ==============================
```

"16 out of 16 pass. 100% spec coverage. Zero regressions."

## Scene 4: Security Scanner Deep Dive (4:30–5:45)
**Visual**: Open `skills/security-scanner/SKILL.md`, highlight the 7-pillar list.

**Narration**:
"Security isn't an afterthought — it's a mandatory phase in the pipeline. The security-scanner skill implements the 7-pillar architecture from Day 4 of the course."

"Pillar 1 — Package verification: every import is checked against real registries. If the LLM hallucinated a package name, it gets flagged."

"Pillar 2 — Secret detection: scans for hardcoded API keys, tokens, passwords. Zero tolerance."

"Pillar 3 — Injection audit: finds unsanitized input in SQL, shell commands, HTML output."

"Pillars 4 through 7 — input validation, output sanitization, spec traceability, and continuous evaluation."

**Visual**: Show the security report format from the skill.

"The scanner produces a structured JSON report with severity levels and fix suggestions. Nothing ships without a clean scan."

## Scene 5: Memory & Progress Tracking (5:45–6:30)
**Visual**: Open `memory/progress.json`.

**Narration**:
"Between sessions, SpecGuard remembers. This progress.json tracks every scenario's status — not_started, in_progress, implemented, tested, or regression."

"If a scenario that passed yesterday fails today, it's flagged as a regression and surfaced immediately."

**Visual**: Show the dashboard output format.

"The progress-tracker skill generates a dashboard: coverage percentage, test pass rate, regressions, velocity, and a recommended next action."

## Scene 6: Course Mapping & Rationale (6:30–7:15)
**Visual**: Table mapping 5 days to SpecGuard features.

**Narration**:
"SpecGuard maps directly to all 5 days of the course. Day 1 — vibe coding: natural language specs drive code generation. Day 2 — tools and interoperability: modular skills that work with any agent framework. Day 3 — skills and memory: progressive disclosure SKILL.md directories plus persistent state. Day 4 — security and evaluation: 7-pillar architecture with 16 automated tests. Day 5 — spec-driven production: the entire agent is built around SDD, where the spec is truth and code is disposable."

**Visual**: Back to GitHub repo README.

"The full writeup, rationale, and code are at github.com/Bathert/specguard-agent. Thank you for watching."

---

## Recording Instructions

1. **Screen recording**: Use QuickTime Player → File → New Screen Recording, or OBS
2. **Audio**: Use built-in mic or external. Speak clearly, moderate pace.
3. **Resolution**: 1920×1080 recommended
4. **Upload**: YouTube (unlisted or public) — paste link in Kaggle submission
5. **Length target**: 5–7 minutes. Don't rush the demo section.
