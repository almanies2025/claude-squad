#!/usr/bin/env python3
"""
Saudi Mining Opportunity - Professional PowerPoint Presentation
Dark blue/gold color scheme for formal business presentation
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
from pptx.enum.dml import MSO_THEME_COLOR
import copy

# ── Color Palette ──────────────────────────────────────────────────────────────
DARK_BLUE = RGBColor(0x0D, 0x2B, 0x55)  # deep navy
MID_BLUE = RGBColor(0x1A, 0x4F, 0x8A)  # royal blue
ACCENT_GOLD = RGBColor(0xC9, 0xA0, 0x2C)  # rich gold
LIGHT_GOLD = RGBColor(0xF0, 0xD9, 0x7B)  # pale gold
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
OFF_WHITE = RGBColor(0xF5, 0xF7, 0xFA)
LIGHT_GRAY = RGBColor(0xD0, 0xDA, 0xE4)
DARK_GRAY = RGBColor(0x44, 0x44, 0x44)
RED_ALERT = RGBColor(0xC0, 0x39, 0x2B)

# ── Helpers ───────────────────────────────────────────────────────────────────


def set_shape_fill(shape, color: RGBColor):
    """Solid fill a shape with a given RGBColor."""
    fill = shape.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_text_box(
    slide,
    left,
    top,
    width,
    height,
    text,
    font_size=18,
    bold=False,
    color=WHITE,
    align=PP_ALIGN.LEFT,
    italic=False,
    wrap=True,
):
    """Add a text box and return it."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txBox


def add_rectangle(slide, left, top, width, height, fill_color, line_color=None):
    """Add a filled rectangle shape."""
    from pptx.util import Emu

    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        left,
        top,
        width,
        height,
    )
    set_shape_fill(shape, fill_color)
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape


def add_rich_text_box(
    slide, left, top, width, height, lines, default_size=16, wrap=True
):
    """
    lines: list of dicts with keys:
      text, size (opt), bold (opt), color (opt), align (opt), italic (opt)
    """
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = wrap
    first = True
    for line in lines:
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()
        p.alignment = line.get("align", PP_ALIGN.LEFT)
        run = p.add_run()
        run.text = line.get("text", "")
        run.font.size = Pt(line.get("size", default_size))
        run.font.bold = line.get("bold", False)
        run.font.italic = line.get("italic", False)
        run.font.color.rgb = line.get("color", WHITE)
    return txBox


# ── Presentation Setup ────────────────────────────────────────────────────────
prs = Presentation()
prs.slide_width = Inches(13.33)
prs.slide_height = Inches(7.5)

# Widescreen 16:9 feel — use blank layout throughout
blank_layout = prs.slide_layouts[6]


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Title Slide
# ══════════════════════════════════════════════════════════════════════════════
slide1 = prs.slides.add_slide(blank_layout)

# Full-bleed dark blue background
bg = add_rectangle(
    slide1,
    left=Inches(0),
    top=Inches(0),
    width=Inches(13.33),
    height=Inches(7.5),
    fill_color=DARK_BLUE,
)

# Gold accent bar at top
add_rectangle(
    slide1,
    left=Inches(0),
    top=Inches(0),
    width=Inches(13.33),
    height=Inches(0.18),
    fill_color=ACCENT_GOLD,
)

# Gold accent bar at bottom
add_rectangle(
    slide1,
    left=Inches(0),
    top=Inches(7.32),
    width=Inches(13.33),
    height=Inches(0.18),
    fill_color=ACCENT_GOLD,
)

# Decorative vertical gold line (left side accent)
add_rectangle(
    slide1,
    left=Inches(0.6),
    top=Inches(1.5),
    width=Inches(0.07),
    height=Inches(3.5),
    fill_color=ACCENT_GOLD,
)

# Main title
add_text_box(
    slide1,
    left=Inches(0.9),
    top=Inches(1.6),
    width=Inches(11.5),
    height=Inches(1.3),
    text="Saudi Mining Construction Opportunity",
    font_size=44,
    bold=True,
    color=WHITE,
    align=PP_ALIGN.LEFT,
)

