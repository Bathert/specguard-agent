import json
from pathlib import Path

from src.progress_tracker import update_progress


def _passing_results() -> dict:
    mapping = json.loads(Path("evals/scenario_map.json").read_text(encoding="utf-8"))
    tests = {
        test_id: "passed"
        for entry in mapping.values()
        for test_id in entry["tests"]
    }
    return {
        "available": True,
        "successful": True,
        "tests": tests,
        "passed": list(tests),
        "failed": [],
        "errors": [],
        "total": len(tests),
        "output": "",
        "error": None,
    }


def test_progress_uses_explicit_mapping_for_scenario_coverage(tmp_path):
    progress_path = tmp_path / "progress.json"

    progress = update_progress(
        "specs/task-manager.feature",
        str(progress_path),
        test_results=_passing_results(),
    )

    assert progress["metrics"]["coverage_pct"] == 100.0
    assert progress["metrics"]["test_pass_pct"] == 100.0
    assert all(item["status"] == "tested" for item in progress["scenarios"].values())


def test_progress_does_not_overwrite_dashboard_when_pytest_is_unavailable(tmp_path):
    progress_path = tmp_path / "progress.json"
    original = '{"feature": "Stable", "scenarios": {}}'
    progress_path.write_text(original, encoding="utf-8")

    progress = update_progress(
        "specs/task-manager.feature",
        str(progress_path),
        test_results={"available": False, "error": "pytest is not installed"},
    )

    assert progress["update_skipped"]["reason"] == "pytest is not installed"
    assert progress_path.read_text(encoding="utf-8") == original


def test_similarly_named_test_cannot_mark_a_scenario_as_tested(tmp_path):
    progress_path = tmp_path / "progress.json"
    results = _passing_results()
    results["tests"] = {"evals/test_other.py::test_create": "passed"}
    results["passed"] = ["evals/test_other.py::test_create"]
    results["total"] = 1

    progress = update_progress(
        "specs/task-manager.feature",
        str(progress_path),
        test_results=results,
    )

    assert progress["scenarios"]["Create a new task"]["status"] == "implemented"


def test_one_failed_parameter_marks_the_entire_outline_as_in_progress(tmp_path):
    progress_path = tmp_path / "progress.json"
    results = _passing_results()
    results["tests"] = {
        "evals/test_task_manager.py::test_validate_priority[urgent]": "passed",
        "evals/test_task_manager.py::test_validate_priority[critical]": "failed",
        "evals/test_task_manager.py::test_validate_priority[unknown]": "passed",
    }
    results["passed"] = [
        "evals/test_task_manager.py::test_validate_priority[urgent]",
        "evals/test_task_manager.py::test_validate_priority[unknown]",
    ]
    results["failed"] = ["evals/test_task_manager.py::test_validate_priority[critical]"]
    results["total"] = 3

    progress = update_progress(
        "specs/task-manager.feature",
        str(progress_path),
        test_results=results,
    )

    assert progress["scenarios"]["Validate task priority"]["status"] == "in_progress"
    assert progress["scenarios"]["Validate task priority"]["test_result"] == "fail"
