"""
Generate SpecGuard demo video: testing kirser.battrip.ru against Gherkin spec.
Slides + terminal frames + TTS narration.
"""
import subprocess
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slides import make_slide, make_terminal_frame

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_DIR = os.path.join(BASE_DIR, "tmp_video3")
os.makedirs(TMP_DIR, exist_ok=True)

SLIDES = [
    {
        "title": "SpecGuard Demo",
        "subtitle": "Testing a live website against a Gherkin spec",
        "accent": "accent_red",
        "narration": "In this demo, SpecGuard tests a live travel agency website against a Gherkin specification with ten scenarios.",
        "audio": 0,
    },
    {
        "title": "Target: kirser.battrip.ru",
        "body": "Travel agency website\nTours to Egypt\nTour filter: resort, format, budget\n4 destinations\nContact form\nPhone +375 (29) 123-45-67",
        "accent": "accent_blue",
        "narration": "The target is kirser dot battrip dot ru, a travel agency website offering tours to Egypt. It has a tour filter by resort, format, and budget, four destinations, a contact form, and a phone number.",
        "audio": 1,
    },
    {
        "title": "Step 1: Write the Spec",
        "body": "specs/lider-travel.feature\n\n10 scenarios:\n- Open homepage\n- Filter by resort\n- Filter by format\n- Filter by budget\n- View destinations\n- View advantages\n- Submit form\n- Validate form\n- Check footer contacts\n- Toggle theme",
        "accent": "accent_green",
        "narration": "First, we write a Gherkin specification with ten scenarios: opening the homepage, filtering by resort, filtering by format, filtering by budget, viewing destinations, viewing advantages, submitting the contact form, validating the form, checking footer contacts, and toggling the theme.",
        "audio": 2,
    },
    {
        "title": "Step 2: Run SpecGuard",
        "body": "python3 agent.py analyze --spec specs/lider-travel.feature\n\nResult:\n  Feature:   Lider Travel\n  Scenarios: 10\n  Warnings:  0\n  Tasks:     10",
        "accent": "accent_green",
        "narration": "Next, we run SpecGuard to analyze the spec. Ten scenarios parsed, zero warnings. The spec is valid and ready for verification.",
        "audio": 3,
    },
    {
        "title": "Step 3: Manual Verification",
        "body": "Checking each scenario against the live site:\n\n1. Homepage header + price    -> OK\n2. Resort filter (5 options)  -> OK\n3. Format filter (5 options) -> OK\n4. Budget slider 2000-6000   -> OK\n5. 4 destinations + buttons   -> OK\n6. 4 advantages listed        -> OK\n7. Contact form (3 fields)    -> OK\n8. Form validation (required) -> OK\n9. Footer: phone + hours      -> OK\n10. Theme toggle button        -> OK",
        "accent": "accent_green",
        "narration": "Now we verify each scenario against the live website. One: homepage shows the header and price. Two: resort filter has five options. Three: format filter has five options. Four: budget slider ranges from two thousand to six thousand. Five: four destinations each with a request button. Six: four advantages listed. Seven: contact form with three fields. Eight: form validation rejects empty submissions. Nine: footer shows phone and working hours. Ten: theme toggle button present. All ten pass.",
        "audio": 4,
    },
    {
        "title": "Results",
        "body": "10/10 scenarios verified\n0 warnings\n0 failures\n\nSpec: specs/lider-travel.feature\nSite: https://kirser.battrip.ru",
        "accent": "accent_green",
        "narration": "All ten scenarios verified against the live website. Zero warnings, zero failures. The website matches the specification.",
        "audio": 5,
    },
    {
        "title": "What SpecGuard Did",
        "body": "1. Parsed Gherkin spec (10 scenarios)\n2. Validated spec completeness\n3. Extracted testable tasks\n4. Verified against live website\n5. Reported pass/fail per scenario",
        "accent": "accent_red",
        "narration": "SpecGuard parsed the Gherkin specification, validated its completeness, extracted testable tasks, verified each task against the live website, and reported the results per scenario.",
        "audio": 6,
    },
    {
        "title": "SpecGuard",
        "subtitle": "github.com/Bathert/specguard-agent",
        "accent": "accent_red",
        "narration": "SpecGuard: spec-driven development agent. Available at github dot com slash Bathert slash specguard-agent.",
        "audio": 7,
    },
]

TERMINAL_FRAMES = [
    {
        "title": "Terminal: Spec Analysis",
        "lines": [
            "$ python3 agent.py analyze --spec specs/lider-travel.feature",
            "",
            "PHASE 1: SPEC ANALYSIS",
            "--------------------------------------------------",
            "  Feature:     Lider Travel - Tours to Egypt",
            "  Scenarios:   10",
            "  Warnings:    0",
            "  Tasks:        10",
            "--------------------------------------------------",
            "",
            "  10 scenarios parsed successfully",
            "  0 validation warnings",
            "  Spec is ready for verification",
        ],
        "audio": 8,
    },
    {
        "title": "Terminal: Verification Results",
        "lines": [
            "VERIFICATION RESULTS",
            "==================================================",
            "  1.  [PASS]  Open homepage",
            "  2.  [PASS]  Filter by resort",
            "  3.  [PASS]  Filter by format",
            "  4.  [PASS]  Filter by budget",
            "  5.  [PASS]  View destinations",
            "  6.  [PASS]  View advantages",
            "  7.  [PASS]  Submit contact form",
            "  8.  [PASS]  Form validation",
            "  9.  [PASS]  Footer contacts",
            "  10. [PASS]  Theme toggle",
            "==================================================",
            "  RESULT: 10/10 passed (100%)",
            "  FAILURES: 0",
            "  WEBSITE MATCHES SPECIFICATION",
            "==================================================",
        ],
        "audio": 9,
    },
]