# Subtitle
add_text_box(
    slide1,
    left=Inches(0.9),
    top=Inches(3.0),
    width=Inches(11.5),
    height=Inches(0.8),
    text="Vision 2030: A Once-in-a-Decade Window",
    font_size=26,
    bold=False,
    color=ACCENT_GOLD,
    align=PP_ALIGN.LEFT,
)

# Gold divider line
add_rectangle(
    slide1,
    left=Inches(0.9),
    top=Inches(3.85),
    width=Inches(9.0),
    height=Inches(0.04),
    fill_color=ACCENT_GOLD,
)

# Presenter
add_text_box(
    slide1,
    left=Inches(0.9),
    top=Inches(4.1),
    width=Inches(11.5),
    height=Inches(0.6),
    text="[Your Name], Saudi Arabia Operations",
    font_size=20,
    bold=False,
    color=LIGHT_GOLD,
    align=PP_ALIGN.LEFT,
)

# Date
add_text_box(
    slide1,
    left=Inches(0.9),
    top=Inches(4.7),
    width=Inches(11.5),
    height=Inches(0.5),
    text="10 May 2026",
    font_size=18,
    bold=False,
    color=LIGHT_GRAY,
    align=PP_ALIGN.LEFT,
)

# CONFIDENTIAL footer
add_text_box(
    slide1,
    left=Inches(0),
    top=Inches(7.0),
    width=Inches(13.33),
    height=Inches(0.4),
    text="CONFIDENTIAL — Internal Use Only",
    font_size=12,
    bold=False,
    color=LIGHT_GRAY,
    align=PP_ALIGN.CENTER,
)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — The Opportunity (3 Big Numbers)
# ══════════════════════════════════════════════════════════════════════════════
slide2 = prs.slides.add_slide(blank_layout)

# Background
add_rectangle(
    slide2,
    left=Inches(0),
    top=Inches(0),
    width=Inches(13.33),
    height=Inches(7.5),
    fill_color=DARK_BLUE,
)

# Gold top bar
add_rectangle(
    slide2,
    left=Inches(0),
    top=Inches(0),
    width=Inches(13.33),
    height=Inches(0.12),
    fill_color=ACCENT_GOLD,
)

# Title
add_text_box(
    slide2,
    left=Inches(0.5),
    top=Inches(0.35),
    width=Inches(12.3),
    height=Inches(0.8),
    text="Why Saudi Arabia — Why Now",
    font_size=34,
    bold=True,
    color=WHITE,
    align=PP_ALIGN.LEFT,
)

# Gold underline for title
add_rectangle(
    slide2,
    left=Inches(0.5),
    top=Inches(1.1),
    width=Inches(7.0),
    height=Inches(0.045),
    fill_color=ACCENT_GOLD,
)

# ── Three big number boxes ────────────────────────────────────────────────────
box_defs = [
    {
        "number": "USD 426B",
        "label": "Saudi mining GDP target by 2035\nunder Vision 2030",
        "x": 0.4,
    },
    {
        "number": "18–24 months",
        "label": "Window to establish position\nbefore market consolidates",
        "x": 4.65,
    },
    {
        "number": "USD 5B+",
        "label": "Chinese EPC contracts already won\nin Saudi Arabia (2022 alone)",
        "x": 8.9,
    },
]

box_width = Inches(3.9)
box_height = Inches(3.4)
box_top = Inches(1.4)

