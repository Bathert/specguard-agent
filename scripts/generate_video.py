"""
Generate video for Kaggle capstone: SpecGuard agent walkthrough.
Creates a slide-based video with English TTS narration + terminal demo.
Output: specguard-demo.mp4
"""
import subprocess
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slides import make_slide, make_terminal_frame

OUTPUT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_DIR = os.path.join(OUTPUT_DIR, "tmp_video")
os.makedirs(TMP_DIR, exist_ok=True)

# ── Slide definitions ──
SLIDES = [
    {
        "title": "SpecGuard",
        "subtitle": "Spec-Driven Development Agent",
        "narration": "SpecGuard is a spec-driven development agent that transforms Gherkin specifications into production-ready code through a disciplined pipeline.",
        "duration": 8,
        "bg": "1a1a2e",
        "fg": "e94560",
    },
    {
        "title": "The Problem",
        "body": "- Vibe-coded prototypes rot fast\n- Hallucinated packages\n- Missing input validation\n- Untraceable logic\n- Zero guardrails",
        "narration": "Vibe coding lets you generate prototypes in seconds. But those prototypes rot fast. Hallucinated packages that don't exist. Missing input validation. Untraceable logic. Zero guardrails.",
        "duration": 12,
        "bg": "0f0f23",
        "fg": "e94560",
    },
    {
        "title": "The Solution",
        "body": "- Gherkin spec = source of truth\n- Code is disposable\n- Automated pipeline\n- Continuous security\n- Progress tracking",
        "narration": "Spec-Driven Development solves this by inverting the relationship. The Gherkin spec is permanent. The code is disposable. SpecGuard automates the full cycle with continuous security scanning and progress tracking.",
        "duration": 12,
        "bg": "0f0f23",
        "fg": "00d4aa",
    },
    {
        "title": "Pipeline",
        "body": "SPEC (.feature)\n  --> spec-analyzer --> PLAN\n  --> code-generator --> CODE\n  --> security-scanner --> AUDIT\n  --> progress-tracker --> DASHBOARD",
        "narration": "The pipeline has four phases. Spec analyzer parses Gherkin and validates completeness. Code generator produces implementation. Security scanner runs a seven-pillar audit. Progress tracker maintains coverage metrics across sessions.",
        "duration": 14,
        "bg": "0f0f23",
        "fg": "e94560",
    },
    {
        "title": "5-Day Course Mapping",
        "body": "Day 1: Vibe Coding (Gherkin to code)\nDay 2: Tools (modular skills)\nDay 3: Skills and Memory (SKILL.md + JSON)\nDay 4: Security and Evaluation (7 pillars)\nDay 5: Spec-Driven Production (SDD)",
        "narration": "SpecGuard maps to all five days of the course. Day one: vibe coding with natural language specs. Day two: modular tools and interoperability. Day three: agent skills with progressive disclosure and long-term memory. Day four: seven-pillar security architecture and automated evaluation. Day five: spec-driven production development.",
        "duration": 18,
        "bg": "0f0f23",
        "fg": "00d4aa",
    },
    {
        "title": "Demo: Task Manager API",
        "body": "9 Gherkin scenarios\n16 automated tests\n100% spec coverage\n0 security issues",
        "narration": "Let me show you the agent in action. We have a Task Manager A P I with nine Gherkin scenarios. The agent parses the spec, runs the security scan, executes sixteen automated tests, and tracks progress.",
        "duration": 12,
        "bg": "0f0f23",
        "fg": "e94560",
    },
    {
        "title": "Run: python3 agent.py",
        "body": "Full pipeline execution\n\nSee terminal output in next frames",
        "narration": "Running the agent with python3 agent.py executes the full pipeline. Let's see the output.",
        "duration": 6,
        "bg": "0f0f23",
        "fg": "00d4aa",
    },
    {
        "title": "Results",
        "body": "Phase 1: 9 scenarios, 0 warnings\nPhase 3: 0 critical, 0 high, 0 injections\nPhase 4: 16/16 tests passed\nPhase 5: 100% coverage, 0 regressions\n\nVerdict: Ready for deployment",
        "narration": "The results. Nine scenarios parsed with zero warnings. Security scan found zero critical issues, zero high issues, zero injections. All sixteen tests passed. One hundred percent spec coverage with zero regressions. The agent reports: ready for deployment.",
        "duration": 16,
        "bg": "0f0f23",
        "fg": "00d4aa",
    },
    {
        "title": "Security Scanner",
        "body": "7 Pillars:\n1. Package verification (anti-slopsquatting)\n2. Secret detection\n3. Injection audit\n4. Input validation\n5. Output sanitization\n6. Spec traceability\n7. Continuous evaluation",
        "narration": "The security scanner implements seven pillars. Package verification checks every import against real registries to prevent slopsquatting. Secret detection scans for hardcoded credentials. Injection audit finds unsanitized input. Input validation flags functions without guards. Spec traceability ensures every function traces to a scenario. And continuous evaluation runs tests after every change.",
        "duration": 18,
        "bg": "0f0f23",
        "fg": "e94560",
    },
    {
        "title": "Code and Writeup",
        "body": "github.com/Bathert/specguard-agent\n\n11 files, ~2000 lines of code\nReal implementations, not stubs",
        "narration": "The full code is available at github dot com slash Bathert slash specguard-agent. Eleven files, approximately two thousand lines of real working code. Not stubs, not documentation only. Real implementations that you can run.",
        "duration": 10,
        "bg": "0f0f23",
        "fg": "00d4aa",
    },
    {
        "title": "Thank You",
        "subtitle": "Built for Kaggle 5-Day AI Agents Intensive",
        "narration": "Thank you for watching. SpecGuard: spec-driven development agent, built for the Kaggle five-day A I Agents intensive course.",
        "duration": 6,
        "bg": "1a1a2e",
        "fg": "e94560",
    },
]

