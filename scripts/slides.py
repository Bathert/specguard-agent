"""
Slide generator using PIL/Pillow — creates 1920x1080 PNG slides.
Professional dark theme with clean typography.
"""
from PIL import Image, ImageDraw, ImageFont
import os

WIDTH, HEIGHT = 1920, 1080

# Font paths (macOS system fonts)
FONT_BOLD = "/System/Library/Fonts/Helvetica.ttc"
FONT_REG = "/System/Library/Fonts/Helvetica.ttc"
FONT_MONO = "/System/Library/Fonts/Menlo.ttf"
FONT_LIGHT = "/System/Library/Fonts/Helvetica.ttc"

# Color palette
COLORS = {
    "bg_dark": (15, 15, 30),       # #0f0f1e
    "bg_card": (22, 22, 40),       # #161628
    "accent_red": (233, 69, 96),   # #e94560
    "accent_green": (0, 212, 170), # #00d4aa
    "accent_blue": (100, 149, 237),# #6495ed
    "text_white": (240, 240, 245), # #f0f0f5
    "text_gray": (160, 160, 180),  # #a0a0b4
    "text_dim": (100, 100, 120),   # #646478
    "border": (40, 40, 60),        # #28283c
}

# Font indices in Helvetica.ttc: 0=Regular, 1=Bold, 2=Light
def get_font(size, weight="regular", mono=False):
    try:
        if mono:
            return ImageFont.truetype(FONT_MONO, size)
        if weight == "bold":
            return ImageFont.truetype(FONT_BOLD, size, index=1)
        if weight == "light":
            return ImageFont.truetype(FONT_LIGHT, size, index=2)
        return ImageFont.truetype(FONT_REG, size, index=0)
    except Exception:
        try:
            return ImageFont.truetype(FONT_BOLD, size)
        except:
            return ImageFont.load_default()


def _draw_rounded_rect(draw, xy, radius, fill):
    """Draw a rounded rectangle."""
    x0, y0, x1, y1 = xy
    r = radius
    # Main rect
    draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
    # Corners
    draw.pieslice([x0, y0, x0 + 2*r, y0 + 2*r], 180, 270, fill=fill)
    draw.pieslice([x1 - 2*r, y0, x1, y0 + 2*r], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2*r, x0 + 2*r, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2*r, y1 - 2*r, x1, y1], 0, 90, fill=fill)


def _center_text(draw, text, font, y, width=WIDTH, color=None):
    """Draw centered text."""
    if color is None:
        color = COLORS["text_white"]
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) / 2, y), text, fill=color, font=font)


