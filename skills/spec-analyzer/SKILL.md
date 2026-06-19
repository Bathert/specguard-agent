# Spec Analyzer

Parse and validate Gherkin feature specifications, then generate an implementation plan.

## Trigger

When the user provides a `.feature` file path or pastes Gherkin content.

## Steps

### 1. Parse the spec
- Read the `.feature` file
- Extract: Feature name, description, Background, supported Scenarios with Given/When/Then steps, and data tables
- Identify Scenario Outlines and expand their Examples tables

### 2. Validate completeness
Check each scenario for:
- [ ] Has at least one Given step (precondition)
- [ ] Has at least one When step (action)
- [ ] Has at least one Then step (assertion)
- [ ] No ambiguous terms: "should work", "handle properly", "etc."
- [ ] Examples tables have values for all placeholders

### 3. Extract implementation units
For each scenario, identify:
- **Entities**: data structures needed
- **Actions**: functions/methods to implement
- **Assertions**: test cases to write
- **Dependencies**: what must exist before this scenario can be tested

### 4. Generate implementation plan
Output a JSON plan:

```json
{
  "feature": "Feature name",
  "scenarios_count": N,
  "tasks": [
    {
      "id": "T1",
      "scenario": "Scenario name",
      "description": "What to implement",
      "entities": ["Entity1"],
      "actions": ["action1"],
      "assertions": ["assertion1"],
      "depends_on": [],
      "estimated_complexity": "low|medium|high"
    }
  ],
  "warnings": ["any issues found"]
}
```

### 5. Report
```
📋 SPEC: <feature name>
📊 SCENARIOS: N total, M with issues
⚠️  WARNINGS: <list or "none">
📝 PLAN: N tasks, ordered by dependency
```

## Pitfalls
- Scenario Outlines with empty Examples tables are invalid
- "And" steps inherit the type of the preceding Given/When/Then
- Background steps apply to all scenarios — include them in each scenario's Given set
- This is a lightweight parser for the supported feature subset, not a complete Gherkin interpreter
