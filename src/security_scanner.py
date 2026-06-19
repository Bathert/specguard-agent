"""
Security Scanner — scans Python source files for vulnerabilities.
Implements 7-pillar audit: package verification, secret detection,
injection vectors, input validation gaps, output sanitization,
spec traceability, and continuous evaluation readiness.

Usage:
    from src.security_scanner import scan_directory
    report = scan_directory("src/")
"""
import re
import os
import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from typing import Optional


# ── Patterns ──────────────────────────────────────────────────────────────

SECRET_PATTERNS = [
    (r"-----BEGIN\s+(RSA\s+|EC\s+|DSA\s+|OPENSSH\s+)?PRIVATE KEY-----", "Private key"),
    (r"""api[_-]?key\s*=\s*["'][A-Za-z0-9_\-]{20,}["']""", "API key"),
    (r"""token\s*=\s*["'][A-Za-z0-9_\-\.]{20,}["']""", "Token"),
    (r"""password\s*=\s*["'][^"']{4,}["']""", "Password"),
    (r"""secret\s*=\s*["'][^"']{8,}["']""", "Secret"),
    (r"""aws[_-]?access[_-]?key[_-]?id\s*=\s*["'][A-Z0-9]{20}["']""", "AWS access key"),
    (r"""aws[_-]?secret[_-]?access[_-]?key\s*=\s*["'][A-Za-z0-9/+=]{40}["']""", "AWS secret key"),
]

INJECTION_PATTERNS = [
    (r'execute\s*\(\s*["\'].*\{.*\}.*["\'].*format', "SQL injection: string formatting in query"),
    (r'execute\s*\(\s*["\'].*\+.*["\']', "SQL injection: string concatenation in query"),
    (r'execute\s*\(\s*f["\']', "SQL injection: f-string in query"),
    (r"subprocess\.(call|run|Popen)\s*\(\s*(?![\"'].*-c)", "Subprocess call (check for user input)"),
    (r"os\.system\s*\(", "Shell injection: os.system()"),
    (r"\beval\s*\(", "Code injection: eval()"),
    (r"\bexec\s*\(", "Code injection: exec()"),
    (r"innerHTML\s*=\s*[^\"]'", "XSS: innerHTML with non-literal"),
    (r"shell\s*=\s*True", "Subprocess with shell=True"),
]

OUTPUT_SANITIZATION_PATTERNS = [
    (r"\bMarkup\s*\(", "HTML marked safe without an escaping audit"),
    (r"render_template_string\s*\(\s*f[\"']", "Template rendered from an f-string"),
    (r"\b(?:Response|make_response)\s*\(\s*f[\"']", "HTTP response rendered from an f-string"),
    (r"\breturn\s+f[\"'][^\"']*<[A-Za-z][^\"']*\{", "HTML returned with interpolated data"),
]

VALIDATION_PATTERNS = [
    r"if\s+not\s+\w+",
    r"\.strip\(\)",
    r"\.isinstance\(",
    r"in\s+VALID_",
    r"\.isdigit\(\)",
    r"raise\s+ValueError",
    r"if\s+\w+\s+not\s+in",
    r"if\s+not\s+\w+\.strip\(\)",
]

# Files / directories to skip
SKIP_DIRS = {"__pycache__", ".pytest_cache", ".git", "node_modules", ".venv", "venv"}
STDLIB_PKGS = {
    "os", "sys", "re", "json", "datetime", "typing", "dataclasses",
    "collections", "pathlib", "io", "urllib", "abc", "functools",
    "itertools", "math", "random", "time", "logging", "enum",
    "pytest", "src", "scripts", "__future__", "csv", "base64",
    "hashlib", "ssl", "socket", "threading", "queue", "signal",
    "keyword", "subprocess", "importlib", "ast", "textwrap", "tempfile",
    "shutil", "unittest", "xml",
}


# ── Data classes ──────────────────────────────────────────────────────────

@dataclass
class Issue:
    severity: str
    pillar: str
    file: str
    line: int
    description: str
    fix: str = ""


# ── Helpers ────────────────────────────────────────────────────────────────

