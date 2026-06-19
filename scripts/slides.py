"""
Slide generator using PIL/Pillow — creates 1920x1080 PNG slides.
"""
from PIL import Image, ImageDraw, ImageFont
import os

WIDTH, HEIGHT = 1920, 1080

# Font paths (macOS system fonts)
FONT_BOLD = "/System/Library/Fonts/Helvetica.ttc"
FONT_MONO = "/System/Library/Fonts/Menlo.ttf"


def get_font(size, bold=False, mono=False):
    try:
        path = FONT_MONO if mono else FONT_BOLD
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def make_slide(slide: dict, output_path: str):
    bg_color = slide.get("bg", "0f0f23")
    fg_color = slide.get("fg", "e94560")
    title = slide.get("title", "")
    subtitle = slide.get("subtitle", "")
    body = slide.get("body", "")

    # Create image
    img = Image.new("RGB", (WIDTH, HEIGHT), color=f"#{bg_color}")
    draw = ImageDraw.Draw(img)

    # Title
    font_title = get_font(72, bold=True)
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) / 2, 150), title, fill=f"#{fg_color}", font=font_title)

    # Subtitle
    if subtitle:
        font_sub = get_font(42)
        bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
        sw = bbox[2] - bbox[0]
        draw.text(((WIDTH - sw) / 2, 250), subtitle, fill="#cccccc", font=font_sub)

    # Body
    if body:
        font_body = get_font(36, mono=True)
        lines = body.split("\n")
        y = 380
        for line in lines:
            draw.text((200, y), line, fill="#ffffff", font=font_body)
            y += 50

    img.save(output_path, "PNG")
    print(f"  Saved: {output_path}")


def make_terminal_frame(title: str, lines: list, output_path: str):
    """Create a frame that looks like terminal output."""
    img = Image.new("RGB", (WIDTH, HEIGHT), color="#0c0c0c")
    draw = ImageDraw.Draw(img)
    font = get_font(24, mono=True)
    font_title = get_font(28, bold=True)

    # Title bar
    draw.text((60, 30), title, fill="#e94560", font=font_title)
    draw.line([(60, 70), (WIDTH - 60, 70)], fill="#333333", width=2)

    y = 90
    for line in lines:
        # Color coding
        if "PASSED" in line or "PASS" in line or "passed" in line:
            color = "#00d4aa"
        elif "FAIL" in line or "fail" in line.lower():
            color = "#e94560"
        elif "╔" in line or "║" in line or "╚" in line or "╠" in line or "═" in line:
            color = "#e94560"
        elif "━" in line:
            color = "#e94560"
        elif "PHASE" in line:
            color = "#e94560"
        elif "SUMMARY" in line:
            color = "#00d4aa"
        else:
            color = "#cccccc"
        draw.text((60, y), line, fill=color, font=font)
        y += 32
        if y > HEIGHT - 50:
            break

    img.save(output_path, "PNG")
    print(f"  Saved: {output_path}")


if __name__ == "__main__":
    # Test
    os.makedirs("/tmp/slides", exist_ok=True)
    make_slide({
        "title": "SpecGuard",
        "subtitle": "Spec-Driven Development Agent",
        "bg": "1a1a2e",
        "fg": "e94560",
    }, "/tmp/slides/test.png")
    print("OK")