for bd in box_defs:
    bx = bd["x"]

    # Card background
    add_rectangle(
        slide2,
        left=Inches(bx),
        top=box_top,
        width=box_width,
        height=box_height,
        fill_color=MID_BLUE,
    )

    # Gold top accent on card
    add_rectangle(
        slide2,
        left=Inches(bx),
        top=box_top,
        width=box_width,
        height=Inches(0.08),
        fill_color=ACCENT_GOLD,
    )

    # Big number
    add_text_box(
        slide2,
        left=Inches(bx + 0.15),
        top=box_top + Inches(0.25),
        width=Inches(box_width.inches - 0.3),
        height=Inches(1.1),
        text=bd["number"],
        font_size=36,
        bold=True,
        color=ACCENT_GOLD,
        align=PP_ALIGN.CENTER,
    )

    # Separator line
    add_rectangle(
        slide2,
        left=Inches(bx + 0.4),
        top=box_top + Inches(1.45),
        width=Inches(box_width.inches - 0.8),
        height=Inches(0.03),
        fill_color=ACCENT_GOLD,
    )

    # Label text
    add_text_box(
        slide2,
        left=Inches(bx + 0.15),
        top=box_top + Inches(1.6),
        width=Inches(box_width.inches - 0.3),
        height=Inches(1.5),
        text=bd["label"],
        font_size=16,
        bold=False,
        color=WHITE,
        align=PP_ALIGN.CENTER,
    )

# Bottom warning note
note_bg = add_rectangle(
    slide2,
    left=Inches(0.4),
    top=Inches(5.05),
    width=Inches(12.53),
    height=Inches(0.85),
    fill_color=RGBColor(0x1E, 0x3A, 0x5F),
)

add_text_box(
    slide2,
    left=Inches(0.55),
    top=Inches(5.12),
    width=Inches(12.2),
    height=Inches(0.7),
    text="Saudi construction awards fell 60% in 2025. Fewer contracts = more competition. Early entrants win.",
    font_size=16,
    bold=True,
    color=ACCENT_GOLD,
    align=PP_ALIGN.CENTER,
)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — Our Unique Position
# ══════════════════════════════════════════════════════════════════════════════
slide3 = prs.slides.add_slide(blank_layout)

add_rectangle(
    slide3,
    left=Inches(0),
    top=Inches(0),
    width=Inches(13.33),
    height=Inches(7.5),
    fill_color=DARK_BLUE,
)
add_rectangle(
    slide3,
    left=Inches(0),
    top=Inches(0),
    width=Inches(13.33),
    height=Inches(0.12),
    fill_color=ACCENT_GOLD,
)

add_text_box(
    slide3,
    left=Inches(0.5),
    top=Inches(0.3),
    width=Inches(12.3),
    height=Inches(0.75),
    text="What We Have That Others Don't",
    font_size=32,
    bold=True,
    color=WHITE,
    align=PP_ALIGN.LEFT,
)
add_rectangle(
    slide3,
    left=Inches(0.5),
    top=Inches(1.0),
    width=Inches(6.5),
    height=Inches(0.045),
    fill_color=ACCENT_GOLD,
)

# ── Two columns ───────────────────────────────────────────────────────────────
col_configs = [
    {
        "title": "Saudi Side (My Contribution):",
        "items": [
            "Ministry of Industry & Mineral Resources contact",
            "Local market knowledge and language",
            "Network of potential Saudi JV partners",
            "Etimad and MOMRA registration capability",
        ],
        "x": 0.4,
    },
    {
        "title": "China Side (Manager's Network):",
        "items": [
            "Chinese construction / mining company",
            "Chinese equipment supply chains",
            "Chinese policy bank financing (EXIM/CDB)",
            "Technical credentials and track record",
        ],
        "x": 6.9,
    },
]

col_width = Inches(6.0)
for col in col_configs:
    cx = col["x"]

    # Column card
    add_rectangle(
        slide3,
        left=Inches(cx),
        top=Inches(1.2),
        width=col_width,
        height=Inches(4.5),
        fill_color=MID_BLUE,
    )
    add_rectangle(
        slide3,
        left=Inches(cx),
        top=Inches(1.2),
        width=col_width,
        height=Inches(0.08),
        fill_color=ACCENT_GOLD,
    )

    # Column title
    add_text_box(
        slide3,
        left=Inches(cx + 0.2),
        top=Inches(1.35),
        width=Inches(col_width.inches - 0.4),
        height=Inches(0.6),
        text=col["title"],
        font_size=18,
        bold=True,
        color=ACCENT_GOLD,
        align=PP_ALIGN.LEFT,
    )

    # Divider under title
    add_rectangle(
        slide3,
        left=Inches(cx + 0.2),
        top=Inches(1.95),
        width=Inches(col_width.inches - 0.4),
        height=Inches(0.03),
        fill_color=ACCENT_GOLD,
    )

    # Bullet items
    for i, item in enumerate(col["items"]):
        iy = 2.15 + i * 0.78

        # Bullet dot
        dot = add_rectangle(
            slide3,
            left=Inches(cx + 0.25),
            top=Inches(iy + 0.12),
            width=Inches(0.14),
            height=Inches(0.14),
            fill_color=ACCENT_GOLD,
        )

        add_text_box(
            slide3,
            left=Inches(cx + 0.5),
            top=Inches(iy),
            width=Inches(col_width.inches - 0.7),
            height=Inches(0.65),
            text=item,
            font_size=15,
            bold=False,
            color=WHITE,
            align=PP_ALIGN.LEFT,
        )

