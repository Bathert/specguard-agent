from types import SimpleNamespace
from unittest.mock import patch

from src.evaluation_runner import run_pytest


@patch("src.evaluation_runner.subprocess.run")
def test_runner_returns_exact_pytest_node_ids(mock_run):
    mock_run.return_value = SimpleNamespace(
        returncode=1,
        stdout=(
            "evals/test_feature.py::test_create PASSED [ 50%]\n"
            "evals/test_feature.py::test_update FAILED [100%]\n"
        ),
        stderr="",
    )

    result = run_pytest("evals")

    assert result["available"] is True
    assert result["successful"] is False
    assert result["tests"] == {
        "evals/test_feature.py::test_create": "passed",
        "evals/test_feature.py::test_update": "failed",
    }
    assert result["errors"] == []


@patch("src.evaluation_runner.subprocess.run")
def test_runner_marks_missing_pytest_as_unavailable(mock_run):
    mock_run.return_value = SimpleNamespace(
        returncode=1,
        stdout="",
        stderr="No module named pytest\n",
    )

    result = run_pytest("evals")

    assert result["available"] is False
    assert "not installed" in result["error"]
