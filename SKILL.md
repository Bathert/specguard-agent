# SpecGuard — Spec-Driven Development Agent

Agent that turns Gherkin feature specifications into an implementation plan, an opt-in deterministic scaffold, or a guarded LLM-generated Python module, then evaluates and reviews the result. Built for the Kaggle 5-Day AI Agents Intensive.

## Philosophy

The spec is the source of truth. Generated scaffolds are deliberately incomplete and must be completed and reviewed before production use. LLM calls are explicit and use runtime environment variables only; every generated method traces back to a Gherkin scenario; security and evaluation are continuous, not afterthoughts.

## Trigger

When the user provides a `.feature` file path, pastes Gherkin content, or says "build from spec", "validate spec", "review against spec".

## Pipeline

```
SPEC → [spec-analyzer] → PLAN → [code-generator] → CODE → [security-scanner] → REVIEW → [progress-tracker] → DASHBOARD
```

### Phase 1: SPEC → PLAN (skill: spec-analyzer)
- Parse Gherkin `.feature` file
- Validate completeness: every scenario has Given/When/Then
- Extract entities, actions, assertions
- Generate ordered implementation plan with dependencies

### Phase 2: PLAN → CODE (skill: code-generator)
- Generate an opt-in Python implementation scaffold from the plan
- Never overwrite an existing implementation without explicit approval
- For LLM generation, require a fenced Python response, AST parse, static scan, and atomic write
- Every function annotated with its source scenario

### Phase 3: CODE → SECURE (skill: security-scanner)
- **Package-name resolution**: third-party top-level imports can be checked against PyPI
- **Secret detection**: scan for hardcoded credentials, tokens, keys
- **Injection audit**: unsanitized input in SQL, shell, HTML
- **Input validation**: every external input must have explicit guards

### Phase 4: REVIEW → TRACK (skill: progress-tracker)
- Map each scenario to explicit pytest node IDs in `evals/scenario_map.json`
- Calculate spec coverage percentage
- Detect regressions (was passing, now failing)
- Store progress in long-term memory across sessions

## Memory & Context (Day 3)

- Store spec-to-code mappings in `memory/progress.json`
- Progressive disclosure: SKILL.md is lightweight; sub-skills load on demand
- Track implementation state across sessions

## Security Architecture (Day 4 — 7 Pillars)

1. **Package-name resolution**: verify resolvable third-party import names where possible
2. **Secret detection**: flag hard-coded credential patterns
3. **Injection audit**: flag SQL, shell, and dynamic-code patterns
4. **Input validation review**: flag public functions with no visible guard
5. **Output sanitization review**: flag interpolated HTML and templates
6. **Spec traceability**: flag public functions without scenario context
7. **Continuous evaluation**: run tests once and preserve exact result node IDs

These are lightweight static guardrails, not a sandbox, full SAST, or provenance system.

## LLM Runtime

- Use Gemini through Google AI Studio by default; OpenAI-compatible gateways are also supported.
- Read credentials only from `SPEC_GUARD_LLM_API_KEY`; never write, log, or echo it.
- Use `llm-generate --dry-run` to inspect the plan and request contract without a key or network request.

## Evaluation (Day 4)

After each cycle:
1. Run spec scenarios as automated tests
2. Report pass/fail per scenario from the explicit node-ID map
3. Calculate coverage: implemented / total
4. Flag regressions

## Output Format

```
📋 SPEC: <feature name>
📊 COVERAGE: X/Y scenarios (Z%)
✅ PASSING: <list>
❌ FAILING: <list>
🔒 SECURITY: N issues (C critical, H high, M medium, L low)
📝 NEXT: <recommended action>
```

## Tools & Interoperability (Day 2)

Designed to work with:
- **MCP servers**: file system access, code execution, web search
- **Agent frameworks**: Hermes Agent, Antigravity, ADK
- **A2A protocols**: can delegate subtasks to specialist agents
