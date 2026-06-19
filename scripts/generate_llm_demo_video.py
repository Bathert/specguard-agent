#!/usr/bin/env python3
"""Build an English demo video from real SpecGuard console output.

The optional URL-slug case replays a recorded LLM response through the exact
parse, scan, write, and behavior-verification gate. This keeps the video
reproducible even where a live provider is region-restricted.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slides import make_case_study_frame, make_slide, make_terminal_frame


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKDIR = ROOT / "tmp_video_llm"
DEFAULT_OUTPUT = ROOT / "specguard-llm-demo.mp4"
SECRET_PATTERN = re.compile(r"(?i)(api[_-]?key|authorization|bearer)\s*[:=]\s*[^\s]+")
TERMINAL_REPLACEMENTS = str.maketrans({
    "🧠": "", "📋": "", "📝": "", "🔒": "", "🧪": "", "📊": "",
    "╔": "+", "╗": "+", "╚": "+", "╝": "+", "╠": "+", "╣": "+",
    "║": "|", "═": "=", "━": "-", "—": "-", "→": ">", "…": "...",
})


@dataclass(frozen=True)
class Scene:
    title: str
    narration: str
    accent: str = "accent_green"
    body: str = ""
    terminal_lines: tuple[str, ...] = ()
    case_spec_lines: tuple[str, ...] = ()
    case_code_lines: tuple[str, ...] = ()


def _run(command: list[str], *, timeout: int = 90) -> str:
    """Capture a real command transcript and fail loudly on a non-zero exit."""
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    output = completed.stdout + completed.stderr
    if completed.returncode:
        raise RuntimeError(f"Command failed ({completed.returncode}): {' '.join(command)}\n{output}")
    return SECRET_PATTERN.sub(r"\1=[REDACTED]", output)


def _tail(transcript: str, lines: int) -> list[str]:
    clean = [line.translate(TERMINAL_REPLACEMENTS).rstrip() for line in transcript.splitlines() if line.strip()]
    return clean[-lines:]


def capture_console_transcripts(workdir: Path, *, include_case: bool) -> dict[str, object]:
    """Run the real CLI and return presentation-sized excerpts plus optional LLM evidence."""
    python = sys.executable
    generated = Path("/tmp/specguard-video-generated.py")
    progress = Path("/tmp/specguard-video-progress.json")
    generated.unlink(missing_ok=True)
    progress.unlink(missing_ok=True)

    llm_dry_run = _run([
        python, "agent.py", "llm-generate", "--dry-run",
        "--llm-provider", "gemini", "--llm-model", "gemini-2.5-flash",
    ])
    full_pipeline = _run([
        python, "agent.py", "--generate", "--output", str(generated),
        "--progress", str(progress), "--no-packages",
    ])
    tests = _run([python, "-m", "pytest", "-q"])
    transcripts: dict[str, object] = {
        "llm": ["$ python agent.py llm-generate --dry-run", *_tail(llm_dry_run, 11)],
        "pipeline": ["$ python agent.py --generate --no-packages", *_tail(full_pipeline, 26)],
        "tests": ["$ python -m pytest -q", *_tail(tests, 5)],
    }

    if not include_case:
        return transcripts

    case_spec = ROOT / "examples" / "url-slug.feature"
    case_output = Path("/tmp/specguard-video-slugify.py")
    case_output.unlink(missing_ok=True)
    contract = "Export exactly one public function: slugify(value: str) -> str."
    generation = _run([
        python, "agent.py", "llm-generate", "--spec", str(case_spec),
        "--output", str(case_output), "--overwrite",
        "--llm-contract", contract,
        "--llm-response-file", "examples/url_slug_response.md",
    ], timeout=120)
    verification_script = f"""import importlib.util
spec = importlib.util.spec_from_file_location('generated_slugify', {str(case_output)!r})
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert module.slugify('Hello, World!') == 'hello-world'
assert module.slugify('  AI   Agents -- Intensive  ') == 'ai-agents-intensive'
try:
    module.slugify('   ')
except ValueError:
    pass
else:
    raise AssertionError('empty input must raise ValueError')