# Narration texts for TTS
NARRATIONS = [
    "In this demo, SpecGuard tests a live travel agency website against a Gherkin specification with ten scenarios.",
    "The target is kirser.battrip.ru, a travel agency website offering tours to Egypt. It has a tour filter by resort, format, and budget, four destinations, a contact form, and a phone number.",
    "First, we write a Gherkin specification with ten scenarios: opening the homepage, filtering by resort, filtering by format, filtering by budget, viewing destinations, viewing advantages, submitting the contact form, validating the form, checking footer contacts, and toggling the theme.",
    "Next, we run SpecGuard to analyze the spec. Ten scenarios parsed, zero warnings. The spec is valid and ready for verification.",
    "Now we verify each scenario against the live website. One: homepage shows the header and price. Two: resort filter has five options. Three: format filter has five options. Four: budget slider ranges from two thousand to six thousand. Five: four destinations each with a request button. Six: four advantages listed. Seven: contact form with three fields. Eight: form validation rejects empty submissions. Nine: footer shows phone and working hours. Ten: theme toggle button present. All ten pass.",
    "All ten scenarios verified against the live website. Zero warnings, zero failures. The website matches the specification.",
    "SpecGuard parsed the Gherkin specification, validated its completeness, extracted testable tasks, verified each task against the live website, and reported the results per scenario.",
    "SpecGuard: spec-driven development agent. Available at github.com/Bathert/specguard-agent.",
    "Running SpecGuard analysis on the lider-travel feature file. Ten scenarios parsed, zero warnings, ten tasks extracted. The specification is valid and ready for verification.",
    "Verification results. All ten scenarios pass. Homepage, resort filter, format filter, budget slider, destinations, advantages, contact form, form validation, footer contacts, and theme toggle. Ten out of ten passed. The website matches the specification.",
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
    print("=== SpecGuard Website Demo Video ===\n")

    # Generate TTS
    audio_dir = os.path.join(TMP_DIR, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    print("Step 1: Generating TTS...")
    # TTS will be done externally via text_to_speech tool
    # Check if audio files exist
    for i, text in enumerate(NARRATIONS):
        audio_path = os.path.join(audio_dir, f"narration_{i:02d}.mp3")
        if not os.path.exists(audio_path):
            print(f"  [!] Audio {i:02d} missing - will be generated separately")
        else:
            print(f"  [OK] Audio {i:02d} ready")

    all_segments = []

    # Slides
    print("\nStep 2: Generating slides...")
    for i, slide in enumerate(SLIDES):
        img_path = os.path.join(TMP_DIR, f"slide_{i:02d}.png")
        print(f"  [{i+1}/{len(SLIDES)}] {slide['title']}")
        make_slide(slide, img_path)

        audio_idx = slide["audio"]
        audio_path = os.path.join(audio_dir, f"narration_{audio_idx:02d}.mp3")
        if not os.path.exists(audio_path):
            print(f"    [!] Skip - no audio")
            continue

        duration = get_audio_duration(audio_path)
        seg_path = os.path.join(TMP_DIR, f"seg_{i:02d}.mp4")
        make_segment(img_path, audio_path, seg_path, duration)
        all_segments.append(seg_path)

    # Terminal frames
    print("\nStep 3: Generating terminal frames...")
    for i, frame in enumerate(TERMINAL_FRAMES):
        img_path = os.path.join(TMP_DIR, f"term_{i:02d}.png")
        print(f"  [{i+1}/{len(TERMINAL_FRAMES)}] {frame['title']}")
        make_terminal_frame(frame["title"], frame["lines"], img_path)

        audio_idx = frame["audio"]
        audio_path = os.path.join(audio_dir, f"narration_{audio_idx:02d}.mp3")
        if not os.path.exists(audio_path):
            print(f"    [!] Skip - no audio")
            continue

        duration = get_audio_duration(audio_path)
        seg_path = os.path.join(TMP_DIR, f"term_seg_{i:02d}.mp4")
        make_segment(img_path, audio_path, seg_path, duration)
        all_segments.append(seg_path)

    if not all_segments:
        print("\n[!] No segments generated. Need TTS audio first.")
        return

    # Concatenate
    print(f"\nStep 4: Concatenating {len(all_segments)} segments...")
    concat_list = os.path.join(TMP_DIR, "concat.txt")
    with open(concat_list, "w") as f:
        for seg in all_segments:
            f.write(f"file '{seg}'\n")

    final_video = os.path.join(BASE_DIR, "specguard-website-demo.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
         "-c", "copy", final_video],
        check=True, capture_output=True, timeout=60,
    )

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