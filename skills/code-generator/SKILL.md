# Code Generator

Generate implementation code from a spec-driven plan. Every function traces back to a Gherkin scenario.

## Trigger

After spec-analyzer produces a plan, or when the user says "generate code for scenario X".

## Steps

### 1. Load the plan
- Read the JSON plan from spec-analyzer output
- Identify the next unimplemented task (respecting dependencies)

### 2. Generate code for one task
For each task:
- Create the entities (data classes, models)
- Implement the actions (functions, methods)
- Add spec-traceability comments: `# Traces to: Scenario "<name>"`

### 3. Code quality rules
- Every function must have a docstring
- Every external input must be validated
- No hardcoded secrets or credentials
- Use type hints where the language supports them

### 4. Write the file
- Place implementation in `src/` directory
- Name files after the feature (e.g., `src/task_manager.py`)

### 5. Report
```
📝 GENERATED: <file path>
🔗 TRACES TO: <scenario names>
📦 ENTITIES: N created
⚡ ACTIONS: N implemented
```

## Pitfalls
- Don't generate code for scenarios whose dependencies aren't met
- Don't over-implement — stick to what the spec requires
- If a scenario is an Outline, generate code that handles all Examples rows