print('slugify: 3/3 behavioral checks passed')
"""
    verification = _run([python, "-c", verification_script])
    transcripts["case_generation"] = [
        "$ python agent.py llm-generate --spec examples/url-slug.feature --llm-response-file ...", *_tail(generation, 12),
    ]
    transcripts["case_verification"] = ["$ python -c '<slugify checks>'", *_tail(verification, 3)]
    transcripts["case_spec"] = [
        line.translate(TERMINAL_REPLACEMENTS).rstrip()
        for line in case_spec.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    transcripts["case_code"] = _tail(case_output.read_text(encoding="utf-8"), 18)
    return transcripts


def build_scenes(transcripts: dict[str, object]) -> list[Scene]:
    """Keep the narration short; terminal scenes always use captured output."""
    return [
        Scene(
            title="SpecGuard",
            body="Spec-Driven Development\nwith an LLM Safety Core",
            accent="accent_red",
            narration=(
                "This is SpecGuard, a spec-driven development agent. It turns Gherkin specifications "
                "into implementation plans, guarded code generation, evaluation, and a progress dashboard."
            ),
        ),
        Scene(
            title="Why SpecGuard?",
            body="- Specs drift from code\n- LLM output can be unsafe\n- Tests need explicit traceability\n- Security checks must run before release",
            accent="accent_red",
            narration=(
                "Fast prototypes are useful, but they often drift from their requirements. An LLM can "
                "also introduce unsafe calls, missing validation, or code that no test actually covers."
            ),
        ),
        Scene(
            title="The LLM Core",
            body="Google AI Studio / Gemini\n\nRuntime key only\nFenced Python response\nAST parse\nStatic security scan\nAtomic file write",
            narration=(
                "The new core uses Gemini through Google AI Studio. The API key exists only at runtime. "
                "Before code reaches the project, SpecGuard requires fenced Python, parses it, runs a "
                "security scan, and writes the artifact atomically."
            ),
        ),
        Scene(
            title="Live Console: LLM Request",
            terminal_lines=tuple(transcripts["llm"]),
            narration=(
                "Here is the request dry run. It exposes the exact contract for Gemini without putting "
                "a key into the terminal or the repository."
            ),
        ),
        Scene(
            title="Live Console: Full Pipeline",
            terminal_lines=tuple(transcripts["pipeline"]),
            narration=(
                "This is the actual full pipeline. It creates a scaffold, scans the generated artifact, "
                "runs evaluation once, and updates the dashboard only from those exact test results."
            ),
        ),
        Scene(
            title="Live Console: Test Suite",
            terminal_lines=tuple(transcripts["tests"]),
            narration=(
                "The suite checks the task manager behavior and the agent itself: LLM response handling, "
                "security rejection, scenario mapping, parser behavior, and safe progress updates."
            ),
        ),
        Scene(
            title="What Makes It Safe",
            body="- API key never enters Git or logs\n- Generated code is never executed\n- High and critical findings block writes\n- Test failures return non-zero\n- Dashboard preserves prior state if pytest breaks",
            narration=(
                "The important thing is the boundary. A model is not trusted merely because it returned "
                "code. SpecGuard validates the artifact, blocks high severity findings, and makes failure "
                "visible to CI instead of silently showing green."
            ),
        ),
    ] + (
        [
            Scene(
                title="Case Study: URL Slug Generator",
                case_spec_lines=tuple(transcripts["case_spec"]),
                case_code_lines=tuple(transcripts["case_code"]),
                narration=(
                    "Now the real use case. This small Gherkin feature asks for a URL slug function. The "
                    "response follows an explicit public API contract, and the generated module is displayed "
                    "next to the original specification."
                ),
            ),
            Scene(
                title="Live Console: Recorded LLM Response",
                terminal_lines=tuple(transcripts["case_generation"]),
                narration=(
                    "For a repeatable video, this replayed response passes through the same parser, scanner, "
                    "and atomic-write gate as Gemini. The live Google AI Studio command is shown in the prior "
                    "dry run and uses this exact core."
                ),
            ),
            Scene(
                title="Live Console: Behavioral Verification",
                terminal_lines=tuple(transcripts["case_verification"]),
                narration=(
                    "Finally, the generated slugify function passes three behavioral checks: normalization, "
                    "separator collapsing, and validation of empty input. This is the evidence loop in action."
                ),
            ),
        ]
        if "case_spec" in transcripts
        else []
    ) + [
        Scene(
            title="SpecGuard",
            body="Gherkin -> Plan -> LLM or Scaffold\n-> Security -> Tests -> Evidence\n\nBuilt for the Kaggle AI Agents Intensive",
            accent="accent_red",
            narration=(
                "SpecGuard makes specification, generation, security, and evaluation part of one auditable "
                "loop. That is the project: not just code generation, but evidence that the generated code "
                "still deserves to move forward."
            ),
        ),
    ]


def _duration(audio_path: Path) -> float:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(audio_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(json.loads(probe.stdout)["format"]["duration"]) + 0.35


def _narrate(text: str, path: Path, voice: str) -> None:
    """Use neural Edge TTS when available; retain macOS speech as an offline fallback."""
    try:
        import edge_tts

        async def save_neural_audio() -> None:
            await edge_tts.Communicate(text, voice=voice, rate="+0%").save(str(path))

        asyncio.run(save_neural_audio())
        return
    except Exception as error:
        print(f"  [!] Neural TTS unavailable ({error}); using macOS fallback")

    aiff_path = path.with_suffix(".aiff")
    subprocess.run(["say", "-v", "Samantha", "-o", str(aiff_path), text], check=True)
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(aiff_path), "-c:a", "aac", "-b:a", "160k", str(path)],
        check=True,
        capture_output=True,
    )
    aiff_path.unlink(missing_ok=True)


def _narrate_batch(items: list[tuple[str, Path]], voice: str) -> None:
    """Synthesize all scenes concurrently so a neural voice stays fast in CI/agents."""
    try:
        import edge_tts

        async def save_all() -> None:
            await asyncio.gather(*[
                edge_tts.Communicate(text, voice=voice, rate="+0%").save(str(path))
                for text, path in items
            ])

        asyncio.run(save_all())
        return
    except Exception as error:
        print(f"  [!] Batch neural TTS unavailable ({error}); using macOS fallback")
        for text, path in items:
            _narrate(text, path, voice)


def _make_segment(image: Path, audio: Path, output: Path) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y", "-loop", "1", "-i", str(image), "-i", str(audio),
            "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "160k",
            "-pix_fmt", "yuv420p", "-r", "30", "-t", str(_duration(audio)), "-shortest", str(output),
        ],
        check=True,
        capture_output=True,
    )


def generate_video(workdir: Path, output: Path, voice: str, *, include_case: bool) -> None:
    """Capture console output, render scenes, narrate, and concatenate the video."""
    workdir.mkdir(parents=True, exist_ok=True)
    transcripts = capture_console_transcripts(workdir, include_case=include_case)
    scenes = build_scenes(transcripts)
    segments = []
    assets: list[tuple[Scene, Path, Path, Path]] = []

    for index, scene in enumerate(scenes):
        image = workdir / f"scene_{index:02d}.png"
        audio = workdir / f"scene_{index:02d}.m4a"
        segment = workdir / f"scene_{index:02d}.mp4"
        if scene.case_spec_lines:
            make_case_study_frame(
                scene.title,
                list(scene.case_spec_lines),
                list(scene.case_code_lines),
                str(image),
            )
        elif scene.terminal_lines:
            make_terminal_frame(scene.title, list(scene.terminal_lines), str(image))
        else:
            make_slide(
                {"title": scene.title, "body": scene.body, "accent": scene.accent},
                str(image),
            )
        assets.append((scene, image, audio, segment))

    _narrate_batch([(scene.narration, audio) for scene, _, audio, _ in assets], voice)

    for _, image, audio, segment in assets:
        _make_segment(image, audio, segment)
        segments.append(segment)

    concat = workdir / "concat.txt"
    concat.write_text("".join(f"file '{segment}'\n" for segment in segments), encoding="utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(output)],
        check=True,
        capture_output=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a SpecGuard LLM demo video")
    parser.add_argument("--workdir", type=Path, default=DEFAULT_WORKDIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--voice", default="en-US-AvaMultilingualNeural", help="Edge Neural TTS voice")
    parser.add_argument("--without-case", action="store_true", help="Skip the recorded URL-slug case study")
    args = parser.parse_args()

    generate_video(args.workdir, args.output, args.voice, include_case=not args.without_case)
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", str(args.output)],
        capture_output=True,
        text=True,
        check=True,
    )
    info = json.loads(probe.stdout)["format"]
    print(f"Video: {args.output}")
    print(f"Duration: {float(info['duration']):.1f}s")
    print(f"Size: {int(info['size']) / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
