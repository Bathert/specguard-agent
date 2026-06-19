# SpecGuard — Spec-Driven Development Agent

**Kaggle 5-Day AI Agents Intensive: Capstone Project**

SpecGuard is an AI agent that transforms Gherkin feature specifications into production-ready code through a disciplined pipeline: analyze → generate → review → secure → track. It treats code as disposable and the spec as the single source of truth.

## Run It

```bash
# Full pipeline
python3 agent.py

# Individual phases
python3 agent.py analyze     # Parse & validate spec
python3 agent.py scan        # Security scan
python3 agent.py test        # Run evaluation tests
python3 agent.py track       # Update progress dashboard

# Custom spec
python3 agent.py --spec specs/my-feature.feature
```

## Rationale

I built SpecGuard because the hardest problem in vibe coding isn't generating code — it's keeping that code correct, secure, and maintainable over time. LLMs can produce impressive prototypes in seconds, but those prototypes rot fast: hallucinated dependencies, missing validation, untraceable logic, and zero guardrails.

Spec-Driven Development (SDD) solves this by inverting the relationship: the Gherkin spec is permanent; the code is regenerated on every change. SpecGuard automates this cycle end-to-end, adding continuous security scanning and progress tracking so you always know exactly which scenarios are implemented, tested, and passing.

## How It Maps to the 5-Day Course

| Day | Topic | SpecGuard Implementation |
|-----|-------|--------------------------|
| **Day 1** | Agents & Vibe Coding | Natural language Gherkin specs drive code generation. The agent understands intent from spec, not syntax. |
| **Day 2** | Tools & Interoperability | Modular skill architecture: spec-analyzer, code-generator, security-scanner, progress-tracker. Each skill is a portable SKILL.md directory. |
| **Day 3** | Agent Skills & Memory | Progressive disclosure: main SKILL.md is lightweight; sub-skills load on demand. Long-term memory in `memory/progress.json` tracks implementation state across sessions. |
| **Day 4** | Security & Evaluation | 7-pillar security architecture: package verification (anti-slopsquatting), secret detection, injection audit, input validation, output sanitization, spec traceability, continuous evaluation. 16 automated tests run after every change. |
| **Day 5** | Spec-Driven Production | The entire agent is built around SDD: Gherkin specs are the source of truth, code is disposable, every function traces to a scenario, and the pipeline is ready for CI/CD integration. |

## Architecture

```
SPEC (.feature)
    │
    ▼
[spec-analyzer] ─── parses Gherkin, validates completeness, extracts tasks
    │                  src/spec_analyzer.py
    ▼
[code-generator] ─── generates implementation with spec-traceability
    │                  src/task_manager.py (demo implementation)
    ▼
[security-scanner] ── 7-pillar audit: packages, secrets, injections, validation
    │                  src/security_scanner.py
    ▼
[progress-tracker] ── coverage metrics, regression detection, dashboard
    │                  src/progress_tracker.py
    ▼
DASHBOARD: 9/9 scenarios (100%), 16/16 tests pass, 0 regressions
```

## Demo: Task Manager API

The agent was tested against a 9-scenario Gherkin spec for a Task Manager API:

- Create, assign, complete, list, search, delete tasks
- Duplicate prevention, priority validation, business rule enforcement

### Test Results (verified)

```
📋 PHASE 1: SPEC ANALYSIS — 9 scenarios, 0 warnings, 9 tasks
🔒 PHASE 3: SECURITY SCAN — pass_with_warnings (0 critical, 0 high, 0 injections, 0 secrets)
🧪 PHASE 4: EVALUATION — 16 passed, 0 failed
📊 PHASE 5: PROGRESS — 9/9 scenarios tested (100%), 0 regressions, Ready for deployment
```

## Project Structure

```
specguard-agent/
├── agent.py                     # CLI entry point — runs full pipeline
├── SKILL.md                     # Main agent skill definition
├── skills/
│   ├── spec-analyzer/SKILL.md   # Parse & validate Gherkin specs
│   ├── code-generator/SKILL.md  # Generate implementation from plan
│   ├── security-scanner/SKILL.md # 7-pillar security audit
│   └── progress-tracker/SKILL.md  # Coverage metrics & regression detection
├── src/
│   ├── spec_analyzer.py         # Real Gherkin parser (230 lines)
│   ├── task_manager.py          # Demo implementation (100 lines)
│   ├── security_scanner.py      # Real security scanner (330 lines)
│   └── progress_tracker.py      # Real progress tracker (240 lines)
├── specs/
│   └── task-manager.feature     # 9-scenario Gherkin specification
├── evals/
│   └── test_task_manager.py      # 16 automated evaluation tests
└── memory/
    └── progress.json            # Long-term progress state
```

## Security Scanner Details

The security scanner implements 7 pillars:

1. **Package verification** — checks every import against PyPI (anti-slopsquatting)
2. **Secret detection** — scans for API keys, tokens, passwords, private keys
3. **Injection audit** — finds unsanitized input in SQL, shell, eval, HTML
4. **Input validation** — flags functions with external input but no validation
5. **Output sanitization** — checks for unescaped output
6. **Spec traceability** — flags functions without spec trace comments
7. **Continuous evaluation** — runs tests after every change

The scanner produces a structured JSON report with severity levels and fix suggestions. It includes smart false-positive suppression: subprocess calls with hardcoded arguments (e.g., `subprocess.run([sys.executable, "-m", "pytest", ...])`) are not flagged as injection vectors.

## Code

Full source code: https://github.com/Bathert/specguard-agent

---

Built for the Kaggle 5-Day AI Agents: Intensive Vibe Coding Course With Google, June 2026.