# Bottom callout bar
add_rectangle(
    slide3,
    left=Inches(0.4),
    top=Inches(5.9),
    width=Inches(12.53),
    height=Inches(0.85),
    fill_color=ACCENT_GOLD,
)

add_text_box(
    slide3,
    left=Inches(0.55),
    top=Inches(5.95),
    width=Inches(12.2),
    height=Inches(0.75),
    text="Together: A complete, compliant, competitive offering",
    font_size=20,
    bold=True,
    color=DARK_BLUE,
    align=PP_ALIGN.CENTER,
)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — The Step-by-Step Strategy
# ══════════════════════════════════════════════════════════════════════════════
slide4 = prs.slides.add_slide(blank_layout)

add_rectangle(
    slide4,
    left=Inches(0),
    top=Inches(0),
    width=Inches(13.33),
    height=Inches(7.5),
    fill_color=DARK_BLUE,
)
add_rectangle(
    slide4,
    left=Inches(0),
    top=Inches(0),
    width=Inches(13.33),
    height=Inches(0.12),
    fill_color=ACCENT_GOLD,
)

add_text_box(
    slide4,
    left=Inches(0.5),
    top=Inches(0.3),
    width=Inches(12.3),
    height=Inches(0.75),
    text="How We Win — 5 Steps",
    font_size=32,
    bold=True,
    color=WHITE,
    align=PP_ALIGN.LEFT,
)
add_rectangle(
    slide4,
    left=Inches(0.5),
    top=Inches(1.0),
    width=Inches(5.5),
    height=Inches(0.045),
    fill_color=ACCENT_GOLD,
)

# ── 5 Steps horizontal flow ───────────────────────────────────────────────────
steps = [
    {
        "num": "1",
        "title": "Introduction",
        "desc": "Manager introduces\nChinese construction\ncompany",
        "tag": "",
    },
    {
        "num": "2",
        "title": "Registration",
        "desc": "Etimad + MOMRA\n(Weeks 2–4)",
        "tag": "",
    },
    {
        "num": "3",
        "title": "Ministry Meeting",
        "desc": "Official MIMR meeting\nthrough proper channels\n(Weeks 3–5)",
        "tag": "",
    },
    {
        "num": "4",
        "title": "JV Formation",
        "desc": "Saudi partner\nidentification and\ndue diligence\n(Month 2–4)",
        "tag": "",
    },
    {
        "num": "5",
        "title": "Tender Bid",
        "desc": "Pre-qualification and\ncompetitive bid\nsubmission\n(Month 4–9)",
        "tag": "",
    },
]

arrow_color = ACCENT_GOLD

step_w = Inches(2.2)
step_h = Inches(4.4)
start_x = Inches(0.35)
step_top = Inches(1.2)
gap = Inches(0.35)

