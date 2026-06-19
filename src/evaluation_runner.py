"""Run pytest once and expose structured, scenario-safe test results."""
from __future__ import annotations

import re
import subprocess
import sys
from typing import Any


_RESULT_LINE = re.compile(
    r"^(?P<nodeid>.+::[^\s]+)\s+(?P<outcome>PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)(?:\s|$)"
)
_OUTCOME_MAP = {
    "PASSED": "passed",
    "FAILED": "failed",
    "ERROR": "error",
    "SKIPPED": "skipped",
    "XFAIL": "skipped",
    "XPASS": "passed",
}


def run_pytest(test_dir: str, timeout: int = 60) -> dict[str, Any]:
    """Run pytest and return node-id-level results without guessing test names.

    ``available`` is false only when pytest could not execute at all. A failing
    assertion still produces usable results and must update regression status.
    """
    command = [sys.executable, "-m", "pytest", test_dir, "-v", "--tb=short", "--color=no"]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        return {
            "available": False,
            "successful": False,
            "returncode": None,
            "tests": {},
            "passed": [],
            "failed": [],
            "errors": [],
            "skipped": [],
            "total": 0,
            "output": "",
            "error": f"pytest timed out after {timeout} seconds: {error}",
        }
    except OSError as error:
        return {
            "available": False,
            "successful": False,
            "returncode": None,
            "tests": {},
            "passed": [],
            "failed": [],
            "errors": [],
            "skipped": [],
            "total": 0,
            "output": "",
            "error": f"could not start pytest: {error}",
        }

    output = completed.stdout + completed.stderr
    tests: dict[str, str] = {}
    for raw_line in output.splitlines():
        match = _RESULT_LINE.match(raw_line.strip())
        if match:
            tests[match.group("nodeid")] = _OUTCOME_MAP[match.group("outcome")]

    grouped = {
        outcome: sorted(node_id for node_id, result in tests.items() if result == outcome)
        for outcome in ("passed", "failed", "error", "skipped")
    }

    execution_error = None
    if "No module named pytest" in output:
        execution_error = "pytest is not installed; install the project's test dependencies first"
    elif completed.returncode not in (0, 1):
        execution_error = f"pytest could not complete (exit {completed.returncode})"
    elif completed.returncode and not tests:
        execution_error = "pytest failed before reporting any test result"

    return {
        "available": execution_error is None,
        "successful": completed.returncode == 0,
        "returncode": completed.returncode,
        "tests": tests,
        **grouped,
        "total": len(tests),
        "output": output,
        "error": execution_error,
    }
