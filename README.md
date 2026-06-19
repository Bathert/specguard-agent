# SpecGuard — Spec-Driven Development Guardrails

**Kaggle 5-Day AI Agents Intensive: Capstone Project**

SpecGuard turns a Gherkin feature into an implementation plan and either an
optional deterministic scaffold or an LLM-generated Python module. It then runs
explicit scenario-to-test evaluation, lightweight static security checks, and a
persistent progress dashboard.

It is deliberately conservative: LLM generation is explicit, opt-in, and uses
only a runtime environment variable. The response must contain fenced Python,
parse successfully, and pass the static security gate before it can be written.
Complete the generated methods, add tests, and let the checks gate the change.

## Quick start

```bash
python3 -m pip install ".[dev]"

# Analyze, scan, evaluate, and update progress.
python3 agent.py --no-packages

# Create a traceable scaffold without overwriting existing code.
python3 agent.py generate --output generated/task_manager_scaffold.py

# Preview the LLM request without a key or a network call.
python3 agent.py llm-generate --dry-run

# Generate through Gemini; the key remains only in this shell session.
export SPEC_GUARD_LLM_API_KEY="your-key-here"
python3 agent.py llm-generate --provider gemini --output generated/task_manager_llm.py

# Add --generate to include scaffold generation in the full pipeline.
python3 agent.py --generate --output generated/task_manager_scaffold.py --no-packages
```

Useful individual phases:

```bash
python3 agent.py analyze
python3 agent.py generate --output generated/feature_scaffold.py
python3 agent.py llm-generate --dry-run
python3 agent.py scan --no-packages
python3 agent.py test
python3 agent.py track
```

The CLI exits non-zero for a failed scan, failed/unavailable tests, or a
dashboard update that was deliberately skipped. This makes it usable in CI.

## What the pipeline does

```text
SPEC (.feature)
    │
    ▼
[spec-analyzer] ─── parses the supported Gherkin subset, validates scenarios,
    │                  extracts tasks, descriptions, outlines, and data tables
    ▼
[code-generator] ── opt-in deterministic Python scaffold; every method traces
    │                  to one or more source scenarios
    ▼
[llm-core] ──────── optional Gemini or OpenAI-compatible generation; fenced
    │                  Python → AST parse → static scan → atomic write
    ▼
[security-scanner] ─ lightweight static checks for package names, secrets,
    │                  injection, validation, output interpolation, traceability
    ▼
[evaluation-runner] ─ runs pytest once and preserves exact pytest node IDs
    ▼
[progress-tracker] ─ maps scenarios to explicit test node IDs; detects regressions
```

The included Task Manager feature has 9 scenarios. `evals/scenario_map.json`
is the source of truth connecting those scenarios to tests; parameterized test
instances must all pass before a scenario is marked tested. No test name
heuristics are used.

## LLM core

The LLM path is a real runtime integration, not a mock. It supports Gemini and
OpenAI-compatible chat-completion endpoints through the standard library, so no
SDK dependency or key file is needed. The exact provider, model, and endpoint
can be supplied with CLI flags or `SPEC_GUARD_LLM_*` environment variables.

```bash
# Gemini defaults; set a different model if your account requires it.
export SPEC_GUARD_LLM_API_KEY="..."
python3 agent.py llm-generate --provider gemini --model gemini-2.5-flash \
  --output generated/task_manager_llm.py

# Re-run a recorded response through the same gate without a provider request.
python3 agent.py llm-generate --spec examples/url-slug.feature \
  --llm-response-file examples/url_slug_response.md \
  --output generated/url_slug.py

# OpenAI-compatible endpoint, including a self-hosted or gateway URL.
export SPEC_GUARD_LLM_PROVIDER=openai
export SPEC_GUARD_LLM_MODEL="your-model"
export SPEC_GUARD_LLM_BASE_URL="https://your-endpoint.example/v1"
python3 agent.py llm-generate --output generated/task_manager_llm.py
```

