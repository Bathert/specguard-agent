"""
Assemble website demo video from real screenshots + TTS audio.
"""
import subprocess
import os
import json
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAMES_DIR = os.path.join(BASE_DIR, "tmp_video3", "site_frames")
AUDIO_DIR = os.path.join(BASE_DIR, "tmp_video3", "audio")
TMP_DIR = os.path.join(BASE_DIR, "tmp_video3", "video_segs")
os.makedirs(TMP_DIR, exist_ok=True)

# (screenshot_filename, audio_filename, narration_label)
SEGMENTS = [
    ("frame_01_home.png",        "site_00.mp3", "Homepage hero"),
    ("frame_02_sharm.png",        "site_01.mp3", "Filter: Sharm"),
    ("frame_03_family.png",       "site_02.mp3", "Filter: Family"),
    ("frame_04_destinations.png", "site_03.mp3", "Destinations"),
    ("frame_05_advantages.png",   "site_04.mp3", "Advantages"),
    ("frame_06_form.png",         "site_05.mp3", "Contact form"),
    ("frame_07_form_filled.png",  "site_06.mp3", "Form filled"),
    ("frame_08_footer.png",       "site_07.mp3", "Footer contacts"),
    ("frame_09_theme_toggle.png", "site_08.mp3", "Theme toggle"),
]


def get_audio_duration(path):
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
         "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black",
         output_path],
        check=True, capture_output=True, timeout=30,
    )


def main():
    print("=== Assembling Website Demo Video ===\n")

    all_segments = []
    for i, (img_name, audio_name, label) in enumerate(SEGMENTS):
        img_path = os.path.join(FRAMES_DIR, img_name)
        audio_path = os.path.join(AUDIO_DIR, audio_name)

        if not os.path.exists(img_path):
            print(f"  [!] Missing screenshot: {img_path}")
            continue
        if not os.path.exists(audio_path):
            print(f"  [!] Missing audio: {audio_path}")
            continue

        duration = get_audio_duration(audio_path)
        seg_path = os.path.join(TMP_DIR, f"seg_{i:02d}.mp4")
        print(f"  [{i+1}/{len(SEGMENTS)}] {label} ({duration:.1f}s)")
        make_segment(img_path, audio_path, seg_path, duration)
        all_segments.append(seg_path)

    if not all_segments:
        print("\n[!] No segments to concatenate")
        return

    # Concatenate
    print(f"\nConcatenating {len(all_segments)} segments...")
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