for i, step in enumerate(steps):
    sx = start_x + i * (step_w + gap)

    # Step card
    add_rectangle(
        slide4, left=sx, top=step_top, width=step_w, height=step_h, fill_color=MID_BLUE
    )
    add_rectangle(
        slide4,
        left=sx,
        top=step_top,
        width=step_w,
        height=Inches(0.08),
        fill_color=ACCENT_GOLD,
    )

    # Step number circle background
    add_rectangle(
        slide4,
        left=sx + Inches(0.8),
        top=step_top + Inches(0.2),
        width=Inches(0.6),
        height=Inches(0.6),
        fill_color=ACCENT_GOLD,
    )

    add_text_box(
        slide4,
        left=sx,
        top=step_top + Inches(0.22),
        width=step_w,
        height=Inches(0.6),
        text=step["num"],
        font_size=28,
        bold=True,
        color=DARK_BLUE,
        align=PP_ALIGN.CENTER,
    )

    # Step title
    add_text_box(
        slide4,
        left=sx + Inches(0.1),
        top=step_top + Inches(0.95),
        width=Inches(step_w.inches - 0.2),
        height=Inches(0.7),
        text=step["title"],
        font_size=16,
        bold=True,
        color=ACCENT_GOLD,
        align=PP_ALIGN.CENTER,
    )

    # Divider
    add_rectangle(
        slide4,
        left=sx + Inches(0.3),
        top=step_top + Inches(1.7),
        width=Inches(step_w.inches - 0.6),
        height=Inches(0.03),
        fill_color=ACCENT_GOLD,
    )

    # Description
    add_text_box(
        slide4,
        left=sx + Inches(0.1),
        top=step_top + Inches(1.85),
        width=Inches(step_w.inches - 0.2),
        height=Inches(2.2),
        text=step["desc"],
        font_size=13,
        bold=False,
        color=WHITE,
        align=PP_ALIGN.CENTER,
    )

    # Arrow between steps (not after last)
    if i < len(steps) - 1:
        ax = sx + step_w + Inches(0.04)
        ay = step_top + step_h / 2 - Inches(0.12)
        add_text_box(
            slide4,
            left=ax,
            top=ay,
            width=Inches(0.27),
            height=Inches(0.3),
            text="▶",
            font_size=18,
            bold=True,
            color=ACCENT_GOLD,
            align=PP_ALIGN.CENTER,
        )


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — Compliance (Critical)
# ══════════════════════════════════════════════════════════════════════════════
slide5 = prs.slides.add_slide(blank_layout)

add_rectangle(
    slide5,
    left=Inches(0),
    top=Inches(0),
    width=Inches(13.33),
    height=Inches(7.5),
    fill_color=DARK_BLUE,
)
add_rectangle(
    slide5,
    left=Inches(0),
    top=Inches(0),
    width=Inches(13.33),
    height=Inches(0.12),
    fill_color=ACCENT_GOLD,
)

add_text_box(
    slide5,
    left=Inches(0.5),
    top=Inches(0.25),
    width=Inches(12.3),
    height=Inches(0.65),
    text="How We Stay Clean",
    font_size=32,
    bold=True,
    color=WHITE,
    align=PP_ALIGN.LEFT,
)
add_rectangle(
    slide5,
    left=Inches(0.5),
    top=Inches(0.88),
    width=Inches(5.0),
    height=Inches(0.04),
    fill_color=ACCENT_GOLD,
)

add_text_box(
    slide5,
    left=Inches(0.5),
    top=Inches(0.95),
    width=Inches(12.3),
    height=Inches(0.5),
    text="Fully Compliant Under Saudi and Chinese Law",
    font_size=18,
    bold=False,
    color=ACCENT_GOLD,
    align=PP_ALIGN.LEFT,
)

# ── Three compliance pillars ─────────────────────────────────────────────────
pillars = [
    {
        "title": "Saudi Law",
        "subtitle": "Anti-Bribery Royal Decree 1975\n+ Tenders Law M/128 (2019)",
        "body": "We use only official channels,\nno payments, no gifts to officials",
        "x": 0.4,
    },
    {
        "title": "Chinese Law",
        "subtitle": "Criminal Law Art. 391\n+ Anti-Foreign Bribery Law (2021)",
        "body": "Zero impropriety;\nall interactions documented",
        "x": 4.65,
    },
    {
        "title": "Our Standard",
        "subtitle": "Internal compliance protocol",
        "body": "Every meeting logged; Saudi legal counsel\npresent; no non-public information accessed",
        "x": 8.9,
    },
]