# Terminal demo frames (real output from agent.py)
TERMINAL_FRAMES = [
    {
        "title": "Terminal: python3 agent.py --no-packages",
        "lines": [
            "==================================================",
            "  PROGRESS DASHBOARD -- Task Manager API",
            "==================================================",
            "  SCENARIOS:     9 total",
            "  IMPLEMENTED:   9 (100.0%)",
            "  TESTED:        9 (100.0%)",
            "  REGRESSIONS:   0",
            "  TESTS:         16/16 passed",
            "==================================================",
            "  SCENARIO STATUS:",
            "    [PASS] Create a new task",
            "    [PASS] Assign a task to a user",
            "    [PASS] Complete a task",
            "    [PASS] List tasks by status",
            "    [PASS] Prevent duplicate task titles",
            "    [PASS] Validate task priority",
            "    [PASS] Search tasks by keyword",
            "    [PASS] Delete a task",
            "    [PASS] Cannot assign a completed task",
            "==================================================",
            "  NEXT: All scenarios tested. Ready for deployment.",
            "==================================================",
        ],
        "narration": "Here is the real terminal output from running the agent. Nine scenarios, all passing. Sixteen tests, all green. One hundred percent coverage. Zero regressions. Ready for deployment.",
        "duration": 16,
    },
    {
        "title": "Terminal: pytest results",
        "lines": [
            "============================== test session starts ==============================",
            "platform darwin -- Python 3.9.6, pytest-8.4.2",
            "",
            "evals/test_task_manager.py::test_create_new_task PASSED",
            "evals/test_task_manager.py::test_assign_task PASSED",
            "evals/test_task_manager.py::test_complete_task PASSED",
            "evals/test_task_manager.py::test_list_tasks_by_status PASSED",
            "evals/test_task_manager.py::test_prevent_duplicate PASSED",
            "evals/test_task_manager.py::test_validate_priority[urgent] PASSED",
            "evals/test_task_manager.py::test_validate_priority[critical] PASSED",
            "evals/test_task_manager.py::test_validate_priority[unknown] PASSED",
            "evals/test_task_manager.py::test_search_tasks PASSED",
            "evals/test_task_manager.py::test_delete_task PASSED",
            "evals/test_task_manager.py::test_cannot_assign_completed PASSED",
            "evals/test_task_manager.py::test_empty_title_rejected PASSED",
            "evals/test_task_manager.py::test_whitespace_title_rejected PASSED",
            "evals/test_task_manager.py::test_empty_assignee_rejected PASSED",
            "evals/test_task_manager.py::test_delete_nonexistent_task PASSED",
            "evals/test_task_manager.py::test_invalid_status_filter PASSED",
            "",
            "============================== 16 passed in 0.01s ==============================",
        ],
        "narration": "All sixteen tests pass. Each test maps to a Gherkin scenario. The evaluation is continuous: tests run after every change, and regressions are flagged immediately.",
        "duration": 14,
    },
    {
        "title": "Terminal: security scan",
        "lines": [
            "PHASE 3: SECURITY SCAN",
            "--------------------------------------------------",
            "  Verdict:         pass_with_warnings",
            "  Files scanned:   4",
            "  Critical:        0",
            "  High:            0",
            "  Medium:          6",
            "  Low:             13",
            "  Secrets:         0",
            "  Injections:      0",
            "  Validation gaps: 6",
            "  Traceability:    13",
            "--------------------------------------------------",
            "",
            "  0 secrets found",
            "  0 injection vectors found",
            "  0 critical issues",
            "  0 high issues",
            "  Verdict: pass_with_warnings",
        ],
        "narration": "The security scan found zero secrets, zero injection vectors, zero critical issues. The verdict is pass with warnings: six medium input validation gaps and thirteen low traceability gaps. No blocking issues.",
        "duration": 14,
    },
]


