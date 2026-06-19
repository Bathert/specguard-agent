from pathlib import Path

import pytest

from src.llm_core import (
    GeminiClient,
    LLMConfig,
    LLMConfigurationError,
    LLMGenerationError,
    extract_python_code,
    generate_with_llm,
    ReplayClient,
)


class FakeClient:
    config = LLMConfig(api_key="test-only-key", provider="gemini", model="test-model")

    def __init__(self, response: str):
        self.response = response

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        assert "implementation specialist" in system_prompt
        assert "Task Manager API" in user_prompt
        return self.response


def test_config_requires_environment_key_and_hides_it_from_repr():
    with pytest.raises(LLMConfigurationError, match="SPEC_GUARD_LLM_API_KEY"):
        LLMConfig.from_environment(environ={})

    config = LLMConfig(api_key="test-only-key")
    assert "test-only-key" not in repr(config)


def test_config_reads_untracked_dotenv_without_overriding_shell(tmp_path):
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        'export SPEC_GUARD_LLM_API_KEY="test-only-key"\nSPEC_GUARD_LLM_MODEL=test-model\n',
        encoding="utf-8",
    )

    config = LLMConfig.from_environment(dotenv_path=dotenv)

    assert config.provider == "gemini"
    assert config.model == "test-model"


def test_extract_python_code_rejects_unfenced_or_invalid_responses():
    with pytest.raises(LLMGenerationError, match="fenced"):
        extract_python_code("def unwrapped(): pass")

    with pytest.raises(LLMGenerationError, match="does not parse"):
        extract_python_code("```python\ndef broken(:\n```")


def test_gemini_client_uses_header_auth_and_extracts_candidate(monkeypatch):
    captured = {}

    def fake_post(url, headers, payload, timeout):
        captured.update(url=url, headers=headers, payload=payload, timeout=timeout)
        return {"candidates": [{"content": {"parts": [{"text": "```python\npass\n```"}]}}]}

    monkeypatch.setattr("src.llm_core._post_json", fake_post)
    client = GeminiClient(LLMConfig(api_key="test-only-key", provider="gemini", model="test-model"))

    result = client.complete("system", "user")

    assert result == "```python\npass\n```"
    assert captured["headers"] == {"x-goog-api-key": "test-only-key"}
    assert captured["url"].endswith("/models/test-model:generateContent")
    assert captured["payload"]["system_instruction"]["parts"][0]["text"] == "system"


def test_llm_generation_parses_scans_and_writes_atomically(tmp_path):
    target = tmp_path / "task_manager.py"
    response = '''```python
# Traces to: Scenario "Create a new task"
def create_task(title: str) -> dict[str, str]:
    """Create a task from validated input."""
    if not title or not title.strip():
        raise ValueError("title is required")
    return {"title": title.strip()}
```'''

    result = generate_with_llm(
        "specs/task-manager.feature",
        str(target),
        FakeClient(response),
    )

    assert result["provider"] == "gemini"
    assert result["security_warnings"] == 0
    assert "def create_task" in target.read_text(encoding="utf-8")
    assert not list(Path(tmp_path).glob("*.specguard-candidate"))


def test_llm_generation_rejects_blocking_security_findings(tmp_path):
    target = tmp_path / "unsafe.py"
    response = '''```python
# Traces to: Scenario "Create a new task"
def create_task(value: str) -> object:
    return eval(value)
```'''

    with pytest.raises(LLMGenerationError, match="rejected"):
        generate_with_llm("specs/task-manager.feature", str(target), FakeClient(response))

    assert not target.exists()


def test_replay_client_supports_offline_llm_gate():
    client = ReplayClient("```python\npass\n```", "fixture.md")

    assert client.config.provider == "replay"
    assert client.complete("system", "user") == "```python\npass\n```"