pillar_w = Inches(3.9)
pillar_h = Inches(3.9)
pillar_top = Inches(1.6)

for p in pillars:
    px = p["x"]

    # Card
    add_rectangle(
        slide5,
        left=Inches(px),
        top=pillar_top,
        width=Inches(pillar_w),
        height=Inches(pillar_h),
        fill_color=MID_BLUE,
    )
    add_rectangle(
        slide5,
        left=Inches(px),
        top=pillar_top,
        width=Inches(pillar_w),
        height=Inches(0.08),
        fill_color=ACCENT_GOLD,
    )

    # Gold shield-style header bar
    add_rectangle(
        slide5,
        left=Inches(px),
        top=pillar_top + Inches(0.08),
        width=Inches(pillar_w),
        height=Inches(0.65),
        fill_color=RGBColor(0x0A, 0x1F, 0x40),
    )

    # Title
    add_text_box(
        slide5,
        left=Inches(px + 0.15),
        top=pillar_top + Inches(0.12),
        width=Inches(pillar_w.inches - 0.3),
        height=Inches(0.55),
        text=p["title"],
        font_size=18,
        bold=True,
        color=ACCENT_GOLD,
        align=PP_ALIGN.CENTER,
    )

    # Subtitle / law reference
    add_text_box(
        slide5,
        left=Inches(px + 0.1),
        top=pillar_top + Inches(0.82),
        width=Inches(pillar_w.inches - 0.2),
        height=Inches(0.85),
        text=p["subtitle"],
        font_size=13,
        bold=False,
        color=LIGHT_GOLD,
        align=PP_ALIGN.CENTER,
    )

    # Divider
    add_rectangle(
        slide5,
        left=Inches(px + 0.3),
        top=pillar_top + Inches(1.75),
        width=Inches(pillar_w.inches - 0.6),
        height=Inches(0.03),
        fill_color=ACCENT_GOLD,
    )

    # Body text
    add_text_box(
        slide5,
        left=Inches(px + 0.1),
        top=pillar_top + Inches(1.9),
        width=Inches(pillar_w.inches - 0.2),
        height=Inches(1.6),
        text=p["body"],
        font_size=14,
        bold=False,
        color=WHITE,
        align=PP_ALIGN.CENTER,
    )

# Bottom personal commitment
add_rectangle(
    slide5,
    left=Inches(0.4),
    top=Inches(5.75),
    width=Inches(12.53),
    height=Inches(0.9),
    fill_color=RGBColor(0x1E, 0x3A, 0x5F),
)

add_text_box(
    slide5,
    left=Inches(0.55),
    top=Inches(5.85),
    width=Inches(12.2),
    height=Inches(0.7),
    text="I will not risk my professional reputation in Saudi Arabia for anything less.",
    font_size=18,
    bold=True,
    color=ACCENT_GOLD,
    align=PP_ALIGN.CENTER,
)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — The Ask (Phase 1)
# ══════════════════════════════════════════════════════════════════════════════
slide6 = prs.slides.add_slide(blank_layout)

add_rectangle(
    slide6,
    left=Inches(0),
    top=Inches(0),
    width=Inches(13.33),
    height=Inches(7.5),
    fill_color=DARK_BLUE,
)
add_rectangle(
    slide6,
    left=Inches(0),
    top=Inches(0),
    width=Inches(13.33),
    height=Inches(0.12),
    fill_color=ACCENT_GOLD,
)

add_text_box(
    slide6,
    left=Inches(0.5),
    top=Inches(0.3),
    width=Inches(12.3),
    height=Inches(0.75),
    text="Phase 1: Small Investment, Big Clarity",
    font_size=32,
    bold=True,
    color=WHITE,
    align=PP_ALIGN.LEFT,
)
add_rectangle(
    slide6,
    left=Inches(0.5),
    top=Inches(1.0),
    width=Inches(8.0),
    height=Inches(0.045),
    fill_color=ACCENT_GOLD,
)

