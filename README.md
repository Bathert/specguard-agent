# SpecGuard — Spec-Driven Development Agent

**Kaggle 5-Day AI Agents Intensive: Capstone Project**

SpecGuard is an AI agent that transforms Gherkin feature specifications into production-ready code through a disciplined pipeline: analyze → generate → review → secure → track. It treats code as disposable and the spec as the single source of truth.

## Rationale

I built SpecGuard because the hardest problem in vibe coding isn't generating code — it's keeping that code correct, secure, and maintainable over time. LLMs can produce impressive prototypes in seconds, but those prototypes rot fast: hallucinated dependencies, missing validation, untraceable logic, and zero guardrails.

Spec-Driven Development (SDD) solves this by inverting the relationship: the Gherkin spec is permanent; the code is regenerated on every change. SpecGuard automates this cycle end-to-end, adding continuous security scanning and progress tracking so you always know exactly which scenarios are implemented, tested, and passing.

## How It Maps to the 5-Day Course

| Day | Topic | SpecGuard Implementation |
|-----|-------|--------------------------|
| **Day 1** | Agents & Vibe Coding | Natural language Gherkin specs → generated code. The agent understands intent from spec, not syntax. |
| **Day 2** | Tools & Interoperability | Modular skill architecture: spec-analyzer, code-generator, security-scanner, progress-tracker. Each skill is a portable SKILL.md directory — interoperable with any agent framework (Hermes, Antigravity, ADK). |
| **Day 3** | Agent Skills & Memory | Progressive disclosure: main SKILL.md is lightweight; sub-skills load on demand. Long-term memory in `memory/progress.json` tracks implementation state across sessions. |
| **Day 4** | Security & Evaluation | 7-pillar security architecture: package verification (anti-slopsquatting), secret detection, injection audit, input validation, output sanitization, spec traceability, continuous evaluation. 16 automated tests run after every change. |
| **Day 5** | Spec-Driven Production | The entire agent is built around SDD: Gherkin specs are the source of truth, code is disposable, every function traces to a scenario, and the pipeline is ready for CI/CD integration. |

## Architecture

```
SPEC (.feature)
    │
    ▼
[spec-analyzer] ─── validates completeness, extracts entities/actions/assertions
    │
    ▼
[code-generator] ─── generates implementation with spec-traceability comments
    │
    ▼
[security-scanner] ─── anti-slopsquatting, secret detection, injection audit, validation gaps
    │
    ▼
[progress-tracker] ─── coverage metrics, regression detection, next-action recommendation
    │
    ▼
DASHBOARD: coverage %, pass/fail, security issues, next step
```

## Demo: Task Manager API

The agent was tested against a 9-scenario Gherkin spec for a Task Manager API:

- Create, assign, complete, list, search, delete tasks
- Duplicate prevention, priority validation, business rule enforcement

### Test Results

```
============================== 16 passed in 0.02s ==============================

✅ Create a new task
✅ Assign a task to a user
✅ Complete a task
✅ List tasks by status
✅ Prevent duplicate task titles
✅ Validate task priority (urgent, critical, unknown)
✅ Search tasks by keyword
✅ Delete a task
✅ Cannot assign a completed task
✅ Edge cases: empty title, whitespace title, empty assignee, nonexistent task, invalid status filter
```

📊 **Spec Coverage**: 9/9 scenarios (100%)
🧪 **Test Pass Rate**: 16/16 (100%)
🔒 **Security**: 0 issues (all inputs validated, no hardcoded secrets, no injection vectors)

## Project Structure

```
specguard-agent/
├── SKILL.md                    # Main agent definition
├── skills/
│   ├── spec-analyzer/SKILL.md  # Parse & validate Gherkin specs
│   ├── code-generator/SKILL.md # Generate implementation from plan
│   ├── security-scanner/SKILL.md # 7-pillar security audit
│   └── progress-tracker/SKILL.md  # Coverage metrics & regression detection
├── specs/
│   └── task-manager.feature    # Example Gherkin specification
├── src/
│   └── task_manager.py         # Generated implementation
├── evals/
│   └── test_task_manager.py    # 16 automated evaluation tests
└── memory/
    └── progress.json           # Long-term progress state
```

## Code

Full source code: https://github.com/Bathert/specguard-agent

## Video

A walkthrough video explaining the agent's architecture, demonstrating the full pipeline from spec to tested code, and showing the security scanner in action will be linked here.

---

Built for the Kaggle 5-Day AI Agents: Intensive Vibe Coding Course With Google, June 2026.
