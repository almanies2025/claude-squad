#!/usr/bin/env python3
"""Generate updated CV for Almanie K — FloatYield version"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# Create PDF
output_path = "/mnt/c/Users/User/Documents/GitHub/claude-squad/cv-Almanie-K.pdf"
doc = SimpleDocTemplate(
    output_path,
    pagesize=A4,
    leftMargin=2 * cm,
    rightMargin=2 * cm,
    topMargin=2 * cm,
    bottomMargin=2 * cm,
)

# Styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    "Title",
    parent=styles["Heading1"],
    fontSize=18,
    spaceAfter=4,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#1a1a2e"),
)
contact_style = ParagraphStyle(
    "Contact",
    parent=styles["Normal"],
    fontSize=10,
    alignment=TA_CENTER,
    spaceAfter=16,
    textColor=colors.HexColor("#444"),
)
section_style = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontSize=12,
    spaceBefore=14,
    spaceAfter=6,
    textColor=colors.HexColor("#1a1a2e"),
    borderPadding=(0, 0, 2, 0),
)
subsection_style = ParagraphStyle(
    "Subsection",
    parent=styles["Heading3"],
    fontSize=11,
    spaceBefore=8,
    spaceAfter=2,
    textColor=colors.HexColor("#333"),
)
body_style = ParagraphStyle(
    "Body", parent=styles["Normal"], fontSize=10, spaceAfter=4, leading=14
)
bullet_style = ParagraphStyle(
    "Bullet",
    parent=styles["Normal"],
    fontSize=10,
    spaceAfter=3,
    leading=13,
    leftIndent=12,
    bulletIndent=0,
)

# Build content
story = []

# Name
story.append(Paragraph("ALMANIE K", title_style))
story.append(
    Paragraph(
        "+1 469 000 0000  |  almanie.k@example.com  |  linkedin.com/in/almanie  |  Dallas, TX",
        contact_style,
    )
)

# Skills Section
story.append(Paragraph("SKILLS", section_style))
skills_data = [
    ["Languages:", "Python, JavaScript, TypeScript, SQL, HTML/CSS"],
    ["Frameworks:", "FastAPI, Next.js, React, Node.js, Express"],
    ["Tools & Platforms:", "Git, REST APIs, JSON, AWS, FedNow, PostgreSQL"],
    ["Libraries:", "Pandas, NumPy, Scikit-learn, ReportLab"],
]
for row in skills_data:
    story.append(Paragraph(f"<b>{row[0]}</b> {row[1]}", body_style))

# Education
story.append(Spacer(1, 6))
story.append(Paragraph("EDUCATION", section_style))
story.append(
    Paragraph(
        "<b>Singapore Management University</b> — BS Information Systems | Expected 2026",
        body_style,
    )
)

# Projects
story.append(Spacer(1, 6))
story.append(Paragraph("PROJECTS", section_style))

# Project 1: FloatYield
story.append(Paragraph("B2B Yield-Bearing Payment Infrastructure", subsection_style))
story.append(
    Paragraph("Python · FastAPI · Next.js · React · REST APIs · AWS", body_style)
)

bullets_fy = [
    "Developed a B2B platform enabling banks and fintechs to offer interest-bearing payment accounts through Treasury reserve yield pass-through",
    "Built yield calculation engine in Python with daily accrual, reconciliation divergence tracking, and tiered bps economics",
    "Implemented 8 REST API endpoints in FastAPI for account management, yield balances, dispute tracking, alerts, rate discrepancy monitoring, portfolio forecasting, and regulatory reporting (1099-INT, unclaimed property)",
    "Designed US Sponsor Bank regulatory pathway (3-6 months, $50-200K/year) and EU EMI Partnership with 27-state MiCA passporting",
    "Quantified reconciliation gap: FloatYield's simple interest (/365) vs Treasury's actual/actual accrual at ~90 bps/year on $1B deposit book",
    "Conducted unit economics red team: Year 3 at 50 bps on $1.5B ADB yields $7.5M revenue, $1.35M reconciliation liability, 5.6× coverage ratio",
    "Identified capital sequencing risk: ILC charter requires 18-24 months vs Year 1 revenue runway gap",
    "Produced 12-slide HTML pitch deck and FloatYield_Report.md covering market analysis, regulatory framework, and go-to-market strategy",
]
for b in bullets_fy:
    story.append(Paragraph(f"• {b}", bullet_style))

story.append(Spacer(1, 8))

# Project 2: Travel Aggregator
story.append(Paragraph("Travel Aggregator", subsection_style))
story.append(Paragraph("Python · REST APIs · JSON", body_style))
story.append(
    Paragraph(
        "• Built a travel deal aggregation tool that scrapes and filters flight and hotel offers from multiple OTAs",
        bullet_style,
    )
)

story.append(Spacer(1, 8))

# Project 3: Employee Directory
story.append(Paragraph("Employee Directory", subsection_style))
story.append(Paragraph("React · Node.js", body_style))
story.append(
    Paragraph(
        "• Developed an interactive employee directory with search and filtering capabilities",
        bullet_style,
    )
)

story.append(Spacer(1, 8))

# Project 4: Property Management
story.append(Paragraph("Property Management", subsection_style))
story.append(Paragraph("SQL · JavaScript", body_style))
story.append(
    Paragraph(
        "• Built a property management system with tenant tracking and lease management features",
        bullet_style,
    )
)

# Build PDF
doc.build(story)
print(f"CV generated: {output_path}")