Copy [.env.example](.env.example) into your shell or an untracked `.env` file;
the runtime reads that local `.env` automatically and Git ignores it. SpecGuard
never prints API keys, writes them into a prompt, or puts them into generated
code or error messages.

## Demo: Task Manager API

The repository includes a small, hand-completed Task Manager implementation to
demonstrate the loop. Its spec covers creation, assignment, completion,
filtering, duplicate prevention, priority validation, search, deletion, and a
completed-task business rule.

The suite covers the generator, scenario mapping, evaluation runner, security
rule, parser, and Task Manager behavior. Run it with:

```bash
python3 -m pytest
```

## Security scope and limits

The scanner implements seven guardrails:

1. Package-name resolution against PyPI for third-party top-level imports.
2. Hard-coded secret pattern detection.
3. SQL, shell, and dynamic-code injection patterns.
4. Heuristic input-validation review.
5. Interpolated HTML/template output checks.
6. Scenario traceability comments on public functions.
7. Continuous test evaluation through the pipeline.

LLM output receives the same static scan before it is written. Critical or high
findings reject the artifact; medium and low findings are reported as warnings.

These are lightweight static checks, not a substitute for a dependency lock,
SBOM/provenance verification, a full SAST tool, code review, or an execution
sandbox. Network failures during optional PyPI resolution are reported as
unknown rather than treated as a clean provenance result. Use `--no-packages`
for deterministic offline/CI runs.

## Reproducibility and CI

`pyproject.toml` declares the test dependency and `.github/workflows/ci.yml`
runs the suite on Python 3.11–3.13, followed by the offline full pipeline.
The pipeline will not overwrite `memory/progress.json` when pytest is absent
or cannot produce usable results; an unavailable test runner is not a
regression.

## Demo video

The repository includes a reproducible English walkthrough generator at
`scripts/generate_llm_demo_video.py`. It uses Edge Neural TTS and renders real
captured console output from the LLM dry run, full pipeline, test suite, and a
URL-slug case study. The case replays a recorded model response through the
same parse/scan/write gate, so the video needs no API key and works in regions
where a live provider is unavailable.

```bash
python3 -m pip install ".[video]"
python3 scripts/generate_llm_demo_video.py
```

It writes `specguard-llm-demo.mp4` and uses Edge Neural TTS plus `ffmpeg` for
voice and assembly, with macOS `say` only as an offline fallback.

## Project structure

```text
specguard-agent/
├── agent.py                         # CLI pipeline and exit-code policy
├── pyproject.toml                   # Reproducible test dependency
├── specs/task-manager.feature       # Demo Gherkin feature
├── src/
│   ├── spec_analyzer.py              # Supported Gherkin parser and planner
│   ├── code_generator.py             # Safe, opt-in scaffold generator
│   ├── llm_core.py                   # Gemini/OpenAI-compatible guarded generation
│   ├── security_scanner.py           # Lightweight static checks
│   ├── evaluation_runner.py          # Exact pytest node-id results
│   ├── progress_tracker.py           # Explicit scenario coverage and regressions
│   └── task_manager.py               # Demo implementation
├── evals/
│   ├── scenario_map.json             # Scenario → test/file mapping
│   └── test_*.py                     # Behaviour and pipeline checks
└── memory/progress.json              # Persisted dashboard state
```

## Course mapping

| Course topic | SpecGuard implementation |
| --- | --- |
| Agents & vibe coding | Gherkin-derived tasks and an opt-in scaffold generator. |
| Tools & interoperability | Small, independently callable pipeline modules. |
| Skills & memory | Skill documentation plus persistent, non-destructive progress state. |
| Security & evaluation | Static guardrails, explicit scenario mappings, and CI-friendly exit codes. |
| Spec-driven production | Specs, mappings, tests, and code are auditable together. |

Built for the Kaggle 5-Day AI Agents: Intensive Vibe Coding Course With Google,
June 2026.
