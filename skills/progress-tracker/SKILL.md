# Progress Tracker

Track spec implementation progress across sessions, maintain coverage metrics, detect regressions.

## Trigger

After each code-generator + security-scanner cycle, or when user asks "status", "progress", "coverage".

## Steps

### 1. Load state
- Read the implementation plan (from spec-analyzer)
- Read latest security scan results
- Load previous progress from `memory/progress.json` (if exists)

### 2. Map scenarios to status

Use `evals/scenario_map.json` as the explicit mapping from a scenario name to
pytest node IDs and implementation/test files. Never infer a match from a test
name prefix. A parametrized node reference passes only when every collected
parameter instance passes.

| Status | Meaning |
|--------|---------|
| `not_started` | No code written |
| `in_progress` | Code exists but not all assertions pass |
| `implemented` | Code exists, passes review |
| `tested` | Code passes automated tests |
| `regression` | Was passing, now failing |

### 3. Calculate metrics
- **Coverage**: implemented / total scenarios
- **Test pass rate**: tested / implemented
- **Regressions**: scenarios that flipped from pass to fail
- **Velocity**: scenarios completed per session

### 4. Store state
Save to `memory/progress.json`:
```json
{
  "feature": "Feature name",
  "last_updated": "ISO timestamp",
  "scenarios": {
    "Scenario name": {
      "status": "implemented",
      "last_change": "ISO timestamp",
      "test_result": "pass",
      "files": ["src/impl.py", "evals/test.py"]
    }
  },
  "metrics": {
    "coverage_pct": 75.0,
    "test_pass_pct": 100.0,
    "regressions": 0
  }
}
```

### 5. Dashboard
```
📊 PROGRESS — <feature name>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 SCENARIOS: N total
✅ IMPLEMENTED: M (X%)
🧪 TESTED: T (Y%)
🔴 REGRESSIONS: R
⚡ VELOCITY: V/session
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 NEXT: <recommended scenario>
⚠️  BLOCKERS: <any dependency issues>
```

### 6. Recommend next action
- Highest-priority `not_started` scenario with satisfied dependencies
- If regressions exist → fix those first
- If 100% coverage + all tests pass → recommend deployment

## Pitfalls
- Scenario Outlines expand to N scenarios (one per Examples row) — track each separately
- Background steps are not separate scenarios
- Do not overwrite a previous dashboard when pytest is unavailable or cannot collect tests
- A scenario marked `implemented` without mapped implementation and test files should be flagged
