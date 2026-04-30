from fpdf import FPDF
from fpdf.enums import XPos, YPos

# ─── UNICODE FONT (DejaVu TTF) ──────────────────────────────────────────────
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


class Resume(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(
            0, 10, f"{self.page_no()}", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT
        )


pdf = Resume()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Register Liberation Sans fonts (proper Unicode with italic support)
font_regular = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
font_bold = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
font_italic = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"
font_bold_italic = "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"

pdf.add_font("DejaVu", "", font_regular)
pdf.add_font("DejaVu", "B", font_bold)
pdf.add_font("DejaVu", "I", font_italic)
pdf.add_font("DejaVu", "BI", font_bold_italic)

# ─── NAME ────────────────────────────────────────────────────────────────────
pdf.set_font("DejaVu", "B", 20)
pdf.set_text_color(30, 30, 30)
pdf.cell(0, 10, "KHALID WALEED ALMANIE", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# ─── CONTACT ─────────────────────────────────────────────────────────────────
pdf.set_font("DejaVu", "", 9)
pdf.set_text_color(80, 80, 80)
pdf.cell(
    0,
    5,
    "+65 91337344  |  linkedin.com/in/khalid-waleed-sb82052193  |  almanie.s.2025@mba.smu.edu.sg  |  Singapore",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT,
)
pdf.ln(4)


# ─── SECTION HELPER ──────────────────────────────────────────────────────────
def section(pdf, title):
    pdf.set_font("DejaVu", "B", 10)
    pdf.set_text_color(20, 80, 160)
    pdf.cell(0, 6, title.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(20, 80, 160)
    pdf.set_line_width(0.5)
    pdf.line(0, pdf.get_y(), 210, pdf.get_y())
    pdf.ln(3)


def entry(pdf, title, org, dates, bullets):
    pdf.set_font("DejaVu", "B", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(115, 5, title, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5, org, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("DejaVu", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 4, dates, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(50, 50, 50)
    for b in bullets:
        pdf.set_x(8)
        pdf.multi_cell(0, 4.2, f"  {b}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)


def project(pdf, title, org, dates, bullets):
    pdf.set_font("DejaVu", "B", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(115, 5, title, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font("DejaVu", "I", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5, org, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("DejaVu", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 4, dates, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(50, 50, 50)
    for b in bullets:
        pdf.set_x(8)
        pdf.multi_cell(0, 4.2, f"  {b}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)


def simple_line(pdf, text, indent=8):
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(50, 50, 50)
    pdf.set_x(indent)
    pdf.multi_cell(0, 4.2, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


# ─── EXPERIENCE ──────────────────────────────────────────────────────────────
section(pdf, "Experience")

entry(
    pdf,
    "Logistics Operations Team Leader",
    "JollyChic (China HQ; Saudi Arabia ops)          Sep 2019 – Nov 2020",
    "China-headquartered e-commerce retailer operating in Saudi Arabia",
    [
        "Directed a team of 40+ staff across logistics operations, achieving 100% on-time delivery across all shifts in a high-volume e-commerce environment serving the Saudi Arabian market",
        "Redesigned shift scheduling workflows, eliminating coverage gaps and increasing daily throughput by 25%",
        "Resolved on-site operational disruptions in real time, maintaining uninterrupted workflows across multiple shifts",
    ],
)

entry(
    pdf,
    "Assistant Project Manager",
    "Expert Path (Riyadh, KSA)                       Apr 2021 – Feb 2022",
    "Riyadh-based legal consulting firm specializing in occupational health and safety",
    [
        "Executed performance audit of NWC distillation stations across Saudi Arabia, identifying operational efficiencies and compliance gaps; interviewed 100+ candidates; managed project billing, timelines, and cross-functional stakeholder communications",
        "Coordinated Riyadh Municipality's commercial shop compliance restructuring across the capital, aligning government agencies, engineers, and legal teams to deliver compliance-driven landscape reforms on schedule",
    ],
)

# ─── TECHNICAL PROJECTS ───────────────────────────────────────────────────────
section(pdf, "Technical Projects")

project(
    pdf,
    "FX Settlement Lock Analysis",
    "Independent Research                                                    2026",
    "",
    [
        "Validated e-CNY architectural dominance over SWIFT via Python simulation of PBOC-HKMA-CBUAE-BOT multi-CBDC FX settlement; submitted findings to BIS Innovation Hub Singapore Centre",
        "Executed performance audit of NWC distillation stations across Saudi Arabia, identifying operational efficiencies and compliance gaps; interviewed 100+ candidates; managed project billing, timelines, and cross-functional stakeholder communications",
        "Led 40+ staff to 100% on-time delivery across Saudi last-mile operations at JollyChic, China's largest cross-border e-commerce platform",
    ],
)


# ─── INTERNATIONAL EXPERIENCE ─────────────────────────────────────────────────
section(pdf, "International Experience")

project(
    pdf,
    "CUFE Week Exchange — Beijing, China",
    "Singapore Management University                                          Mar 2026",
    "",
    [
        "Analyzed China's AI landscape via site visits to iFLYTEK, Haidian Science City, and Meituan 'Super Brain'; evaluated wearable AI market entry strategy for Western brands in China",
    ],
)

project(
    pdf,
    "Overseas Immersion Programme — Bangkok, Thailand",
    "ESG & Community Stewardship Focus                                       Oct 2025",
    "",
    [
        "Conducted field research on mangrove conservation in Bang Tabun district; developed community ESG stewardship framework for coastal resilience; evaluated DTGO's Forestias megaproject",
    ],
)

# ─── EDUCATION ────────────────────────────────────────────────────────────────
section(pdf, "Education")

pdf.set_font("DejaVu", "B", 10)
pdf.set_text_color(30, 30, 30)
pdf.cell(
    115,
    5,
    "Master of Business Administration — Finance Track",
    new_x=XPos.RIGHT,
    new_y=YPos.TOP,
)
pdf.set_font("DejaVu", "", 9)
pdf.set_text_color(80, 80, 80)
pdf.cell(
    0,
    5,
    "Singapore Management University",
    align="R",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT,
)
pdf.set_font("DejaVu", "I", 8)
pdf.set_text_color(120, 120, 120)
pdf.cell(0, 4, "Aug 2025 – Present", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(2)

pdf.set_font("DejaVu", "B", 10)
pdf.set_text_color(30, 30, 30)
pdf.cell(
    115,
    5,
    "Bachelor of Arts — English Language and Translation",
    new_x=XPos.RIGHT,
    new_y=YPos.TOP,
)
pdf.set_font("DejaVu", "", 9)
pdf.set_text_color(80, 80, 80)
pdf.cell(
    0,
    5,
    "Qassim University, Saudi Arabia",
    align="R",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT,
)
pdf.set_font("DejaVu", "I", 8)
pdf.set_text_color(120, 120, 120)
pdf.cell(0, 4, "Apr 2014 – Dec 2018", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(3)

# ─── SKILLS ──────────────────────────────────────────────────────────────────
section(pdf, "Skills")


def skill_group(pdf, label, items, indent=8):
    pdf.set_font("DejaVu", "B", 9)
    pdf.set_text_color(20, 80, 160)
    pdf.set_x(indent)
    pdf.cell(35, 4.2, label, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 4.2, items, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


skill_group(
    pdf,
    "Finance & Val.",
    "DCF Valuation  ·  Comparable Company Analysis  ·  LBO Modeling  ·  EBITDA Normalization  ·  Capital Structure  ·  M&A Fundamentals  ·  Portfolio Management",
)
skill_group(
    pdf,
    "Data & ML",
    "Python  ·  pandas  ·  NumPy  ·  scikit-learn  ·  Data Visualization  ·  Machine Learning",
)
skill_group(
    pdf,
    "Operations",
    "Supply Chain Optimization  ·  Risk Management  ·  ESG Analysis  ·  Go-to-Market Strategy",
)
skill_group(
    pdf,
    "Leadership",
    "Team Management (40+)  ·  Cross-cultural Communication  ·  Stakeholder Management",
)
skill_group(
    pdf,
    "Languages",
    "Arabic (Native)  ·  English (Professional)  ·  Mandarin (Conversational)",
)

out = "/mnt/c/Users/User/Desktop/cv-Almanie-K.pdf"
pdf.output(out)
print(f"Saved: {out}")
