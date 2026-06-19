# Code Generator

Generate a safe Python implementation scaffold from a spec-driven plan. Every generated method traces back to a Gherkin scenario.

## Trigger

After spec-analyzer produces a plan, or when the user says "generate code for scenario X".

For an LLM implementation, use `agent.py llm-generate` with a runtime-only
`SPEC_GUARD_LLM_API_KEY`; never add a key to a source file, prompt artifact, or
Git history.

## Steps

### 1. Load the plan
- Read the JSON plan from spec-analyzer output
- Identify the next unimplemented task (respecting dependencies)

### 2. Generate code for one task
For each task:
- Create traceable method stubs for extracted actions
- Keep business logic explicitly incomplete rather than pretending it was inferred safely
- Add spec-traceability comments: `# Traces to: Scenario "<name>"`

### 3. Code quality rules
- Every function must have a docstring
- Every external input must be validated
- No hardcoded secrets or credentials
- Use type hints where the language supports them

### 4. Write the file
- Write to an explicit output path (default: `generated/feature_scaffold.py`)
- Refuse to overwrite an existing file unless `--overwrite` was requested

### 5. Report
```
📝 GENERATED: <file path>
🔗 TRACES TO: <scenario names>
📦 ENTITIES: N created
⚡ ACTIONS: N implemented
```

## Pitfalls
- The deterministic generator does not replace a reviewed implementation or an LLM coding step
- The LLM generator accepts only fenced Python, parses it, scans it, and writes atomically after no high/critical findings
- Don't over-implement — stick to what the spec requires
- If a scenario is an Outline, generate a method traceable to its parent scenario and add parametrized tests for all Examples rows