def generate_tts(text: str, output_path: str) -> bool:
    """Generate TTS audio using macOS `say` command."""
    try:
        aiff_path = output_path.replace(".mp3", ".aiff")
        subprocess.run(
            ["say", "-v", "Samantha", "-r", "175", "-o", aiff_path, text],
            check=True, timeout=30,
        )
        subprocess.run(
            ["ffmpeg", "-y", "-i", aiff_path,
             "-codec:a", "libmp3lame", "-qscale:a", "4", output_path],
            check=True, capture_output=True, timeout=15,
        )
        os.remove(aiff_path)
        return True
    except Exception as e:
        print(f"  TTS error: {e}")
        return False


def get_audio_duration(path: str) -> float:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", path],
        capture_output=True, text=True, timeout=5,
    )
    try:
        return float(json.loads(probe.stdout)["format"]["duration"]) + 0.5
    except Exception:
        return 5.0


def make_segment(img_path, audio_path, output_path, duration):
    """Create a video segment from image + audio."""
    subprocess.run(
        ["ffmpeg", "-y",
         "-loop", "1", "-i", img_path,
         "-i", audio_path,
         "-c:v", "libx264", "-tune", "stillimage",
         "-c:a", "aac", "-b:a", "128k",
         "-pix_fmt", "yuv420p",
         "-t", str(duration),
         "-shortest",
         output_path],
        check=True, capture_output=True, timeout=30,
    )


def main():
    print("=== SpecGuard Video Generator ===\n")

    all_segments = []

    # Process regular slides
    print("Step 1: Generating slide images + TTS...")
    for i, slide in enumerate(SLIDES):
        print(f"  Slide {i+1}/{len(SLIDES)}: {slide['title'][:40]}...")

        # Image
        img_path = os.path.join(TMP_DIR, f"slide_{i:02d}.png")
        make_slide(slide, img_path)

        # TTS
        audio_path = os.path.join(TMP_DIR, f"narration_{i:02d}.mp3")
        if not generate_tts(slide["narration"], audio_path):
            subprocess.run(
                ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                 "-t", str(slide["duration"]), audio_path],
                check=True, capture_output=True, timeout=10,
            )

        duration = get_audio_duration(audio_path)

        # Segment
        seg_path = os.path.join(TMP_DIR, f"seg_{i:02d}.mp4")
        make_segment(img_path, audio_path, seg_path, duration)
        all_segments.append(seg_path)

    # Process terminal frames
    print("\nStep 2: Generating terminal demo frames + TTS...")
    for i, frame in enumerate(TERMINAL_FRAMES):
        print(f"  Terminal {i+1}/{len(TERMINAL_FRAMES)}: {frame['title'][:40]}...")

        img_path = os.path.join(TMP_DIR, f"term_{i:02d}.png")
        make_terminal_frame(frame["title"], frame["lines"], img_path)

        audio_path = os.path.join(TMP_DIR, f"term_audio_{i:02d}.mp3")
        if not generate_tts(frame["narration"], audio_path):
            subprocess.run(
                ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                 "-t", str(frame["duration"]), audio_path],
                check=True, capture_output=True, timeout=10,
            )

        duration = get_audio_duration(audio_path)

        seg_path = os.path.join(TMP_DIR, f"term_seg_{i:02d}.mp4")
        make_segment(img_path, audio_path, seg_path, duration)
        all_segments.append(seg_path)

    # Concatenate
    print(f"\nStep 3: Concatenating {len(all_segments)} segments...")
    concat_list = os.path.join(TMP_DIR, "concat.txt")
    with open(concat_list, "w") as f:
        for seg in all_segments:
            f.write(f"file '{seg}'\n")

    final_video = os.path.join(OUTPUT_DIR, "specguard-demo.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
         "-c", "copy", final_video],
        check=True, capture_output=True, timeout=60,
    )

    # Info
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", final_video],
        capture_output=True, text=True, timeout=5,
    )
    final_duration = float(json.loads(probe.stdout)["format"]["duration"])
    size_mb = os.path.getsize(final_video) / 1024 / 1024

    print(f"\n=== Done! ===")
    print(f"Video: {final_video}")
    print(f"Duration: {final_duration:.1f}s ({final_duration/60:.1f} min)")
    print(f"Size: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()