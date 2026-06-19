"""
Progress Tracker — tracks spec implementation across sessions.
Maps scenarios to status, calculates coverage metrics, detects regressions.

Usage:
    from src.progress_tracker import update_progress, get_dashboard
    update_progress("specs/task-manager.feature", "memory/progress.json")
    print(get_dashboard("memory/progress.json"))
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_progress(path: str) -> dict:
    """Load progress.json, return empty structure if not found."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"feature": "", "last_updated": "", "scenarios": {}, "metrics": {}}


def _save_progress(path: str, data: dict) -> None:
    """Save progress.json, creating parent dirs if needed."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _run_tests(test_dir: str) -> dict:
    """Run pytest and parse results. Returns {total, passed, failed, failures: [names]}."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_dir, "-v", "--tb=no"],
            capture_output=True, text=True, timeout=30,
        )
        output = result.stdout + result.stderr
        passed = []
        failed = []
        for line in output.splitlines():
            line = line.strip()
            if " PASSED" in line:
                # Extract test name: evals/test.py::test_name PASSED [ 6%]
                name = line.split("::")[-1].split(" PASSED")[0].strip()
                passed.append(name)
            elif " FAILED" in line:
                name = line.split("::")[-1].split(" FAILED")[0].strip()
                failed.append(name)
        return {"total": len(passed) + len(failed), "passed": passed, "failed": failed}
    except Exception as e:
        return {"total": 0, "passed": [], "failed": [], "error": str(e)}


def update_progress(spec_path: str, progress_path: str, test_dir: str = "evals/") -> dict:
    """
    Full update cycle:
    1. Parse spec → get scenario names
    2. Run tests → get pass/fail
    3. Compare with previous state → detect regressions
    4. Save updated progress

    Returns the updated progress dict.
    """
    # Import spec_analyzer to get scenario names
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.spec_analyzer import analyze_spec

    # Get current spec state
    spec = analyze_spec(spec_path)
    feature_name = spec["feature"]
    scenario_names = [s["name"] for s in spec["scenarios"]]

    # Load previous progress
    prev = _load_progress(progress_path)
    prev_scenarios = prev.get("scenarios", {})

    # Run tests
    test_results = _run_tests(test_dir)

    # Build scenario status map
    new_scenarios = {}
    regressions = []

    for name in scenario_names:
        prev_status = prev_scenarios.get(name, {}).get("status", "not_started")
        prev_test = prev_scenarios.get(name, {}).get("test_result", None)

        # Determine current test status by matching test names
        # Test names follow pattern: test_<scenario_name_snake_case>
        # But test names may be shorter — match on key words
        test_name = "test_" + name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        # Also try matching on first significant word (e.g. "Validate task priority" -> "test_validate")
        words = [w for w in name.lower().replace("(", "").replace(")", "").split()
                 if w not in ("a", "an", "the", "to", "by", "and", "is", "has", "with")]
        first_word = words[0] if words else ""
        alt_prefix = f"test_{first_word}"

        passed = test_results.get("passed", [])
        failed = test_results.get("failed", [])
        is_passing = any(test_name in t or alt_prefix in t for t in passed) if passed else False
        is_failing = any(test_name in t or alt_prefix in t for t in failed) if failed else False

        if is_passing:
            status = "tested"
            test_result = "pass"
        elif is_failing:
            status = "in_progress"
            test_result = "fail"
        else:
            status = "not_started" if prev_status == "not_started" else "in_progress"
            test_result = None

        # Detect regression: was passing, now failing
        if prev_test == "pass" and test_result == "fail":
            status = "regression"
            regressions.append(name)

        new_scenarios[name] = {
            "status": status,
            "last_change": _now(),
            "test_result": test_result,
            "files": prev_scenarios.get(name, {}).get("files", []),
        }

    # Calculate metrics
    total = len(scenario_names)
    implemented = sum(1 for s in new_scenarios.values() if s["status"] in ("implemented", "tested"))
    tested = sum(1 for s in new_scenarios.values() if s["status"] == "tested")
    coverage_pct = (implemented / total * 100) if total > 0 else 0
    test_pass_pct = (tested / implemented * 100) if implemented > 0 else 0

    progress = {
        "feature": feature_name,
        "last_updated": _now(),
        "scenarios": new_scenarios,
        "metrics": {
            "coverage_pct": round(coverage_pct, 1),
            "test_pass_pct": round(test_pass_pct, 1),
            "regressions": len(regressions),
            "regression_names": regressions,
            "tests_total": test_results["total"],
            "tests_passed": len(test_results["passed"]),
            "tests_failed": len(test_results["failed"]),
        },
    }

    _save_progress(progress_path, progress)
    return progress


