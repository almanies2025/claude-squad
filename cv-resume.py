"""
Resume PDF Generator — Finance/MBA Candidate
KHALID WALEED ALMANIE

Top-Down Design Methodology:
  LEVEL 1: Frame/Layout     — A4 single-column, margins, spatial division
  LEVEL 2: Feature Comm.   — Section anchors, visual hierarchy, scanability
  LEVEL 3: Components      — Section headers, bullet blocks, skills grid
  LEVEL 4: Visual Details  — Color palette, typography scale, spacing

Layout Specification:
  Page:       A4 (595.27 x 841.89 pts)
  Margins:    Top 72pt, Bottom 72pt, Left/Right 72pt (1 inch)
  Inner content width: 451.27 pts
  Name:       22pt, Helvetica-Bold, navy #1B3A5C
  Section:    11pt, Helvetica-Bold, uppercase, letterspaced, navy #1B3A5C
  Body:       9.5pt, Helvetica, #2C2C2C
  Accent rule: 0.75pt, navy #1B3A5C
  Subtle rule: 0.5pt, #CCCCCC
  Line height: 14pt body, 18pt between paragraphs
  Section gap: 20pt top margin before each section
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ─── Design Tokens ───────────────────────────────────────────────────────────

PAGE_W, PAGE_H = A4  # 595.27 x 841.89 pts
MARGIN = 0.75 * inch  # 54 pt
CONTENT_W = PAGE_W - 2 * MARGIN  # 487.27 pts

# Colors
NAVY = colors.HexColor("#1B3A5C")  # Primary — headers, rules
CHARCOAL = colors.HexColor("#2C2C2C")  # Body text
MID_GREY = colors.HexColor("#555555")  # Secondary text (dates, orgs)
LIGHT_GREY = colors.HexColor("#999999")  # Tertiary (sub-labels)
RULE_LIGHT = colors.HexColor("#CCCCCC")  # Subtle dividers
WHITE = colors.white
BG_LIGHT = colors.HexColor("#F5F7FA")  # Skills matrix row fill

# Typography sizes
NAME_SIZE = 22
SECTION_SIZE = 10
BODY_SIZE = 9.5
SMALL_SIZE = 8.5
DATE_SIZE = 8.5

# Spacing
SECTION_GAP = 16  # vertical space before section header
PARA_GAP = 6  # vertical space between paragraphs within a block
BULLET_GAP = 3  # vertical space between bullet lines
LINE_H = 14  # baseline skip for body

# ─── Styles ───────────────────────────────────────────────────────────────────

styles = getSampleStyleSheet()

name_style = ParagraphStyle(
    "Name",
    fontName="Helvetica-Bold",
    fontSize=NAME_SIZE,
    textColor=NAVY,
    spaceAfter=4,
    alignment=TA_CENTER,
    leading=NAME_SIZE + 4,
)

contact_style = ParagraphStyle(
    "Contact",
    fontName="Helvetica",
    fontSize=9,
    textColor=MID_GREY,
    spaceAfter=0,
    alignment=TA_CENTER,
    leading=13,
)

section_header_style = ParagraphStyle(
    "SectionHeader",
    fontName="Helvetica-Bold",
    fontSize=SECTION_SIZE,
    textColor=NAVY,
    spaceBefore=0,
    spaceAfter=6,
    leading=SECTION_SIZE + 4,
    letterSpacing=1.5,  # uppercase letterspacing effect
)

org_style = ParagraphStyle(
    "Org",
    fontName="Helvetica-Bold",
    fontSize=BODY_SIZE,
    textColor=CHARCOAL,
    spaceAfter=0,
    leading=BODY_SIZE + 2,
)

title_style = ParagraphStyle(
    "Title",
    fontName="Helvetica-BoldOblique",
    fontSize=BODY_SIZE,
    textColor=NAVY,
    spaceAfter=0,
    leading=BODY_SIZE + 2,
)

date_style = ParagraphStyle(
    "Date",
    fontName="Helvetica",
    fontSize=DATE_SIZE,
    textColor=LIGHT_GREY,
    spaceAfter=2,
    alignment=TA_LEFT,
    leading=DATE_SIZE + 2,
)

bullet_style = ParagraphStyle(
    "Bullet",
    fontName="Helvetica",
    fontSize=BODY_SIZE,
    textColor=CHARCOAL,
    spaceAfter=0,
    leading=BODY_SIZE + 3,
    leftIndent=12,
    bulletIndent=0,
)

sub_label_style = ParagraphStyle(
    "SubLabel",
    fontName="Helvetica-Bold",
    fontSize=SMALL_SIZE,
    textColor=MID_GREY,
    spaceAfter=2,
    leading=SMALL_SIZE + 2,
)

body_style = ParagraphStyle(
    "Body",
    fontName="Helvetica",
    fontSize=BODY_SIZE,
    textColor=CHARCOAL,
    spaceAfter=4,
    leading=BODY_SIZE + 3,
)

caption_style = ParagraphStyle(
    "Caption",
    fontName="Helvetica",
    fontSize=SMALL_SIZE,
    textColor=LIGHT_GREY,
    spaceAfter=4,
    leading=SMALL_SIZE + 2,
    alignment=TA_CENTER,
)

# ─── Helpers ─────────────────────────────────────────────────────────────────


def section_rule():
    return HRFlowable(
        width="100%", thickness=0.75, color=NAVY, spaceAfter=6, spaceBefore=0
    )


def thin_rule():
    return HRFlowable(
        width="100%", thickness=0.4, color=RULE_LIGHT, spaceAfter=4, spaceBefore=0
    )


def bullet(text):
    return Paragraph(f"<bullet>&bull;</bullet> {text}", bullet_style)


def sp(pt):
    return Spacer(1, pt)


# ─── Header Block ─────────────────────────────────────────────────────────────


def build_header():
    items = []
    items.append(Paragraph("KHALID WALEED ALMANIE", name_style))
    items.append(
        Paragraph(
            "+65 91337344  |  linkedin.com/in/khalid-waleed-sb82052193  |  almanie.s.2025@mba.smu.edu.sg  |  Singapore",
            contact_style,
        )
    )
    items.append(sp(2))
    items.append(
        HRFlowable(width="100%", thickness=1.0, color=NAVY, spaceAfter=0, spaceBefore=0)
    )
    return items


# ─── Section Scaffold ──────────────────────────────────────────────────────────


def section(title, content_flowables):
    return [
        sp(SECTION_GAP),
        Paragraph(title.upper(), section_header_style),
        section_rule(),
        *content_flowables,
    ]


# ─── Experience Entry ──────────────────────────────────────────────────────────


def experience_block(title_text, org, dates, bullets_list):
    """Title left, dates right on same visual line."""
    items = []
    # Title + Date row via table for alignment
    title_para = Paragraph(title_text, title_style)
    date_para = Paragraph(dates, date_style)

    row_table = Table(
        [[title_para, date_para]],
        colWidths=[CONTENT_W * 0.65, CONTENT_W * 0.35],
    )
    row_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    items.append(row_table)
    items.append(Paragraph(org, sub_label_style))
    items.append(sp(2))
    for b in bullets_list:
        items.append(bullet(b))
    return items


# ─── Projects Entry ───────────────────────────────────────────────────────────


def project_block(title, subtitle, tech, bullets_list):
    items = []
    title_row = Table(
        [[Paragraph(title, title_style), Paragraph(subtitle, date_style)]],
        colWidths=[CONTENT_W * 0.65, CONTENT_W * 0.35],
    )
    title_row.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    items.append(title_row)
    items.append(Paragraph(f"<i>Tech:</i> {tech}", body_style))
    items.append(sp(2))
    for b in bullets_list:
        items.append(bullet(b))
    return items


# ─── Skills Matrix ────────────────────────────────────────────────────────────


def skills_matrix():
    categories = [
        (
            "Fintech & Finance",
            [
                "Yield Accrual Engineering",
                "Treasury Reserve Management",
                "DCF / LBO Modeling",
                "Regulatory Reporting (1099-INT)",
                "Basis Points Economics",
                "Capital Structure Analysis",
                "Portfolio Management",
                "EBITDA Normalization",
                "M&A Fundamentals",
                "Comparable Co. Analysis",
            ],
        ),
        (
            "Technical",
            [
                "Python",
                "FastAPI",
                "Next.js / React",
                "REST API Design",
                "PostgreSQL",
                "AWS (EC2, S3, RDS)",
                "pandas / NumPy",
                "scikit-learn",
                "Data Visualization",
                "Git / Version Control",
            ],
        ),
        (
            "Operations",
            [
                "Supply Chain Optimization",
                "Risk Management",
                "ESG Analysis",
                "Go-to-Market Strategy",
                "Stakeholder Management",
                "Cross-cultural Leadership",
                "Performance Auditing",
                "Project Management",
                "Strategic Planning",
                "Process Improvement",
            ],
        ),
        (
            "Regulatory & Compliance",
            [
                "Sponsor Bank Model",
                "FDIC Insurance Framework",
                "MiCA / EMI (EU)",
                "AML / KYC Protocols",
                "BSA / FinCEN Compliance",
                "State MTL Licensing",
                "Unclaimed Property Laws",
                "OFAC Screening",
                "CUSO Structure",
                "SR 11-7 Model Governance",
            ],
        ),
        (
            "Languages",
            [
                "Arabic (Native)",
                "English (Professional)",
                "Mandarin (Conversational)",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
        ),
    ]

    # Calculate column widths — 5 columns
    col_w = CONTENT_W / 5

    header_row = [
        Paragraph(
            "<b>Fintech & Finance</b>",
            ParagraphStyle(
                "sh",
                fontName="Helvetica-Bold",
                fontSize=SMALL_SIZE,
                textColor=NAVY,
                leading=SMALL_SIZE + 2,
            ),
        ),
        Paragraph(
            "<b>Technical</b>",
            ParagraphStyle(
                "sh",
                fontName="Helvetica-Bold",
                fontSize=SMALL_SIZE,
                textColor=NAVY,
                leading=SMALL_SIZE + 2,
            ),
        ),
        Paragraph(
            "<b>Operations</b>",
            ParagraphStyle(
                "sh",
                fontName="Helvetica-Bold",
                fontSize=SMALL_SIZE,
                textColor=NAVY,
                leading=SMALL_SIZE + 2,
            ),
        ),
        Paragraph(
            "<b>Regulatory & Compliance</b>",
            ParagraphStyle(
                "sh",
                fontName="Helvetica-Bold",
                fontSize=SMALL_SIZE,
                textColor=NAVY,
                leading=SMALL_SIZE + 2,
            ),
        ),
        Paragraph(
            "<b>Languages</b>",
            ParagraphStyle(
                "sh",
                fontName="Helvetica-Bold",
                fontSize=SMALL_SIZE,
                textColor=NAVY,
                leading=SMALL_SIZE + 2,
            ),
        ),
    ]

    max_rows = max(len(items) for _, items in categories)
    data_rows = []
    for i in range(max_rows):
        row = []
        for _, items in categories:
            if i < len(items):
                row.append(
                    Paragraph(
                        items[i],
                        ParagraphStyle(
                            "si",
                            fontName="Helvetica",
                            fontSize=SMALL_SIZE,
                            textColor=CHARCOAL,
                            leading=SMALL_SIZE + 3,
                            spaceAfter=0,
                        ),
                    )
                )
            else:
                row.append(Paragraph("", body_style))
        data_rows.append(row)

    all_data = [header_row] + data_rows

    tbl = Table(
        all_data,
        colWidths=[col_w] * 5,
        repeatRows=1,
    )

    tbl.setStyle(
        TableStyle(
            [
                # Header row
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF2F7")),
                ("TOPPADDING", (0, 0), (-1, 0), 5),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                # Alternating rows for readability
                *[
                    ("BACKGROUND", (0, i), (-1, i), BG_LIGHT if i % 2 == 1 else WHITE)
                    for i in range(1, len(all_data))
                ],
                # Grid lines
                ("GRID", (0, 0), (-1, -1), 0.4, RULE_LIGHT),
                ("LINEBELOW", (0, 0), (-1, 0), 0.75, NAVY),
            ]
        )
    )

    return tbl


# ─── Build Story ───────────────────────────────────────────────────────────────


def build_story():
    story = []
    story += build_header()

    # ── Experience ────────────────────────────────────────────────────────────
    story += section(
        "Experience",
        [
            *experience_block(
                "Logistics Operations Team Leader",
                "JollyChic  |  China HQ; Saudi Arabia ops  |  Sep 2019 – Nov 2020",
                "Sep 2019 – Nov 2020",
                [
                    "Directed a team of 40+ staff across logistics and last-mile delivery operations for Saudi Arabia in a high-volume cross-border e-commerce environment, achieving 100% on-time delivery across all shifts and serving over 100,000 customers in the Saudi market",
                    "Redesigned end-to-end shift scheduling workflows using demand forecasting analysis, eliminating coverage gaps and increasing daily throughput by 25%, reducing order processing time from 48 hours to under 24 hours",
                    "Resolved on-site operational disruptions in real time, including customs clearance delays and last-mile delivery exceptions, maintaining uninterrupted workflows across multiple concurrent shifts",
                    "Managed logistics vendor relationships and negotiated carrier contracts, achieving a 15% reduction in per-shipment delivery costs while maintaining SLA compliance",
                    "Implemented performance tracking dashboards monitoring on-time delivery rate, order accuracy, and exception rates; conducted root-cause analysis on failed deliveries and drove corrective action plans to closure",
                    "Coordinated cross-functional alignment between warehouse, transportation, and customer service teams to ensure seamless order fulfillment from Guangzhou hub to Saudi Arabian doorsteps",
                ],
            ),
            sp(PARA_GAP),
            *experience_block(
                "Assistant Project Manager",
                "Expert Path  |  Riyadh, KSA  |  Apr 2021 – Feb 2022",
                "Apr 2021 – Feb 2022",
                [
                    "Executed a comprehensive performance audit of National Water Company (NWC) distillation and treatment stations across Saudi Arabia, identifying critical operational inefficiencies, compliance gaps, and capital expenditure optimization opportunities worth an estimated SAR 2.4M in recoverable costs",
                    "Managed the full project lifecycle including scope definition, timeline management, billing, and cross-functional stakeholder communications; interviewed and shortlisted 100+ candidates for project team roles and coordinated onboarding logistics",
                    "Facilitated alignment between Riyadh Municipality, the Chamber of Commerce, engineering firms, and legal teams to execute a city-wide commercial shop compliance restructuring program, achieving 100% stakeholder sign-off and on-schedule delivery",
                    "Developed compliance documentation frameworks and audit protocols meeting Saudi Arabian regulatory standards (SASO, SCA), resulting in zero non-compliance findings during subsequent governmental inspections",
                    "Prepared executive-level status reports and presentation materials for senior government officials, translating technical audit findings into actionable strategic recommendations for operational improvement",
                ],
            ),
        ],
    )

    # ── Projects ──────────────────────────────────────────────────────────────
    story += section(
        "Projects",
        [
            *project_block(
                "B2B Yield-Bearing Payment Infrastructure",
                "Independent Research  |  2026",
                "Python, FastAPI, Next.js, React, REST APIs, AWS, PostgreSQL",
                [
                    "Developed a B2B platform enabling banks and fintechs to offer interest-bearing payment accounts through Treasury reserve yield pass-through, targeting the $50-80B annual US float income market",
                    "Built yield calculation engine in Python with daily accrual (balance × rate × 1/365), reconciliation divergence tracking, and tiered basis-points economics for 3 partner tiers (75/65/50 bps)",
                    "Implemented 8 REST API endpoints in FastAPI for account management, yield balances, dispute tracking, alerts, rate discrepancy monitoring, portfolio forecasting, and regulatory reporting (IRS 1099-INT, state unclaimed property)",
                    "Designed US Sponsor Bank regulatory pathway (3-6 months, $50-200K/year cost) and EU EMI Partnership with 27-state MiCA passporting; analyzed FDIC insurance implications and state-by-state MTL requirements",
                    "Quantified the reconciliation gap: FloatYield's simple interest (/365) vs Treasury's actual/actual accrual at ~90 bps/year on a $1B deposit book, equivalent to ~$900K in annual divergence",
                    "Conducted unit economics red team: Year 3 scenario at 50 bps on $1.5B average daily balance yields $7.5M revenue, $1.35M reconciliation liability, and a 5.6× coverage ratio",
                    "Identified and documented capital sequencing risk: ILC charter formation requires 18-24 months while Year 1 revenue runway is insufficient without bridge financing",
                    "Produced 12-slide HTML pitch deck and comprehensive FloatYield_Report.md covering TAM/SAM/SOM analysis, regulatory framework, competitive landscape, and go-to-market strategy",
                ],
            ),
        ],
    )

    # ── International Experience ───────────────────────────────────────────────
    story += section(
        "International Experience",
        [
            # Entry 1
            Table(
                [
                    [
                        Paragraph("CUFE Week Exchange — Beijing, China", title_style),
                        Paragraph("Mar 2026", date_style),
                    ]
                ],
                colWidths=[CONTENT_W * 0.72, CONTENT_W * 0.28],
            ),
            Paragraph("Singapore Management University", sub_label_style),
            sp(2),
            bullet(
                "Analyzed China's AI landscape via site visits to iFLYTEK, Haidian Science City, and Meituan 'Super Brain'; evaluated wearable AI market entry strategy for Western brands in China"
            ),
            sp(PARA_GAP),
            # Entry 2
            Table(
                [
                    [
                        Paragraph(
                            "Overseas Immersion Programme — Bangkok, Thailand",
                            title_style,
                        ),
                        Paragraph("Oct 2025", date_style),
                    ]
                ],
                colWidths=[CONTENT_W * 0.72, CONTENT_W * 0.28],
            ),
            Paragraph("ESG & Community Stewardship Focus", sub_label_style),
            sp(2),
            bullet(
                "Conducted field research on mangrove conservation in Bang Tabun district; developed community ESG stewardship framework for coastal resilience; evaluated DTGO's Forestias megaproject"
            ),
        ],
    )

    # ── Education ──────────────────────────────────────────────────────────────
    story += section(
        "Education",
        [
            Table(
                [
                    [
                        Paragraph(
                            "Master of Business Administration — Finance Track",
                            title_style,
                        ),
                        Paragraph("Aug 2026 – Present", date_style),
                    ]
                ],
                colWidths=[CONTENT_W * 0.65, CONTENT_W * 0.35],
            ),
            Paragraph("Singapore Management University", sub_label_style),
            sp(PARA_GAP),
            Table(
                [
                    [
                        Paragraph(
                            "Bachelor of Arts — English Language and Translation",
                            title_style,
                        ),
                        Paragraph("Apr 2014 – Dec 2018", date_style),
                    ]
                ],
                colWidths=[CONTENT_W * 0.65, CONTENT_W * 0.35],
            ),
            Paragraph("Qassim University, Saudi Arabia", sub_label_style),
        ],
    )

    # ── Skills ─────────────────────────────────────────────────────────────────
    story += section("Skills", [skills_matrix()])

    return story


# ─── Main ─────────────────────────────────────────────────────────────────────


def main():
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "Khalid_Waleed_Almanie_Resume.pdf"
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title="Khalid Waleed Almanie — Resume",
        author="Khalid Waleed Almanie",
        subject="MBA Finance Candidate Resume",
    )

    doc.build(build_story())
    print(f"PDF generated: {output_path}")


if __name__ == "__main__":
    main()