# ── Three action item boxes ───────────────────────────────────────────────────
actions = [
    {
        "title": "1. Register on Etimad",
        "desc": "Saudi government procurement platform",
        "cost": "RMB 5,000",
        "x": 0.4,
    },
    {
        "title": "2. Formal MIMR Meeting",
        "desc": "Delegation visit to Riyadh\n(legal counsel + logistics)",
        "cost": "RMB 30,000",
        "x": 4.65,
    },
    {
        "title": "3. MOMRA Classification",
        "desc": "Contractor grade application",
        "cost": "RMB 3,000",
        "x": 8.9,
    },
]

act_w = Inches(3.9)
act_h = Inches(3.6)
act_top = Inches(1.2)

for act in actions:
    ax = act["x"]

    # Card
    add_rectangle(
        slide6,
        left=Inches(ax),
        top=act_top,
        width=act_w,
        height=act_h,
        fill_color=MID_BLUE,
    )
    add_rectangle(
        slide6,
        left=Inches(ax),
        top=act_top,
        width=act_w,
        height=Inches(0.08),
        fill_color=ACCENT_GOLD,
    )

    # Checkmark circle
    add_rectangle(
        slide6,
        left=Inches(ax) + act_w / 2 - Inches(0.3),
        top=act_top + Inches(0.2),
        width=Inches(0.6),
        height=Inches(0.6),
        fill_color=ACCENT_GOLD,
    )
    add_text_box(
        slide6,
        left=Inches(ax),
        top=act_top + Inches(0.22),
        width=Inches(act_w),
        height=Inches(0.55),
        text="✓",
        font_size=26,
        bold=True,
        color=DARK_BLUE,
        align=PP_ALIGN.CENTER,
    )

    # Title
    add_text_box(
        slide6,
        left=Inches(ax + 0.1),
        top=act_top + Inches(0.95),
        width=Inches(act_w.inches - 0.2),
        height=Inches(0.6),
        text=act["title"],
        font_size=16,
        bold=True,
        color=WHITE,
        align=PP_ALIGN.CENTER,
    )

    # Description
    add_text_box(
        slide6,
        left=Inches(ax + 0.1),
        top=act_top + Inches(1.55),
        width=Inches(act_w.inches - 0.2),
        height=Inches(1.0),
        text=act["desc"],
        font_size=14,
        bold=False,
        color=LIGHT_GRAY,
        align=PP_ALIGN.CENTER,
    )

    # Cost — gold, prominent
    add_text_box(
        slide6,
        left=Inches(ax + 0.1),
        top=act_top + Inches(2.65),
        width=Inches(act_w.inches - 0.2),
        height=Inches(0.6),
        text=act["cost"],
        font_size=24,
        bold=True,
        color=ACCENT_GOLD,
        align=PP_ALIGN.CENTER,
    )

# ── Total Phase 1 box ─────────────────────────────────────────────────────────
# Gold highlight box for total
add_rectangle(
    slide6,
    left=Inches(0.4),
    top=Inches(5.05),
    width=Inches(12.53),
    height=Inches(0.95),
    fill_color=ACCENT_GOLD,
)

add_text_box(
    slide6,
    left=Inches(0.55),
    top=Inches(5.1),
    width=Inches(8.0),
    height=Inches(0.85),
    text="Total Phase 1:",
    font_size=28,
    bold=True,
    color=DARK_BLUE,
    align=PP_ALIGN.LEFT,
)

add_text_box(
    slide6,
    left=Inches(8.5),
    top=Inches(5.1),
    width=Inches(4.35),
    height=Inches(0.85),
    text="RMB 50,000",
    font_size=32,
    bold=True,
    color=DARK_BLUE,
    align=PP_ALIGN.RIGHT,
)

# Timeline note
add_text_box(
    slide6,
    left=Inches(0.4),
    top=Inches(6.1),
    width=Inches(12.53),
    height=Inches(0.5),
    text="Decision needed within 10 days.  Results in 30 days.",
    font_size=16,
    bold=True,
    color=LIGHT_GOLD,
    align=PP_ALIGN.CENTER,
)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — Close
# ══════════════════════════════════════════════════════════════════════════════
slide7 = prs.slides.add_slide(blank_layout)

