import py_compile

import pytest

from src.code_generator import generate_scaffold


def test_generate_scaffold_creates_traceable_compilable_python(tmp_path):
    output = tmp_path / "task_manager_scaffold.py"

    result = generate_scaffold("specs/task-manager.feature", str(output))

    source = output.read_text(encoding="utf-8")
    assert result["scenarios"] == 9
    assert "class TaskManagerApiImplementation:" in source
    assert "def create(self, **payload: Any) -> None:" in source
    assert "# Traces to: 'Create a new task'" in source
    py_compile.compile(str(output), doraise=True)


def test_generate_scaffold_does_not_overwrite_without_opt_in(tmp_path):
    output = tmp_path / "existing.py"
    output.write_text("sentinel\n", encoding="utf-8")

    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        generate_scaffold("specs/task-manager.feature", str(output))

    assert output.read_text(encoding="utf-8") == "sentinel\n"


def test_generate_scaffold_escapes_feature_text_in_generated_python(tmp_path):
    spec = tmp_path / "hostile.feature"
    spec.write_text(
        '''Feature: Bad \"\"\" feature
  Scenario: Create \"quoted\" item
    Given an item exists
    When I create an item
    Then it exists
''',
        encoding="utf-8",
    )
    output = tmp_path / "scaffold.py"

    generate_scaffold(str(spec), str(output))

    py_compile.compile(str(output), doraise=True)