def get_dashboard(progress_path: str) -> str:
    """Generate a human-readable dashboard from progress.json."""
    data = _load_progress(progress_path)

    if not data.get("scenarios"):
        return "No progress data found. Run update_progress first."

    metrics = data.get("metrics", {})
    scenarios = data.get("scenarios", {})
    feature = data.get("feature", "Unknown")

    total = len(scenarios)
    implemented = sum(1 for s in scenarios.values() if s["status"] in ("implemented", "tested"))
    tested = sum(1 for s in scenarios.values() if s["status"] == "tested")
    regressions = metrics.get("regressions", 0)

    lines = [
        "",
        "=" * 50,
        f"  PROGRESS DASHBOARD — {feature}",
        "=" * 50,
        f"  SCENARIOS:     {total} total",
        f"  IMPLEMENTED:   {implemented} ({metrics.get('coverage_pct', 0)}%)",
        f"  TESTED:        {tested} ({metrics.get('test_pass_pct', 0)}%)",
        f"  REGRESSIONS:   {regressions}",
        f"  TESTS:         {metrics.get('tests_passed', 0)}/{metrics.get('tests_total', 0)} passed",
        "=" * 50,
    ]

    # Show per-scenario status
    lines.append("  SCENARIO STATUS:")
    for name, info in scenarios.items():
        status = info["status"]
        icon = {"tested": "[PASS]", "implemented": "[OK]  ", "in_progress": "[WIP] ", "regression": "[REG] ", "not_started": "[--]  "}
        lines.append(f"    {icon.get(status, '[??]  ')} {name}")

    lines.append("=" * 50)

    # Next action
    if regressions > 0:
        reg_names = metrics.get("regression_names", [])
        lines.append(f"  NEXT: Fix regressions: {', '.join(reg_names)}")
    else:
        not_started = [n for n, s in scenarios.items() if s["status"] == "not_started"]
        if not_started:
            lines.append(f"  NEXT: Implement '{not_started[0]}'")
        elif tested == total:
            lines.append("  NEXT: All scenarios tested. Ready for deployment.")
        else:
            lines.append("  NEXT: Run tests to verify implementation.")

    lines.append("=" * 50)
    lines.append("")
    return "\n".join(lines)


def recommend_next(progress_path: str) -> str:
    """Return the recommended next action as a string."""
    data = _load_progress(progress_path)
    metrics = data.get("metrics", {})
    scenarios = data.get("scenarios", {})

    if metrics.get("regressions", 0) > 0:
        return f"Fix regressions: {', '.join(metrics.get('regression_names', []))}"

    not_started = [n for n, s in scenarios.items() if s["status"] == "not_started"]
    if not_started:
        return f"Implement '{not_started[0]}'"

    in_progress = [n for n, s in scenarios.items() if s["status"] == "in_progress"]
    if in_progress:
        return f"Complete '{in_progress[0]}' (code exists but not all tests pass)"

    total = len(scenarios)
    tested = sum(1 for s in scenarios.values() if s["status"] == "tested")
    if tested == total:
        return "All scenarios tested. Ready for deployment."

    return "Run tests to verify implementation."


if __name__ == "__main__":
    import sys as _sys
    spec = _sys.argv[1] if len(_sys.argv) > 1 else "specs/task-manager.feature"
    progress_file = _sys.argv[2] if len(_sys.argv) > 2 else "memory/progress.json"

    update_progress(spec, progress_file)
    print(get_dashboard(progress_file))