add_rectangle(
    slide7,
    left=Inches(0),
    top=Inches(0),
    width=Inches(13.33),
    height=Inches(7.5),
    fill_color=DARK_BLUE,
)
add_rectangle(
    slide7,
    left=Inches(0),
    top=Inches(0),
    width=Inches(13.33),
    height=Inches(0.12),
    fill_color=ACCENT_GOLD,
)

add_text_box(
    slide7,
    left=Inches(0.5),
    top=Inches(0.3),
    width=Inches(12.3),
    height=Inches(0.75),
    text="10 Days to Decide.  18 Months to Act.",
    font_size=32,
    bold=True,
    color=WHITE,
    align=PP_ALIGN.LEFT,
)
add_rectangle(
    slide7,
    left=Inches(0.5),
    top=Inches(1.0),
    width=Inches(8.5),
    height=Inches(0.045),
    fill_color=ACCENT_GOLD,
)

# Main message box
add_rectangle(
    slide7,
    left=Inches(0.4),
    top=Inches(1.25),
    width=Inches(12.53),
    height=Inches(1.1),
    fill_color=MID_BLUE,
)
add_rectangle(
    slide7,
    left=Inches(0.4),
    top=Inches(1.25),
    width=Inches(12.53),
    height=Inches(0.07),
    fill_color=ACCENT_GOLD,
)

add_text_box(
    slide7,
    left=Inches(0.6),
    top=Inches(1.35),
    width=Inches(12.1),
    height=Inches(0.9),
    text="This is not a commitment. It is an option to find out if the opportunity is real.",
    font_size=22,
    bold=True,
    color=WHITE,
    align=PP_ALIGN.CENTER,
)

# Three bullet summary
add_rectangle(
    slide7,
    left=Inches(0.4),
    top=Inches(2.6),
    width=Inches(12.53),
    height=Inches(2.5),
    fill_color=RGBColor(0x0F, 0x24, 0x45),
)

bullets = [
    "✓  Can we register and meet the Ministry officially?",
    "✓  Are Saudi JV partners available and interested?",
    "✓  Is Chinese financing viable for Saudi mining projects?",
]
for j, bull in enumerate(bullets):
    add_text_box(
        slide7,
        left=Inches(0.7),
        top=Inches(2.8 + j * 0.72),
        width=Inches(12.0),
        height=Inches(0.6),
        text=bull,
        font_size=18,
        bold=False,
        color=WHITE,
        align=PP_ALIGN.LEFT,
    )

# Closing statement box
add_rectangle(
    slide7,
    left=Inches(0.4),
    top=Inches(5.3),
    width=Inches(12.53),
    height=Inches(0.9),
    fill_color=ACCENT_GOLD,
)

add_text_box(
    slide7,
    left=Inches(0.55),
    top=Inches(5.38),
    width=Inches(12.2),
    height=Inches(0.75),
    text="If Phase 1 works, we are positioned in the Saudi mining market for the next decade.",
    font_size=18,
    bold=True,
    color=DARK_BLUE,
    align=PP_ALIGN.CENTER,
)

# Footer
add_text_box(
    slide7,
    left=Inches(0),
    top=Inches(7.0),
    width=Inches(13.33),
    height=Inches(0.4),
    text="Presenter: [Your Name]  |  Date: 10 May 2026",
    font_size=12,
    bold=False,
    color=LIGHT_GRAY,
    align=PP_ALIGN.CENTER,
)

# Gold bottom bar
add_rectangle(
    slide7,
    left=Inches(0),
    top=Inches(7.32),
    width=Inches(13.33),
    height=Inches(0.18),
    fill_color=ACCENT_GOLD,
)


# ── Save ───────────────────────────────────────────────────────────────────────
out_path = "/mnt/c/Users/User/Documents/GitHub/claude-squad/workspaces/saudi-mining-bid-analysis/materials/saudi_mining_opportunity.pptx"
prs.save(out_path)
print(f"Saved: {out_path}")