def _draw_accent_bar(draw, x, y, w, h, color):
    """Draw a colored accent bar."""
    _draw_rounded_rect(draw, (x, y, x + w, y + h), h // 2, color)


def make_slide(slide: dict, output_path: str):
    """Create a professional slide."""
    bg = COLORS["bg_dark"]
    accent = COLORS.get(slide.get("accent", "accent_red"), COLORS["accent_red"])
    title = slide.get("title", "")
    subtitle = slide.get("subtitle", "")
    body = slide.get("body", "")
    body_lines = slide.get("body_lines", [])  # list of (text, color_key) tuples

    img = Image.new("RGB", (WIDTH, HEIGHT), bg)
    draw = ImageDraw.Draw(img)

    # Subtle gradient overlay (top lighter)
    for i in range(200):
        alpha = int(15 * (1 - i / 200))
        draw.line([(0, i), (WIDTH, i)], fill=(bg[0] + alpha, bg[1] + alpha, bg[2] + alpha))

    # Accent bar at top
    _draw_accent_bar(draw, 0, 0, WIDTH, 6, accent)

    # Title
    font_title = get_font(64, weight="bold")
    _center_text(draw, title, font_title, 120, color=accent)

    # Subtitle
    if subtitle:
        font_sub = get_font(36, weight="light")
        _center_text(draw, subtitle, font_sub, 210, color=COLORS["text_gray"])

    # Body — handle both plain string and structured body_lines
    if body_lines:
        font_body = get_font(34, mono=False)
        y = 340
        for text, color_key in body_lines:
            color = COLORS.get(color_key, COLORS["text_white"])
            # Bullet point
            if text.startswith("- "):
                text = text[2:]
                draw.ellipse([180, y + 12, 188, y + 20], fill=accent)
                draw.text([210, y], text, fill=color, font=font_body)
            elif text.startswith("  "):
                # Indented line
                draw.text([250, y], text.strip(), fill=COLORS["text_gray"], font=get_font(30, mono=True))
            else:
                draw.text([200, y], text, fill=color, font=font_body)
            y += 55
    elif body:
        font_body = get_font(34, mono=True)
        lines = body.split("\n")
        y = 340
        for line in lines:
            if line.strip().startswith("-"):
                # Bullet
                text = line.strip()[1:].strip()
                draw.ellipse([180, y + 14, 190, y + 24], fill=accent)
                draw.text([220, y], text, fill=COLORS["text_white"], font=get_font(34))
            elif "-->" in line:
                # Pipeline arrow
                draw.text([200, y], line, fill=COLORS["text_gray"], font=get_font(30, mono=True))
            elif line.strip():
                draw.text([200, y], line, fill=COLORS["text_white"], font=font_body)
            y += 50

    # Footer
    _draw_accent_bar(draw, 60, HEIGHT - 40, 40, 3, accent)
    draw.text([60, HEIGHT - 32], "SpecGuard", fill=COLORS["text_dim"], font=get_font(18))

    img.save(output_path, "PNG")
    print(f"  Saved: {output_path}")


def make_terminal_frame(title: str, lines: list, output_path: str):
    """Create a professional terminal-style frame."""
    # Terminal background
    img = Image.new("RGB", (WIDTH, HEIGHT), (12, 12, 15))
    draw = ImageDraw.Draw(img)

    # Window chrome
    _draw_rounded_rect(draw, (80, 60, WIDTH - 80, HEIGHT - 60), 12, (30, 30, 45))
    # Title bar
    _draw_rounded_rect(draw, (80, 60, WIDTH - 80, 120), 12, (45, 45, 60))
    draw.rectangle([80, 100, WIDTH - 80, 120], fill=(45, 45, 60))

    # Traffic lights
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = 110 + i * 28
        draw.ellipse([cx, 75, cx + 18, 93], fill=color)

    # Terminal title
    font_title = get_font(24, weight="bold")
    draw.text([200, 78], title, fill=(200, 200, 210), font=font_title)

    # Terminal content
    font = get_font(22, mono=True)
    y = 150
    for line in lines:
        # Color coding
        if "PASSED" in line or "PASS" in line or "passed" in line:
            color = COLORS["accent_green"]
        elif "FAIL" in line or "fail" in line.lower():
            color = COLORS["accent_red"]
        elif "===" in line or "---" in line:
            color = COLORS["text_dim"]
        elif "PHASE" in line or "DASHBOARD" in line or "SUMMARY" in line:
            color = COLORS["accent_red"]
        elif "SCENARIO" in line or "IMPLEMENTED" in line or "TESTED" in line or "REGRESSION" in line:
            color = COLORS["accent_blue"]
        elif "Ready" in line or "100" in line or "NEXT" in line:
            color = COLORS["accent_green"]
        elif "Verdict" in line:
            color = COLORS["accent_green"]
        elif "Security" in line or "Critical" in line or "High" in line:
            color = COLORS["accent_red"]
        else:
            color = (200, 200, 210)

        draw.text([120, y], line, fill=color, font=font)
        y += 30
        if y > HEIGHT - 80:
            break

    # Footer accent
    _draw_accent_bar(draw, 80, HEIGHT - 20, 100, 2, COLORS["accent_red"])

    img.save(output_path, "PNG")
    print(f"  Saved: {output_path}")


def make_case_study_frame(title: str, spec_lines: list, code_lines: list, output_path: str):
    """Render a polished before/after case study: Gherkin on the left, code on the right."""
    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_dark"])
    draw = ImageDraw.Draw(img)
    accent = COLORS["accent_green"]

    for i in range(260):
        alpha = int(14 * (1 - i / 260))
        draw.line([(0, i), (WIDTH, i)], fill=(15 + alpha, 15 + alpha, 30 + alpha))
    _draw_accent_bar(draw, 0, 0, WIDTH, 6, accent)
    _center_text(draw, title, get_font(58, weight="bold"), 80, color=COLORS["text_white"])
    _center_text(draw, "A real spec becomes a reviewed implementation", get_font(28, weight="light"), 165, color=COLORS["text_gray"])

    cards = [
        (100, 245, 900, 875, "Gherkin specification", spec_lines, COLORS["accent_red"]),
        (1020, 245, 1820, 875, "Guarded generated Python", code_lines, COLORS["accent_green"]),
    ]
    for x0, y0, x1, y1, label, lines, label_color in cards:
        _draw_rounded_rect(draw, (x0, y0, x1, y1), 20, COLORS["bg_card"])
        _draw_rounded_rect(draw, (x0, y0, x1, y0 + 58), 20, (39, 39, 59))
        draw.rectangle([x0, y0 + 38, x1, y0 + 58], fill=(39, 39, 59))
        draw.text([x0 + 30, y0 + 14], label, fill=label_color, font=get_font(23, weight="bold"))
        y = y0 + 88
        for line in lines[:20]:
            color = label_color if line.startswith(("Feature:", "Scenario:", "def ", "class ", "return ", "raise ")) else COLORS["text_white"]
            draw.text([x0 + 28, y], line, fill=color, font=get_font(20, mono=True))
            y += 31

    _draw_rounded_rect(draw, (650, 915, 1270, 985), 30, (0, 110, 92))
    _center_text(draw, "Spec -> response -> parse -> scan -> write", get_font(23, weight="bold"), 936, color=COLORS["text_white"])
    draw.text([60, HEIGHT - 34], "SpecGuard / case study", fill=COLORS["text_dim"], font=get_font(18))
    img.save(output_path, "PNG")
    print(f"  Saved: {output_path}")


if __name__ == "__main__":
    os.makedirs("/tmp/slides2", exist_ok=True)
    make_slide({
        "title": "SpecGuard",
        "subtitle": "Spec-Driven Development Agent",
        "accent": "accent_red",
    }, "/tmp/slides2/test1.png")
    make_slide({
        "title": "The Problem",
        "body": "- Vibe-coded prototypes rot fast\n- Hallucinated packages\n- Missing input validation",
        "accent": "accent_red",
    }, "/tmp/slides2/test2.png")
    make_terminal_frame("Terminal", ["PHASE 1: SPEC ANALYSIS", "Scenarios: 9", "16 passed"], "/tmp/slides2/test3.png")
    print("OK")
