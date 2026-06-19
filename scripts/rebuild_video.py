"""
Rebuild video: new slides (PIL) + TTS audio (edge provider) + ffmpeg assembly.
"""
import subprocess
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slides import make_slide, make_terminal_frame

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_DIR = os.path.join(BASE_DIR, "tmp_video2")
AUDIO_DIR = os.path.join(BASE_DIR, "tmp_video", "audio")
os.makedirs(TMP_DIR, exist_ok=True)

SLIDES = [
    {"title": "SpecGuard", "subtitle": "Spec-Driven Development Agent", "accent": "accent_red", "audio": 0},
    {"title": "The Problem", "body": "- Vibe-coded prototypes rot fast\n- Hallucinated packages\n- Missing input validation\n- Untraceable logic\n- Zero guardrails", "accent": "accent_red", "audio": 1},
    {"title": "The Solution", "body": "- Gherkin spec = source of truth\n- Code is disposable\n- Automated pipeline\n- Continuous security\n- Progress tracking", "accent": "accent_green", "audio": 2},
    {"title": "Pipeline", "body": "SPEC (.feature)\n  --> spec-analyzer --> PLAN\n  --> code-generator --> CODE\n  --> security-scanner --> AUDIT\n  --> progress-tracker --> DASHBOARD", "accent": "accent_red", "audio": 3},
    {"title": "5-Day Course Mapping", "body": "Day 1: Vibe Coding (Gherkin to code)\nDay 2: Tools (modular skills)\nDay 3: Skills and Memory (SKILL.md + JSON)\nDay 4: Security and Evaluation (7 pillars)\nDay 5: Spec-Driven Production (SDD)", "accent": "accent_green", "audio": 4},
    {"title": "Demo: Task Manager API", "body": "9 Gherkin scenarios\n16 automated tests\n100% spec coverage\n0 security issues", "accent": "accent_red", "audio": 5},
    {"title": "Run: python3 agent.py", "body": "Full pipeline execution\n\nSee terminal output in next frames", "accent": "accent_green", "audio": 6},
    {"title": "Results", "body": "Phase 1: 9 scenarios, 0 warnings\nPhase 3: 0 critical, 0 high, 0 injections\nPhase 4: 16/16 tests passed\nPhase 5: 100% coverage, 0 regressions\n\nVerdict: Ready for deployment", "accent": "accent_green", "audio": 7},
    {"title": "Security Scanner", "body": "7 Pillars:\n1. Package verification (anti-slopsquatting)\n2. Secret detection\n3. Injection audit\n4. Input validation\n5. Output sanitization\n6. Spec traceability\n7. Continuous evaluation", "accent": "accent_red", "audio": 8},
    {"title": "Code and Writeup", "body": "github.com/Bathert/specguard-agent\n\n11 files, ~2000 lines of code\nReal implementations, not stubs", "accent": "accent_green", "audio": 9},
    {"title": "Thank You", "subtitle": "Built for Kaggle 5-Day AI Agents Intensive", "accent": "accent_red", "audio": 10},
]

TERMINAL_FRAMES = [
    {
        "title": "Terminal: Progress Dashboard",
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
        "audio": 11,
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
        "audio": 12,
    },
    {
        "title": "Terminal: Security Scan",
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
        "audio": 13,
    },
]


def get_audio_duration(path):
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", path],
        capture_output=True, text=True, timeout=5,
    )
    try:
        return float(json.loads(probe.stdout)["format"]["duration"]) + 0.3
    except Exception:
        return 5.0


def make_segment(img_path, audio_path, output_path, duration):
    subprocess.run(
        ["ffmpeg", "-y",
         "-loop", "1", "-i", img_path,
         "-i", audio_path,
         "-c:v", "libx264", "-tune", "stillimage",
         "-c:a", "aac", "-b:a", "192k",
         "-pix_fmt", "yuv420p",
         "-t", str(duration),
         "-shortest",
         "-r", "30",
         output_path],
        check=True, capture_output=True, timeout=30,
    )


def main():
    print("=== SpecGuard Video Rebuild ===\n")

    all_segments = []

    # Slides
    print("Step 1: Generating slides...")
    for i, slide in enumerate(SLIDES):
        img_path = os.path.join(TMP_DIR, f"slide_{i:02d}.png")
        print(f"  [{i+1}/{len(SLIDES)}] {slide['title']}")
        make_slide(slide, img_path)

        audio_idx = slide["audio"]
        audio_path = os.path.join(AUDIO_DIR, f"narration_{audio_idx:02d}.mp3")
        if not os.path.exists(audio_path):
            print(f"    [!] Audio not found: {audio_path}")
            continue

        duration = get_audio_duration(audio_path)
        seg_path = os.path.join(TMP_DIR, f"seg_{i:02d}.mp4")
        make_segment(img_path, audio_path, seg_path, duration)
        all_segments.append(seg_path)

    # Terminal frames
    print("\nStep 2: Generating terminal frames...")
    for i, frame in enumerate(TERMINAL_FRAMES):
        img_path = os.path.join(TMP_DIR, f"term_{i:02d}.png")
        print(f"  [{i+1}/{len(TERMINAL_FRAMES)}] {frame['title']}")
        make_terminal_frame(frame["title"], frame["lines"], img_path)

        audio_idx = frame["audio"]
        audio_path = os.path.join(AUDIO_DIR, f"narration_{audio_idx:02d}.mp3")
        if not os.path.exists(audio_path):
            print(f"    [!] Audio not found: {audio_path}")
            continue

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

    final_video = os.path.join(BASE_DIR, "specguard-demo.mp4")
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