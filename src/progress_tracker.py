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
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.evaluation_runner import run_pytest


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


def _load_scenario_map(path: str) -> dict[str, dict]:
    """Load explicit scenario-to-test mappings; never infer them from names."""
    with open(path, "r", encoding="utf-8") as file:
        mapping = json.load(file)
    if not isinstance(mapping, dict):
        raise ValueError("scenario map must be a JSON object")
    for scenario, entry in mapping.items():
        if not isinstance(entry, dict) or not isinstance(entry.get("tests"), list):
            raise ValueError(f"scenario map entry for '{scenario}' must contain a tests list")
        if not all(isinstance(test, str) and "::" in test for test in entry["tests"]):
            raise ValueError(f"scenario map entry for '{scenario}' has an invalid test node id")
        if "files" in entry and not all(isinstance(file, str) for file in entry["files"]):
            raise ValueError(f"scenario map entry for '{scenario}' has invalid file paths")
    return mapping


def _matches_node_id(reference: str, node_id: str) -> bool:
    """Match one exact pytest node id, including parametrized instances only."""
    return node_id == reference or node_id.startswith(f"{reference}[")


def update_progress(
    spec_path: str,
    progress_path: str,
    test_dir: str = "evals/",
    scenario_map_path: str = "evals/scenario_map.json",
    test_results: Optional[dict] = None,
) -> dict:
    """
    Full update cycle:
    1. Parse spec → get scenario names
    2. Use explicit scenario-to-test mappings to evaluate each scenario
    3. Compare with previous state → detect regressions
    4. Save updated progress only when pytest actually ran

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

    scenario_map = _load_scenario_map(scenario_map_path)
    test_results = test_results or run_pytest(test_dir)
    if not test_results.get("available", False):
        # A missing dependency or collection failure is not a regression. Do not
        # erase a previously good dashboard merely because the runner is broken.
        preserved = dict(prev)
        preserved["update_skipped"] = {
            "at": _now(),
            "reason": test_results.get("error", "pytest did not produce usable results"),
        }
        return preserved

    # Build scenario status map
    new_scenarios = {}
    regressions = []

    for name in scenario_names:
        entry = scenario_map.get(name, {})
        expected_tests = entry.get("tests", [])
        files = entry.get("files", [])
        prev_test = prev_scenarios.get(name, {}).get("test_result", None)
        results_by_reference = {
            reference: [
                result
                for node_id, result in test_results.get("tests", {}).items()
                if _matches_node_id(reference, node_id)
            ]
            for reference in expected_tests
        }
        matched_results = [result for results in results_by_reference.values() for result in results]
        every_expected_test_reported = bool(expected_tests) and all(results_by_reference.values())
        all_files_exist = bool(files) and all(Path(path).is_file() for path in files)

        if every_expected_test_reported and all(result == "passed" for result in matched_results):
            status = "tested"
            test_result = "pass"
        elif any(result in ("failed", "error") for result in matched_results):
            status = "in_progress"
            test_result = "fail"
        else:
            status = "implemented" if all_files_exist else "not_started"
            test_result = None

        # Detect regression: was passing, now failing
        if prev_test == "pass" and test_result == "fail":
            status = "regression"
            regressions.append(name)

        new_scenarios[name] = {
            "status": status,
            "last_change": _now(),
            "test_result": test_result,
            "files": files,
        }

    # Calculate metrics
    total = len(scenario_names)
    implemented = sum(1 for s in new_scenarios.values() if s["status"] in ("implemented", "tested", "in_progress", "regression"))
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
            "tests_failed": len(test_results["failed"]) + len(test_results.get("errors", [])),
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
    implemented = sum(
        1
        for s in scenarios.values()
        if s["status"] in ("implemented", "tested", "in_progress", "regression")
    )
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
            lines.append("  NEXT: All scenarios tested. Ready for release review.")
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
        return "All scenarios tested. Ready for release review."

    return "Run tests to verify implementation."


if __name__ == "__main__":
    import sys as _sys
    spec = _sys.argv[1] if len(_sys.argv) > 1 else "specs/task-manager.feature"
    progress_file = _sys.argv[2] if len(_sys.argv) > 2 else "memory/progress.json"

    update_progress(spec, progress_file)
    print(get_dashboard(progress_file))
