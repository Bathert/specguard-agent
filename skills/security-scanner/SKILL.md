# Security Scanner

Run lightweight static checks against generated or hand-written Python: package-name resolution, secrets, injection vectors, missing validation, output interpolation, and traceability.

## Trigger

After code-generator produces code, or when the user says "scan for security issues".

## Steps

### 1. Package-name resolution
- Extract third-party top-level Python imports from scanned files
- Optionally query PyPI for the import name
- Flag a name that definitively does not resolve; network failures are unknown, not clean provenance

### 2. Secret detection
Scan for patterns:
- `-----BEGIN.*PRIVATE KEY-----`
- `api_key\s*=\s*["'][A-Za-z0-9_-]{20,}["']`
- `token\s*=\s*["'][A-Za-z0-9_.-]{20,}["']`
- `password\s*=\s*["'][^"']+["']`
- `secret\s*=\s*["'][^"']+["']`

### 3. Injection vectors
Check for:
- String concatenation in SQL queries: `"SELECT * FROM" + input`
- Unsanitized shell: `os.system(user_input)`, `subprocess.call(user_input)`
- Unescaped HTML output: `f"<div>{user_input}</div>"`
- Unsanitized eval/exec: `eval(user_input)`, `exec(user_input)`

### 4. Output sanitization
Check for interpolated HTML, `Markup()`, and f-string template/response calls
that need context-aware escaping.

### 5. Input validation audit
For every function that accepts external input, verify:
- [ ] Type check exists
- [ ] Range/bounds check (if numeric)
- [ ] Length check (if string)
- [ ] Format validation (if email, URL, etc.)
- [ ] Sanitization before use in sensitive context

### 6. Traceability and evaluation
- Flag public functions with no nearby scenario trace comment
- Run pytest through the evaluation runner; use exact node IDs in the progress map

### 7. Report

```json
{
  "verdict": "pass|fail|pass_with_warnings",
  "issues": [
    {
      "severity": "critical|high|medium|low",
      "type": "slopsquatting|secret|injection|validation",
      "file": "path/to/file",
      "line": N,
      "description": "what's wrong",
      "fix": "how to fix"
    }
  ],
  "stats": {
    "packages_checked": N,
    "packages_flagged": M,
    "secrets_found": S,
    "injections_found": I,
    "validation_gaps": V
  }
}
```

### 6. Output
```
🔒 SECURITY SCAN: <verdict>
📦 PACKAGES: N checked, M flagged
🔑 SECRETS: S found
💉 INJECTIONS: I found
✅ VALIDATION: V gaps
```

## Pitfalls
- Test fixtures and config files may contain fake credentials — flag but note context
- Some packages have different names on different registries — check the project's actual package manager
- Don't flag `os.getenv("API_KEY")` — that's correct secret management
- This scanner is heuristic static analysis, not an execution sandbox, dependency provenance verifier, or full SAST tool
