# SpecGuard — Spec-Driven Development Agent

Agent that transforms Gherkin feature specifications into production-ready code through a disciplined pipeline: analyze → generate → review → secure → track. Built for the Kaggle 5-Day AI Agents Intensive.

## Philosophy

Code is disposable. The spec is the source of truth. Every line of generated code must trace back to a Gherkin scenario. Security and evaluation are continuous, not afterthoughts.

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
- For each task in the plan, generate implementation
- Natural language describes intent; tools produce syntax
- Every function annotated with its source scenario

### Phase 3: CODE → SECURE (skill: security-scanner)
- **Package verification**: every import checked against real registries (anti-slopsquatting)
- **Secret detection**: scan for hardcoded credentials, tokens, keys
- **Injection audit**: unsanitized input in SQL, shell, HTML
- **Input validation**: every external input must have explicit guards

### Phase 4: REVIEW → TRACK (skill: progress-tracker)
- Map each scenario to implementation status
- Calculate spec coverage percentage
- Detect regressions (was passing, now failing)
- Store progress in long-term memory across sessions

## Memory & Context (Day 3)

- Store spec-to-code mappings in `memory/progress.json`
- Progressive disclosure: SKILL.md is lightweight; sub-skills load on demand
- Track implementation state across sessions

## Security Architecture (Day 4 — 7 Pillars)

1. **Ephemeral Sandbox**: generated code runs in isolated environment first
2. **Package Provenance**: every dependency verified against real registries
3. **Secret Zero-Tolerance**: no hardcoded credentials survive review
4. **Input Validation Mandatory**: every external input validated
5. **Output Sanitization**: outputs sanitized for target context
6. **Spec Traceability**: no orphan code without spec justification
7. **Continuous Evaluation**: tests run after every change

## Evaluation (Day 4)

After each cycle:
1. Run spec scenarios as automated tests
2. Report pass/fail per scenario
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