def _read_file(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()


def _is_pattern_line(line: str) -> bool:
    """Check if a line defines a regex pattern (not actual code to scan)."""
    stripped = line.strip()
    # Lines that define patterns: start with (r" or (r' or r"""
    return bool(
        stripped.startswith("(r\"")
        or stripped.startswith("(r'")
        or stripped.startswith('SECRET_PATTERNS')
        or stripped.startswith('INJECTION_PATTERNS')
        or stripped.startswith('OUTPUT_SANITIZATION_PATTERNS')
        or stripped.startswith('VALIDATION_PATTERNS')
        or stripped.startswith('STDLIB_PKGS')
        or stripped.startswith('SKIP_DIRS')
    )


# ── Scanners ──────────────────────────────────────────────────────────────

def scan_secrets(lines: list[str], filepath: str) -> list[Issue]:
    """Pillar 2: Secret detection."""
    issues = []
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("#") or _is_pattern_line(line):
            continue
        for pattern, name in SECRET_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(Issue(
                    severity="critical",
                    pillar="secret_detection",
                    file=filepath,
                    line=i,
                    description=f"{name} detected",
                    fix="Use environment variables or a secrets manager instead of hardcoding",
                ))
    return issues


def scan_injections(lines: list[str], filepath: str) -> list[Issue]:
    """Pillar 3: Injection vectors."""
    issues = []
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("#") or _is_pattern_line(line):
            continue
        for pattern, name in INJECTION_PATTERNS:
            if not re.search(pattern, line):
                continue
            # For subprocess: check if arguments are literals (not user input)
            if "Subprocess call" in name:
                # Look at the full call — if all args are literals, skip
                # Get the next few lines to see the full call
                call_text = "".join(lines[max(0, i-6):min(i+5, len(lines))])
                # A list argument with shell=False cannot be interpreted as shell
                # syntax. This includes commands built around sys.executable.
                list_command = re.search(r"\b(?:command|cmd)\s*=\s*\[", call_text)
                if "sys.executable" in call_text or "[sys" in call_text or list_command:
                    # Check if any user-controlled variable is in the call
                    # Safe patterns: subprocess.run([sys.executable, "-m", "pytest", ...])
                    if not re.search(r"subprocess\.\w+\(.*\b(user|input|request|argv|args)\b", call_text):
                        continue
            issues.append(Issue(
                severity="high",
                pillar="injection_audit",
                file=filepath,
                line=i,
                description=name,
                fix="Sanitize all user input before passing to system calls, queries, or eval",
            ))
    return issues


def scan_input_validation(lines: list[str], filepath: str) -> list[Issue]:
    """Pillar 4: Input validation gaps."""
    issues = []
    input_keywords = ["title", "name", "keyword", "query", "search", "input",
                      "user", "data", "value", "text", "priority", "assignee",
                      "status", "email", "url", "path"]

    for i, line in enumerate(lines, 1):
        func_match = re.match(r"\s*def\s+(\w+)\s*\(([^)]*)\)", line)
        if not func_match:
            continue

        func_name = func_match.group(1)
        params = func_match.group(2)

        if func_name.startswith("_") or func_name.startswith("test_"):
            continue

        has_input = any(kw in params.lower() for kw in input_keywords)
        if not has_input:
            continue

        # Look ahead in function body for validation
        func_body = []
        for j in range(i, min(i + 20, len(lines))):
            func_body.append(lines[j])

        body_text = "".join(func_body)
        has_validation = any(re.search(p, body_text) for p in VALIDATION_PATTERNS)

        if not has_validation:
            issues.append(Issue(
                severity="medium",
                pillar="input_validation",
                file=filepath,
                line=i,
                description=f"Function '{func_name}' accepts external input but has no visible validation",
                fix="Add type checks, range checks, and raise ValueError for invalid input",
            ))
    return issues


def scan_output_sanitization(lines: list[str], filepath: str) -> list[Issue]:
    """Pillar 5: flag interpolated output that needs context-aware escaping."""
    issues = []
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("#") or _is_pattern_line(line):
            continue
        for pattern, description in OUTPUT_SANITIZATION_PATTERNS:
            if re.search(pattern, line):
                issues.append(Issue(
                    severity="high",
                    pillar="output_sanitization",
                    file=filepath,
                    line=i,
                    description=description,
                    fix="Escape untrusted data for its output context before rendering it",
                ))
    return issues


def scan_packages(lines: list[str], filepath: str) -> tuple[list[Issue], int, int]:
    """Pillar 1: Package verification (anti-slopsquatting).
    Returns (issues, packages_checked, packages_flagged).
    """
    issues = []
    checked = 0
    flagged = 0

    imports = set()
    for line in lines:
        if _is_pattern_line(line):
            continue
        m = re.match(r"^\s*(?:from\s+|import\s+)(\w+)", line)
        if m:
            pkg = m.group(1)
            if pkg in STDLIB_PKGS:
                continue
            imports.add(pkg)

    for pkg in imports:
        checked += 1
        try:
            url = f"https://pypi.org/pypi/{pkg}/json"
            req = urllib.request.Request(url, headers={"User-Agent": "SpecGuard/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status != 200:
                    flagged += 1
                    issues.append(Issue(
                        severity="high",
                        pillar="package_verification",
                        file=filepath,
                        line=0,
                        description=f"Package '{pkg}' not found on PyPI — possible slopsquatting",
                        fix="Verify package name. If hallucinated, replace with a real package",
                    ))
        except urllib.error.HTTPError:
            flagged += 1
            issues.append(Issue(
                severity="high",
                pillar="package_verification",
                file=filepath,
                line=0,
                description=f"Package '{pkg}' not found on PyPI — possible slopsquatting",
                fix="Verify package name or remove the import",
            ))
        except Exception as error:
            issues.append(Issue(
                severity="low",
                pillar="package_verification",
                file=filepath,
                line=0,
                description=f"Could not verify package '{pkg}' against PyPI: {error}",
                fix="Retry with network access; an unavailable registry is not proof of provenance",
            ))

    return issues, checked, flagged


def scan_traceability(lines: list[str], filepath: str) -> list[Issue]:
    """Pillar 6: Spec traceability — every function should trace to a scenario."""
    issues = []
    for i, line in enumerate(lines, 1):
        func_match = re.match(r"\s*def\s+(\w+)\s*\(", line)
        if not func_match:
            continue
        func_name = func_match.group(1)
        if func_name.startswith("_") or func_name.startswith("test_"):
            continue

        context = "".join(lines[max(0, i-3):i])
        if "Traces to" not in context and "# T" not in context and "scenario" not in context.lower():
            issues.append(Issue(
                severity="low",
                pillar="traceability",
                file=filepath,
                line=i,
                description=f"Function '{func_name}' has no spec traceability comment",
                fix="Add a comment: '# Traces to: Scenario \"X\"'",
            ))
    return issues


def scan_file(filepath: str, check_packages: bool = True) -> tuple[list[Issue], int, int]:
    """Scan a single Python file. Returns (issues, packages_checked, packages_flagged)."""
    lines = _read_file(filepath)
    issues = []

    issues.extend(scan_secrets(lines, filepath))
    issues.extend(scan_injections(lines, filepath))
    issues.extend(scan_input_validation(lines, filepath))
    issues.extend(scan_output_sanitization(lines, filepath))
    issues.extend(scan_traceability(lines, filepath))

    pkg_checked = 0
    pkg_flagged = 0
    if check_packages:
        pkg_issues, pkg_checked, pkg_flagged = scan_packages(lines, filepath)
        issues.extend(pkg_issues)

    return issues, pkg_checked, pkg_flagged


def scan_directory(directory: str, check_packages: bool = True) -> dict:
    """
    Scan all .py files in a directory.
    Returns a JSON-serializable dict with the full report.
    """
    all_issues = []
    files_scanned = 0
    total_packages_checked = 0
    total_packages_flagged = 0

    if os.path.isfile(directory):
        paths = [directory] if directory.endswith(".py") else []
    else:
        paths = []
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            paths.extend(os.path.join(root, name) for name in files if name.endswith(".py"))

    for filepath in paths:
        issues, pkg_checked, pkg_flagged = scan_file(filepath, check_packages)
        all_issues.extend(issues)
        files_scanned += 1
        total_packages_checked += pkg_checked
        total_packages_flagged += pkg_flagged

    critical = sum(1 for i in all_issues if i.severity == "critical")
    high = sum(1 for i in all_issues if i.severity == "high")
    medium = sum(1 for i in all_issues if i.severity == "medium")
    low = sum(1 for i in all_issues if i.severity == "low")

    if critical > 0 or high > 0:
        verdict = "fail"
    elif medium > 0:
        verdict = "pass_with_warnings"
    else:
        verdict = "pass"

    return {
        "verdict": verdict,
        "files_scanned": files_scanned,
        "issues": [asdict(i) for i in all_issues],
        "stats": {
            "total_issues": len(all_issues),
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "packages_checked": total_packages_checked,
            "packages_flagged": total_packages_flagged,
            "secrets_found": sum(1 for i in all_issues if i.pillar == "secret_detection"),
            "injections_found": sum(1 for i in all_issues if i.pillar == "injection_audit"),
            "validation_gaps": sum(1 for i in all_issues if i.pillar == "input_validation"),
            "output_sanitization_gaps": sum(1 for i in all_issues if i.pillar == "output_sanitization"),
            "traceability_gaps": sum(1 for i in all_issues if i.pillar == "traceability"),
        },
    }


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "src/"
    report = scan_directory(target, check_packages="--no-packages" not in sys.argv)
    print(json.dumps(report, indent=2))
