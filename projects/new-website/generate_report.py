#!/usr/bin/env python3
"""
Generate the Website Modernization & Account Centralization report PDF.
Run: python3 projects/new-website/generate_report.py
Output: projects/new-website/greenmark-website-modernization-report.pdf
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether, ListFlowable, ListItem
)
from reportlab.pdfgen import canvas as pdfcanvas


# ── Brand Colors ──────────────────────────────────────────────────────────────
GREENMARK_GREEN = colors.HexColor("#2D6A4F")
GREENMARK_DARK  = colors.HexColor("#1B4332")
GREENMARK_LIGHT = colors.HexColor("#D8F3DC")
GREENMARK_ACCENT = colors.HexColor("#40916C")
HEADER_BG       = colors.HexColor("#2D6A4F")
ROW_ALT         = colors.HexColor("#F0FAF4")
TEXT_DARK       = colors.HexColor("#1A1A2E")
TEXT_MED        = colors.HexColor("#444444")
TEXT_LIGHT      = colors.HexColor("#666666")
RISK_RED        = colors.HexColor("#D62828")
RISK_AMBER      = colors.HexColor("#F77F00")
RISK_GREEN      = colors.HexColor("#2D6A4F")
SCORE_BAD       = colors.HexColor("#D62828")
SCORE_GOOD      = colors.HexColor("#2D6A4F")
WHITE           = colors.white
LIGHT_GRAY      = colors.HexColor("#F5F5F5")
BORDER_GRAY     = colors.HexColor("#CCCCCC")


# ── Custom Page Templates ─────────────────────────────────────────────────────

def cover_page(canvas, doc):
    """Draw the cover page background and branding."""
    canvas.saveState()
    w, h = letter

    # Full green header block (top 45%)
    canvas.setFillColor(GREENMARK_DARK)
    canvas.rect(0, h * 0.55, w, h * 0.45, fill=1, stroke=0)

    # Accent stripe
    canvas.setFillColor(GREENMARK_ACCENT)
    canvas.rect(0, h * 0.55, w, 4, fill=1, stroke=0)

    # Footer line
    canvas.setFillColor(BORDER_GRAY)
    canvas.rect(0.75 * inch, 0.75 * inch, w - 1.5 * inch, 0.5, fill=1, stroke=0)

    canvas.restoreState()


def later_pages(canvas, doc):
    """Header + footer for body pages."""
    canvas.saveState()
    w, h = letter

    # Header bar
    canvas.setFillColor(GREENMARK_GREEN)
    canvas.rect(0, h - 36, w, 36, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(0.75 * inch, h - 24, "GREENMARK WASTE SOLUTIONS")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - 0.75 * inch, h - 24, "Website Modernization & Account Centralization")

    # Footer
    canvas.setFillColor(BORDER_GRAY)
    canvas.rect(0.75 * inch, 0.6 * inch, w - 1.5 * inch, 0.5, fill=1, stroke=0)
    canvas.setFillColor(TEXT_LIGHT)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(0.75 * inch, 0.4 * inch, "CONFIDENTIAL  |  Prepared by AIC Holdings for Greenmark Waste Solutions")
    canvas.drawRightString(w - 0.75 * inch, 0.4 * inch, f"Page {doc.page}")

    canvas.restoreState()


# ── Style Definitions ─────────────────────────────────────────────────────────

def build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=32,
        leading=38,
        textColor=WHITE,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="CoverSubtitle",
        fontName="Helvetica",
        fontSize=16,
        leading=22,
        textColor=colors.HexColor("#B7E4C7"),
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="CoverMeta",
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        textColor=TEXT_MED,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=26,
        textColor=GREENMARK_DARK,
        spaceBefore=24,
        spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        name="SubsectionTitle",
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=GREENMARK_GREEN,
        spaceBefore=16,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="BodyText2",
        fontName="Helvetica",
        fontSize=10,
        leading=14.5,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY,
        spaceBefore=4,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="BodyBold",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14.5,
        textColor=TEXT_DARK,
        spaceBefore=4,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="Callout",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=GREENMARK_DARK,
        backColor=GREENMARK_LIGHT,
        borderColor=GREENMARK_GREEN,
        borderWidth=1,
        borderPadding=8,
        spaceBefore=8,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="BulletBody",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=TEXT_DARK,
        leftIndent=18,
        bulletIndent=6,
        spaceBefore=2,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="TableHeader",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=WHITE,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="TableCell",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=TEXT_DARK,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=TEXT_DARK,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="FootnoteStyle",
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=TEXT_LIGHT,
        spaceBefore=2,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="MetricBig",
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=32,
        textColor=GREENMARK_GREEN,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="MetricLabel",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=TEXT_LIGHT,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="QuestionStyle",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=GREENMARK_DARK,
        spaceBefore=8,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="AnswerStyle",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_MED,
        leftIndent=12,
        spaceBefore=0,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
    ))
    return styles


# ── Helper Functions ──────────────────────────────────────────────────────────

def green_hr():
    return HRFlowable(width="100%", thickness=1, color=GREENMARK_GREEN, spaceBefore=6, spaceAfter=6)

def gray_hr():
    return HRFlowable(width="100%", thickness=0.5, color=BORDER_GRAY, spaceBefore=4, spaceAfter=4)

def bullet(text, styles):
    return Paragraph(f"\u2022  {text}", styles["BulletBody"])

def styled_table(data, col_widths, styles):
    """Create a consistently styled table with green header."""
    header_row = [Paragraph(str(c), styles["TableHeader"]) for c in data[0]]
    body_rows = []
    for row in data[1:]:
        body_rows.append([Paragraph(str(c), styles["TableCell"]) for c in row])

    t = Table([header_row] + body_rows, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, ROW_ALT]),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t


def metric_box(value, label, color, styles):
    """Single metric card for the scorecard row."""
    data = [
        [Paragraph(str(value), ParagraphStyle("m", parent=styles["MetricBig"], textColor=color))],
        [Paragraph(label, styles["MetricLabel"])],
    ]
    t = Table(data, colWidths=[1.6 * inch])
    t.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 1, color),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
    ]))
    return t


def qa_block(num, question, answer, styles):
    """Q&A pair."""
    return KeepTogether([
        Paragraph(f"{num}. \u201c{question}\u201d", styles["QuestionStyle"]),
        Paragraph(answer, styles["AnswerStyle"]),
    ])


# ── Build the Document ────────────────────────────────────────────────────────

def build_report():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "greenmark-website-modernization-report.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )

    styles = build_styles()
    story = []
    W = doc.width  # usable width

    # ══════════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ══════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 2.2 * inch))
    story.append(Paragraph("Website Modernization<br/>&amp; Account Centralization", styles["CoverTitle"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("greenmarkwaste.com  |  htdisposal.com", styles["CoverSubtitle"]))
    story.append(Spacer(1, 2.4 * inch))

    cover_meta = [
        ["Prepared for", "Greenmark Waste Solutions"],
        ["Prepared by", "AIC Holdings \u2014 Technology Division"],
        ["Lead", "Daniel Shanklin, Director of AI & Technology"],
        ["Date", datetime.now().strftime("%B %d, %Y")],
        ["Classification", "CONFIDENTIAL"],
    ]
    meta_table = Table(
        [[Paragraph(r[0], ParagraphStyle("ml", parent=styles["CoverMeta"], textColor=TEXT_LIGHT)),
          Paragraph(r[1], ParagraphStyle("mr", parent=styles["CoverMeta"], fontName="Helvetica-Bold"))]
         for r in cover_meta],
        colWidths=[1.8 * inch, 4 * inch],
    )
    meta_table.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(meta_table)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Table of Contents", styles["SectionTitle"]))
    story.append(green_hr())
    toc_items = [
        ("1", "Executive Summary"),
        ("2", "Current State Assessment"),
        ("3", "Performance Scorecard"),
        ("4", "The Plan: What We\u2019re Doing and Why"),
        ("5", "Execution Sequence: The Critical Path"),
        ("6", "Account Transfer Checklists"),
        ("7", "Cost Analysis & ROI"),
        ("8", "Risk Assessment & Mitigations"),
        ("9", "Stakeholder FAQ (25 Questions Answered)"),
        ("10", "Discovery Questions for Michael"),
        ("11", "Draft Email to Michael"),
        ("12", "Next Steps"),
    ]
    for num, title in toc_items:
        story.append(Paragraph(
            f'<b>{num}.</b>&nbsp;&nbsp;&nbsp;{title}',
            ParagraphStyle("toc", parent=styles["BodyText2"], fontSize=11, leading=20, spaceBefore=2, spaceAfter=2)
        ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 1. EXECUTIVE SUMMARY
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("1. Executive Summary", styles["SectionTitle"]))
    story.append(green_hr())
    story.append(Paragraph(
        "Greenmark Waste Solutions operates two customer-facing websites\u2014greenmarkwaste.com and htdisposal.com\u2014"
        "both built on Webflow and registered through GoDaddy. When these sites were built, Webflow was a solid choice: "
        "good-looking design, fast to launch, no developers required. The people who built it made a reasonable decision "
        "with the tools available at the time.",
        styles["BodyText2"]
    ))
    story.append(Paragraph(
        "Two things have changed since then. First, <b>Google got stricter about mobile speed.</b> Mobile page speed is now "
        "a direct ranking factor, and Google actively penalizes sites that load slowly on phones. Greenmark\u2019s Webflow site "
        "scores <b>47 out of 100</b> on Google\u2019s mobile test, with a <b>17.5-second load time</b>\u2014well into the "
        "\u201cPoor\u201d category. This isn\u2019t a configuration issue; it\u2019s a limitation of how Webflow generates pages. "
        "There is no setting to flip to fix it.",
        styles["BodyText2"]
    ))
    story.append(Paragraph(
        "Second, <b>AI tools changed what a small team can build without an agency.</b> We used AI to rebuild the homepage "
        "on a modern framework (Astro), and the same design now scores <b>92/100 on mobile</b> with a <b>2.7-second load time</b>. "
        "It runs on Railway\u2014same infrastructure as Cerebro\u2014at zero incremental hosting cost. What used to require "
        "a web designer and months of back-and-forth, AI tools can now do in days.",
        styles["BodyText2"]
    ))
    story.append(Paragraph(
        "Separately, we have an account ownership gap: we do not know who controls the GoDaddy account or the Webflow workspace. "
        "Per the policy Alex Kaye approved on Feb 27, these need to be centralized under it@greenmarkwaste.com\u2014"
        "same pattern we already completed for Railway, Supabase, and GitHub.",
        styles["BodyText2"]
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph("This report covers three workstreams:", styles["BodyBold"]))
    story.append(bullet("<b>Account Centralization</b> \u2014 Transfer GoDaddy and Webflow accounts to "
                        "it@greenmarkwaste.com, closing a security gap.", styles))
    story.append(bullet("<b>DNS Modernization</b> \u2014 Add Cloudflare as a DNS/CDN layer between GoDaddy and "
                        "hosting, enabling instant cutover and rollback.", styles))
    story.append(bullet("<b>Website Replacement</b> \u2014 Complete the Astro build, cut over DNS, and wind down "
                        "Webflow once the new site is stable\u2014reducing subscription cost and agency dependency.", styles))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "The net result: faster site, better search rankings, lower cost, full Greenmark ownership of all accounts, "
        "and a site that Greenmark\u2019s team can maintain going forward\u2014with or without AIC.",
        styles["Callout"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 2. CURRENT STATE ASSESSMENT
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("2. Current State Assessment", styles["SectionTitle"]))
    story.append(green_hr())

    story.append(Paragraph("Domain & Hosting", styles["SubsectionTitle"]))
    state_data = [
        ["Asset", "Platform", "Owner", "Status"],
        ["greenmarkwaste.com (domain)", "GoDaddy", "Unknown", "Expires Aug 1, 2026 \u2014 5 months"],
        ["greenmarkwaste.com (site)", "Webflow", "Unknown (Daniel has editor access)", "Live \u2014 mobile score 47/100"],
        ["htdisposal.com (domain)", "Likely GoDaddy", "Unknown", "Needs confirmation"],
        ["htdisposal.com (site)", "Likely Webflow", "Unknown", "Needs confirmation"],
        ["Astro replacement", "Railway", "it@greenmarkwaste.com", "Homepage deployed, remaining pages needed"],
        ["DNS management", "GoDaddy (default)", "Unknown", "No Cloudflare layer yet"],
    ]
    story.append(styled_table(state_data, [1.8*inch, 1.1*inch, 2.1*inch, 2*inch], styles))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Account Ownership Gaps", styles["SubsectionTitle"]))
    story.append(Paragraph(
        "Per the account ownership policy (approved by Alex Kaye, Feb 27, 2026), every vendor account should be "
        "owned by <b>it@greenmarkwaste.com</b> with billing to <b>accounting@greenmarkwaste.com</b>. "
        "We have already completed this for Railway, Supabase, and GitHub (Tasks 78\u201381). "
        "GoDaddy and Webflow are the remaining gaps.",
        styles["BodyText2"]
    ))

    gap_data = [
        ["Vendor", "Current Owner", "Target Owner", "Billing Target", "Status"],
        ["Railway", "\u2014", "it@greenmarkwaste.com", "accounting@", "\u2713 Done"],
        ["Supabase", "\u2014", "it@greenmarkwaste.com", "accounting@", "\u2713 Done"],
        ["GitHub", "\u2014", "it@greenmarkwaste.com", "accounting@", "\u2713 Done"],
        ["GoDaddy", "Unknown", "it@greenmarkwaste.com", "accounting@", "\u2717 Not started"],
        ["Webflow", "Unknown", "it@greenmarkwaste.com", "accounting@", "\u2717 Not started"],
        ["Cloudflare", "N/A (new)", "it@greenmarkwaste.com", "accounting@", "\u2717 Not started"],
    ]
    story.append(styled_table(gap_data, [1.1*inch, 1.2*inch, 1.6*inch, 1.2*inch, 0.9*inch], styles))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 3. PERFORMANCE SCORECARD
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("3. Performance Scorecard", styles["SectionTitle"]))
    story.append(green_hr())
    story.append(Paragraph(
        "Google\u2019s PageSpeed Insights measures real-world user experience. Scores below 50 are rated \u201cPoor\u201d "
        "and trigger ranking penalties. The Webflow site fails on mobile\u2014the majority of search traffic.",
        styles["BodyText2"]
    ))
    story.append(Spacer(1, 12))

    # Before / After comparison
    perf_data = [
        ["Metric", "Webflow (Current)", "Astro (Replacement)", "Improvement"],
        ["Mobile Speed Score", "47 / 100 (Poor)", "92 / 100 (Good)", "+96%"],
        ["Desktop Speed Score", "~70 / 100", "99 / 100", "+41%"],
        ["Largest Contentful Paint (LCP)", "17.5 seconds", "2.7 seconds", "6.5x faster"],
        ["Cumulative Layout Shift (CLS)", "Unknown (high)", "0.001 (excellent)", "\u2014"],
        ["Total Blocking Time (TBT)", "Unknown", "0 ms (perfect)", "\u2014"],
        ["Google Ranking Impact", "Penalized (slow mobile)", "Rewarded (fast mobile)", "Direct SEO benefit"],
    ]
    story.append(styled_table(perf_data, [1.8*inch, 1.5*inch, 1.5*inch, 1.2*inch], styles))

    story.append(Spacer(1, 12))

    # Metric boxes row
    m1 = metric_box("47", "Webflow Mobile", SCORE_BAD, styles)
    m2 = metric_box("\u2192", "", TEXT_LIGHT, styles)
    m3 = metric_box("92", "Astro Mobile", SCORE_GOOD, styles)
    m4 = metric_box("2.7s", "New LCP", SCORE_GOOD, styles)

    metrics_row = Table([[m1, m2, m3, m4]], colWidths=[1.75*inch, 0.6*inch, 1.75*inch, 1.75*inch])
    metrics_row.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(metrics_row)

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>What this means in plain English:</b> When someone searches \u201cwaste services Dallas\u201d on their phone, "
        "Google measures how fast each result\u2019s website loads. Greenmark\u2019s current site takes 17 seconds\u2014"
        "most visitors leave after 3. The new site loads in under 3 seconds. This wasn\u2019t fixable when the site was "
        "first built\u2014AI tools made it possible to rebuild at this performance level without a web agency.",
        styles["Callout"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 4. THE PLAN
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("4. The Plan: What We\u2019re Doing and Why", styles["SectionTitle"]))
    story.append(green_hr())

    story.append(Paragraph("Three Workstreams, One Goal", styles["SubsectionTitle"]))
    story.append(Paragraph(
        "Everything in this plan serves a single objective: Greenmark owns and controls its own web presence, "
        "with no unknown account holders, a clear path to self-service, and the best possible performance for customer acquisition.",
        styles["BodyText2"]
    ))
    story.append(Spacer(1, 6))

    ws_data = [
        ["#", "Workstream", "What", "Why"],
        ["1", "Account Centralization",
         "Transfer GoDaddy + Webflow accounts to it@greenmarkwaste.com",
         "Security: unknown owners = unknown risk. Compliance with approved ownership policy."],
        ["2", "DNS Modernization",
         "Add Cloudflare between registrar and hosting",
         "Enables zero-downtime cutover, instant rollback, free CDN/SSL. Industry standard practice."],
        ["3", "Website Replacement",
         "Complete Astro build, cut DNS, cancel Webflow",
         "Fix mobile speed (47\u219292), eliminate subscription, remove agency dependency, full SEO control."],
    ]
    story.append(styled_table(ws_data, [0.35*inch, 1.5*inch, 2.3*inch, 2.6*inch], styles))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Why the Goalposts Moved", styles["SubsectionTitle"]))
    story.append(Paragraph(
        "Webflow was a reasonable choice when the site was built. Two shifts made it obsolete for Greenmark\u2019s needs:",
        styles["BodyText2"]
    ))
    story.append(bullet("<b>Google raised the bar on mobile speed.</b> Sites that load slowly on phones are now "
                        "directly penalized in search rankings. Webflow\u2019s generated code can\u2019t meet the new threshold.", styles))
    story.append(bullet("<b>AI tools eliminated the need for a web agency.</b> Building and maintaining a high-performance "
                        "site used to require a designer and a developer. AI can now do both\u2014faster, at lower cost, "
                        "with better results.", styles))
    story.append(Spacer(1, 6))
    why_data = [
        ["Factor", "Webflow (then)", "Astro + AI (now)"],
        ["Mobile speed", "47/100 \u2014 Google penalty", "92/100 \u2014 Google reward"],
        ["Page load time", "17.5 seconds", "2.7 seconds"],
        ["Monthly cost", "$14\u2013$39/site (subscription)", "$0 incremental (Railway already paid)"],
        ["Who can edit", "Hired designer or agency", "Team + AI tools \u2014 or future marketing hire"],
        ["SEO control", "Limited \u2014 Webflow generates HTML", "Full \u2014 every tag, schema, and markup"],
        ["Vendor lock-in", "Content trapped in Webflow CMS", "Zero \u2014 standard HTML/CSS/JS files"],
        ["AI/AIO readiness", "Cannot customize for AI search", "Full structured data, JSON-LD, semantic HTML"],
        ["Self-service path", "Always needs Webflow subscription", "Can add a simple CMS for non-technical editors"],
    ]
    story.append(styled_table(why_data, [1.3*inch, 2.5*inch, 2.9*inch], styles))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 5. EXECUTION SEQUENCE
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("5. Execution Sequence: The Critical Path", styles["SectionTitle"]))
    story.append(green_hr())
    story.append(Paragraph(
        "This is the order of operations. Each phase depends on the previous one. "
        "We can\u2019t skip ahead, and we shouldn\u2019t try to do everything at once.",
        styles["BodyText2"]
    ))
    story.append(Spacer(1, 8))

    # Phase 1
    story.append(Paragraph("Phase 1: Discovery &amp; Access (Week 1\u20132)", styles["SubsectionTitle"]))
    story.append(Paragraph("Goal: Know who owns what. Get admin access to everything.", styles["BodyBold"]))
    p1_data = [
        ["#", "Action", "Owner", "Blocker"],
        ["1.1", "Send discovery email to Michael (questions about GoDaddy, Webflow, designer)", "Daniel", "None \u2014 ready now"],
        ["1.2", "Michael identifies GoDaddy account owner", "Michael", "Waiting on email response"],
        ["1.3", "Michael identifies Webflow workspace owner", "Michael", "Waiting on email response"],
        ["1.4", "Get Daniel added as admin on GoDaddy", "Michael / current owner", "Step 1.2"],
        ["1.5", "Verify domain auto-renewal is ON (expires Aug 2026)", "Daniel", "Step 1.4"],
        ["1.6", "Document Webflow plan tier, cost, and access list", "Daniel", "Step 1.3"],
    ]
    story.append(styled_table(p1_data, [0.4*inch, 3.3*inch, 1.2*inch, 1.8*inch], styles))

    story.append(Spacer(1, 12))
    # Phase 2
    story.append(Paragraph("Phase 2: Account Centralization (Week 2\u20133)", styles["SubsectionTitle"]))
    story.append(Paragraph("Goal: All accounts owned by it@greenmarkwaste.com. Billing to accounting@.", styles["BodyBold"]))
    p2_data = [
        ["#", "Action", "Owner", "Blocker"],
        ["2.1", "Transfer GoDaddy account ownership to it@greenmarkwaste.com", "Daniel + current owner", "Phase 1 complete"],
        ["2.2", "Transfer Webflow workspace ownership to it@greenmarkwaste.com", "Daniel + current owner", "Phase 1 complete"],
        ["2.3", "Update billing on both accounts to accounting@greenmarkwaste.com", "Daniel", "Steps 2.1, 2.2"],
        ["2.4", "Create Cloudflare account under it@greenmarkwaste.com", "Daniel", "None"],
        ["2.5", "Add greenmarkwaste.com to Cloudflare, get assigned nameservers", "Daniel", "Step 2.4"],
    ]
    story.append(styled_table(p2_data, [0.4*inch, 3.3*inch, 1.5*inch, 1.5*inch], styles))

    story.append(Spacer(1, 12))
    # Phase 3
    story.append(Paragraph("Phase 3: DNS Migration (Week 3\u20134)", styles["SubsectionTitle"]))
    story.append(Paragraph("Goal: Cloudflare manages DNS. Site still points to Webflow. Zero downtime.", styles["BodyBold"]))
    p3_data = [
        ["#", "Action", "Owner", "Blocker"],
        ["3.1", "Change GoDaddy nameservers to Cloudflare\u2019s assigned NS records", "Daniel", "Phase 2 complete"],
        ["3.2", "Configure Cloudflare DNS to point to Webflow (preserves current site)", "Daniel", "Step 3.1"],
        ["3.3", "Verify site loads normally through Cloudflare (test all pages)", "Daniel", "Step 3.2"],
        ["3.4", "Enable Cloudflare CDN caching and SSL (free tier)", "Daniel", "Step 3.3"],
    ]
    story.append(styled_table(p3_data, [0.4*inch, 3.5*inch, 1*inch, 1.8*inch], styles))

    story.append(PageBreak())

    # Phase 4
    story.append(Paragraph("Phase 4: Build Remaining Astro Pages (Week 3\u20136)", styles["SubsectionTitle"]))
    story.append(Paragraph("Goal: All current pages rebuilt on Astro, plus new SEO pages.", styles["BodyBold"]))
    story.append(Paragraph(
        "This phase runs in parallel with Phase 3. The homepage is already built and deployed.",
        styles["BodyText2"]
    ))
    p4_data = [
        ["#", "Page / Feature", "Priority", "Notes"],
        ["4.1", "About page", "High", "Company story, leadership, values"],
        ["4.2", "Services pages (per service line)", "High", "Core conversion pages \u2014 what Greenmark does"],
        ["4.3", "Contact page with form", "High", "Must connect to HubSpot for lead capture"],
        ["4.4", "FAQ page", "Medium", "Common customer questions"],
        ["4.5", "Service-area city pages (DFW metro)", "Medium", "Local SEO \u2014 rank for \u201cwaste services [city]\u201d"],
        ["4.6", "Structured data / JSON-LD schema", "Medium", "Google Business, service schema, FAQ schema"],
        ["4.7", "GA4 + Google Search Console setup", "High", "Tracking from day one of cutover"],
        ["4.8", "Blog infrastructure", "Low", "Content marketing \u2014 can add post-launch"],
    ]
    story.append(styled_table(p4_data, [0.4*inch, 2.5*inch, 0.8*inch, 3*inch], styles))

    story.append(Spacer(1, 12))
    # Phase 5
    story.append(Paragraph("Phase 5: Cutover &amp; Verification (Week 6\u20137)", styles["SubsectionTitle"]))
    story.append(Paragraph("Goal: greenmarkwaste.com serves the Astro site. Webflow is standby.", styles["BodyBold"]))
    p5_data = [
        ["#", "Action", "Owner", "Blocker"],
        ["5.1", "Michael reviews and approves new site", "Michael", "Phase 4 complete"],
        ["5.2", "Provision SSL certificate for greenmarkwaste.com on Railway", "Daniel", "Step 5.1"],
        ["5.3", "Update Cloudflare DNS: CNAME \u2192 Railway endpoint", "Daniel", "Step 5.2"],
        ["5.4", "Verify all pages, forms, redirects, structured data", "Daniel", "Step 5.3"],
        ["5.5", "Monitor 48 hours \u2014 rankings, traffic, form submissions", "Daniel", "Step 5.4"],
        ["5.6", "If issues: rollback DNS to Webflow in Cloudflare (instant)", "Daniel", "Only if needed"],
    ]
    story.append(styled_table(p5_data, [0.4*inch, 3.3*inch, 1*inch, 2*inch], styles))

    story.append(Spacer(1, 12))
    # Phase 6
    story.append(Paragraph("Phase 6: Wind Down Webflow (Week 8+)", styles["SubsectionTitle"]))
    story.append(Paragraph("Goal: Webflow subscription cancelled once everyone\u2019s confident in the new site.", styles["BodyBold"]))
    p6_data = [
        ["#", "Action", "Owner", "Blocker"],
        ["6.1", "Confirm Astro site is stable (2+ weeks of clean operation)", "Daniel", "Phase 5 complete"],
        ["6.2", "Export any remaining Webflow content/assets", "Daniel", "Step 6.1"],
        ["6.3", "Cancel Webflow subscription (with Michael\u2019s approval)", "Daniel + Michael", "Step 6.2"],
        ["6.4", "Document final state in cockpit", "Daniel", "Step 6.3"],
    ]
    story.append(styled_table(p6_data, [0.4*inch, 3.3*inch, 1*inch, 2*inch], styles))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 6. ACCOUNT TRANSFER CHECKLISTS
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("6. Account Transfer Checklists", styles["SectionTitle"]))
    story.append(green_hr())
    story.append(Paragraph(
        "These follow the identical pattern used for Railway (Task-78), Supabase (Task-79), "
        "GitHub (Task-80), and ownership transfer emails (Task-81). All previously completed successfully.",
        styles["BodyText2"]
    ))

    story.append(Paragraph("GoDaddy (Registrar + DNS)", styles["SubsectionTitle"]))
    gd_data = [
        ["Step", "Action", "Who", "Depends On"],
        ["1", "Identify account owner (email on file)", "Michael", "\u2014"],
        ["2", "Add it@greenmarkwaste.com as delegate/admin", "Current owner", "Step 1"],
        ["3", "Transfer full ownership to it@greenmarkwaste.com", "Current owner + Daniel", "Step 2"],
        ["4", "Set billing to accounting@greenmarkwaste.com", "Daniel", "Step 3"],
        ["5", "Verify Daniel can manage DNS records", "Daniel", "Step 2"],
        ["6", "Verify domain auto-renewal is ON (Aug 2026 expiry)", "Daniel", "Step 2"],
        ["7", "Check if htdisposal.com is on same account", "Daniel", "Step 2"],
    ]
    story.append(styled_table(gd_data, [0.5*inch, 2.8*inch, 1.5*inch, 1.2*inch], styles))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Webflow (Hosting + CMS)", styles["SubsectionTitle"]))
    wf_data = [
        ["Step", "Action", "Who", "Depends On"],
        ["1", "Identify workspace owner (check LastPass or ask Michael)", "Daniel", "\u2014"],
        ["2", "Change workspace owner to it@greenmarkwaste.com", "Current owner", "Step 1"],
        ["3", "Set billing to accounting@greenmarkwaste.com", "Daniel", "Step 2"],
        ["4", "Audit all access (editors, designers, agencies)", "Daniel", "Step 2"],
        ["5", "Document plan tier and monthly cost", "Daniel", "Step 2"],
        ["6", "Check if htdisposal.com uses same workspace", "Daniel", "Step 2"],
    ]
    story.append(styled_table(wf_data, [0.5*inch, 2.8*inch, 1.5*inch, 1.2*inch], styles))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Cloudflare (New \u2014 DNS/CDN Layer)", styles["SubsectionTitle"]))
    cf_data = [
        ["Step", "Action", "Who", "Depends On"],
        ["1", "Create account under it@greenmarkwaste.com", "Daniel", "\u2014"],
        ["2", "Add greenmarkwaste.com", "Daniel", "Step 1"],
        ["3", "Change GoDaddy nameservers to Cloudflare", "Daniel", "GoDaddy Step 5 + Step 2"],
        ["4", "Configure DNS (initially point to Webflow)", "Daniel", "Step 3"],
        ["5", "When Astro ready: update DNS to Railway", "Daniel", "Step 4 + Astro complete"],
        ["6", "Set billing to accounting@ (if upgrading from free)", "Daniel", "Step 1"],
    ]
    story.append(styled_table(cf_data, [0.5*inch, 2.8*inch, 1.5*inch, 1.2*inch], styles))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 7. COST ANALYSIS & ROI
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("7. Cost Analysis &amp; ROI", styles["SectionTitle"]))
    story.append(green_hr())

    story.append(Paragraph("Current Costs (Estimated)", styles["SubsectionTitle"]))
    cost_data = [
        ["Item", "Monthly", "Annual", "Notes"],
        ["Webflow subscription (per site)", "$14\u2013$39", "$168\u2013$468", "Depends on plan tier \u2014 discovery needed"],
        ["Webflow (if 2 sites)", "$28\u2013$78", "$336\u2013$936", "htdisposal.com may be separate"],
        ["GoDaddy domain renewal", "\u2014", "~$20\u2013$40", "Standard .com pricing"],
        ["Designer/agency (if active)", "Unknown", "Unknown", "Discovery question for Michael"],
    ]
    story.append(styled_table(cost_data, [2*inch, 1*inch, 1.2*inch, 2.5*inch], styles))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Post-Migration Costs", styles["SubsectionTitle"]))
    post_data = [
        ["Item", "Monthly", "Annual", "Notes"],
        ["Railway hosting (Astro)", "$0 incremental", "$0", "Already included in Cerebro infrastructure"],
        ["Cloudflare (free tier)", "$0", "$0", "DNS, CDN, SSL all included"],
        ["GoDaddy domain renewal", "\u2014", "~$20\u2013$40", "Unchanged"],
        ["Designer/agency", "$0", "$0", "No longer needed \u2014 AI tools + optional CMS for self-service"],
    ]
    story.append(styled_table(post_data, [2*inch, 1*inch, 1.2*inch, 2.5*inch], styles))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Net Savings", styles["SubsectionTitle"]))
    story.append(Paragraph(
        "<b>Conservative estimate:</b> $336\u2013$936/year in Webflow subscriptions eliminated, "
        "plus whatever the designer/agency costs. The actual savings depend on the current Webflow plan tier "
        "and whether there\u2019s an active support contract\u2014both are discovery questions.",
        styles["BodyText2"]
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>The bigger ROI is in search rankings.</b> A waste services company in DFW competing for local "
        "search traffic\u2014where a single commercial account can be worth $5,000\u2013$50,000/year in revenue\u2014"
        "gains far more from moving up in Google results than it saves on subscriptions. "
        "The mobile speed fix (47\u219292) is the single highest-impact SEO change available.",
        styles["Callout"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 8. RISK ASSESSMENT
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("8. Risk Assessment &amp; Mitigations", styles["SectionTitle"]))
    story.append(green_hr())

    risk_data = [
        ["Risk", "Likelihood", "Impact", "Mitigation"],
        ["Domain expires before we get access (Aug 2026)",
         "Low", "Critical",
         "Step 1 of discovery: confirm auto-renewal. We have 5 months."],
        ["GoDaddy account holder is unresponsive",
         "Very Low", "High",
         "Greenmark is the domain registrant. Michael can reach whoever set it up. Worst case, GoDaddy has an account recovery process."],
        ["Designer/agency has questions about ownership change",
         "Low", "Low",
         "Not removing anyone\u2014adding Greenmark as owner. Designer keeps editor access. Active contracts continue."],
        ["DNS migration causes brief downtime",
         "Very Low", "Medium",
         "Cloudflare migration is zero-downtime by design. We point DNS to Webflow first, then switch to Astro later."],
        ["Astro site has issues after cutover",
         "Low", "Medium",
         "Instant rollback: change one Cloudflare DNS record back to Webflow. Takes effect in minutes."],
        ["Forms break during migration (leads lost)",
         "Medium", "High",
         "Discovery question: what forms exist and where do they submit? We rebuild before cutover."],
        ["htdisposal.com is on a different account/platform entirely",
         "Medium", "Low",
         "Discovery question. If separate, we handle it as a follow-on project. Doesn\u2019t block greenmarkwaste.com."],
        ["Michael is too busy to answer discovery questions",
         "Medium", "Medium",
         "Email is async. We also offer a 15-min call. Most answers are \u201cwho owns this?\u201d \u2014 quick lookups."],
    ]
    story.append(styled_table(risk_data, [2*inch, 0.7*inch, 0.65*inch, 3.35*inch], styles))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "The single biggest risk is <b>standing still while the goalposts move</b>: an unknown party controls the domain, "
        "Google\u2019s speed requirements keep tightening, and the domain could lapse in August 2026 if nobody "
        "monitors it. The Webflow site served Greenmark well\u2014but the landscape has shifted, and staying put "
        "now carries more risk than moving forward.",
        styles["Callout"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 9. STAKEHOLDER FAQ
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("9. Stakeholder FAQ", styles["SectionTitle"]))
    story.append(green_hr())
    story.append(Paragraph(
        "Twenty-five questions investors, the CEO, CFO, and CRO would ask\u2014and the answers.",
        styles["BodyText2"]
    ))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Cost &amp; ROI", styles["SubsectionTitle"]))
    faqs_cost = [
        ("What does Webflow cost us today?",
         "We don\u2019t know yet\u2014that\u2019s a discovery question. Webflow plans range $14\u2013$39/month per site. "
         "If both sites are on it, $28\u2013$78/month. The Astro replacement runs on Railway at zero incremental cost."),
        ("What does Cloudflare cost?",
         "Free tier. Zero dollars. DNS management, CDN, and SSL are all included at no charge."),
        ("What\u2019s the total cost of this migration?",
         "Daniel\u2019s time (already budgeted as part of the Cerebro engagement). No new vendor costs. "
         "Net effect is eliminating a recurring Webflow subscription."),
        ("What\u2019s the ROI?",
         "Eliminate Webflow subscription + eliminate designer dependency + 2x improvement in Google search visibility "
         "(mobile score 47\u219292 directly affects rankings). For a waste services company, even one additional "
         "lead per month from better SEO pays for the entire project."),
        ("Why not just fix the speed problem inside Webflow?",
         "We can\u2019t. Webflow generates its own HTML/CSS/JS\u2014we don\u2019t control it. The 17.5s load time is "
         "inherent to the platform. This wasn\u2019t a bad choice when the site was built\u2014Google\u2019s speed requirements "
         "got stricter, and AI tools now let us build at a performance level that wasn\u2019t accessible without an agency before."),
    ]
    for i, (q, a) in enumerate(faqs_cost, 1):
        story.append(qa_block(i, q, a, styles))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Risk", styles["SubsectionTitle"]))
    faqs_risk = [
        ("What if the migration breaks something?",
         "Cloudflare gives us instant rollback. Change one DNS record and greenmarkwaste.com points back to "
         "Webflow within minutes. The old site stays intact until we explicitly cancel it."),
        ("What about the domain expiring?",
         "greenmarkwaste.com expires Aug 1, 2026. Step one is confirming auto-renewal. We need access now\u2014not "
         "because we\u2019re in a rush, but because 5 months isn\u2019t comfortable if we discover a problem."),
        ("What happens if Daniel gets hit by a bus?",
         "That\u2019s why we centralize under it@greenmarkwaste.com\u2014a shared IT login, not a personal account. "
         "Any IT person can access GoDaddy, Webflow, Cloudflare, and Railway with one credential. "
         "This migration reduces bus-factor risk."),
        ("Is there downtime during the switch?",
         "Zero. Cloudflare manages DNS while pointing to Webflow first. When Astro is ready, we update one record. "
         "DNS propagation happens in the background. Visitors don\u2019t notice."),
        ("What if the designer or agency has concerns about the change?",
         "This isn\u2019t about cutting anyone out\u2014it\u2019s about making sure Greenmark has a front door key to its own house. "
         "The designer keeps editor access and can continue working. If there\u2019s an active support contract, that "
         "relationship continues until Greenmark decides otherwise."),
    ]
    for i, (q, a) in enumerate(faqs_risk, 6):
        story.append(qa_block(i, q, a, styles))

    story.append(PageBreak())

    story.append(Paragraph("Strategic", styles["SubsectionTitle"]))
    faqs_strat = [
        ("Why now? The website was fine before.",
         "It was. Two things changed: Google raised the bar on mobile speed (now a direct ranking penalty), and AI tools "
         "made it possible to build a faster replacement without hiring an agency. The opportunity didn\u2019t exist a year ago. "
         "Every month we wait, potential customers searching \u201cwaste services Dallas\u201d see competitors first."),
        ("Isn\u2019t this scope creep from Cerebro?",
         "No. Cerebro\u2019s mandate includes technology leadership. Account centralization was explicitly approved by "
         "Alex (Feb 27 policy). Website work was called \u201clow hanging fruit, top of the list\u201d by Michael and Alex on the "
         "Feb 19 call. We\u2019re acting on their stated priority, not inventing new work."),
        ("How does this help us win more deals?",
         "Three ways: (1) Better Google rankings = more inbound leads, (2) Faster site = lower bounce rate\u2014"
         "visitors who wait 17 seconds leave, (3) Service-area city pages let us rank for \u201cwaste services [city]\u201d across DFW."),
        ("What about htdisposal.com?",
         "Same playbook. We\u2019re discovering whether it shares accounts. If so, we centralize both in one pass. The Astro approach works for both."),
        ("Why Astro specifically? What if Astro disappears?",
         "Astro generates static HTML files. If it disappeared tomorrow, the site keeps running. We could rebuild with any "
         "static site generator. Zero vendor lock-in\u2014unlike Webflow where content is trapped in their CMS."),
    ]
    for i, (q, a) in enumerate(faqs_strat, 11):
        story.append(qa_block(i, q, a, styles))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Operations", styles["SubsectionTitle"]))
    faqs_ops = [
        ("Who updates the site after the switch? What if AIC\u2019s engagement ends?",
         "Initially, Daniel using AI tools\u2014same workflow as Cerebro. But the site is built so Greenmark isn\u2019t locked in. "
         "A headless CMS (like Decap or Tina\u2014both free) can be added so a marketing hire or admin can edit content in a browser "
         "without touching code. The architecture supports self-service; we\u2019ll set it up when the team is ready for it."),
        ("How do we handle content changes in the meantime?",
         "Webflow stays live until cutover. Any content changes just need to be reflected in the Astro build. "
         "We\u2019re not ripping out Webflow tomorrow\u2014this is a controlled transition."),
        ("What\u2019s the timeline?",
         "Account centralization: 1\u20132 weeks after Michael provides GoDaddy access. Astro build: depends on prioritization. "
         "Cutover: same day once pages are built and Michael approves. No hard deadline."),
        ("Do we need to redo SEO when we switch?",
         "No. Same URLs, same titles, same meta descriptions. Google sees the same site, just faster. "
         "Rankings should improve immediately from the speed boost."),
        ("What about forms? We need those leads.",
         "Discovery question #17 asks this exactly. Any forms on Webflow will be rebuilt in Astro pointing to the same "
         "backend (likely HubSpot). No leads get lost."),
    ]
    for i, (q, a) in enumerate(faqs_ops, 16):
        story.append(qa_block(i, q, a, styles))

    story.append(PageBreak())

    story.append(Paragraph("Governance &amp; Compliance", styles["SubsectionTitle"]))
    faqs_gov = [
        ("Is this consistent with how we handle other vendor accounts?",
         "Identical pattern to Tasks 78\u201381 (Railway, Supabase, GitHub). Same policy (Task-92), same target owner, "
         "same billing address. Alex already approved this framework."),
        ("Who has access to what after the transfer?",
         "it@greenmarkwaste.com owns everything. Daniel administers day-to-day. Michael retains visibility. "
         "Designers/agencies can have limited access as needed. All access is documented and auditable."),
        ("What if we decide to go back to Webflow later?",
         "Webflow isn\u2019t deleted\u2014we just stop paying for hosting. All project data persists on their free tier. "
         "Going back means resubscribing. But given the 2x speed improvement, there\u2019s no technical reason to go back."),
        ("Are we creating any security exposure?",
         "The opposite. Right now, an unknown party controls the domain. They could transfer it, change DNS, or let "
         "it expire. Centralizing under it@greenmarkwaste.com closes a security gap."),
        ("What does Alex (CFO) need to approve?",
         "Nothing new. The account ownership policy (Task-92) already covers this. Alex may want to see the Webflow "
         "subscription cost once we discover it. The email is CC\u2019d to Alex for visibility. Net financial impact is positive."),
    ]
    for i, (q, a) in enumerate(faqs_gov, 21):
        story.append(qa_block(i, q, a, styles))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 10. DISCOVERY QUESTIONS
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("10. Discovery Questions for Michael", styles["SectionTitle"]))
    story.append(green_hr())
    story.append(Paragraph(
        "We need these answers before we can proceed with account transfers and plan the cutover timeline.",
        styles["BodyText2"]
    ))

    story.append(Paragraph("Webflow History", styles["SubsectionTitle"]))
    wf_qs = [
        "Who designed the greenmarkwaste.com Webflow site? (agency, freelancer, internal?)",
        "Who approved the current design and content?",
        "Is there an ongoing support contract with the designer/agency? What does it cost?",
        "Who has been making edits? (Site was last published Feb 28, 2026.)",
        "Does htdisposal.com use the same Webflow workspace or a separate one?",
        "Are there pages or sections especially important to preserve exactly as-is?",
    ]
    for q in wf_qs:
        story.append(bullet(q, styles))

    story.append(Paragraph("GoDaddy Account", styles["SubsectionTitle"]))
    gd_qs = [
        "Who owns the GoDaddy account where greenmarkwaste.com is registered? (Email on file?)",
        "Is htdisposal.com also registered on GoDaddy? Same account or different?",
        "Are there other domains on that GoDaddy account?",
        "Can it@greenmarkwaste.com be added as delegate/admin right away?",
        "Is domain auto-renewal turned on? (Expires Aug 1, 2026.)",
    ]
    for q in gd_qs:
        story.append(bullet(q, styles))

    story.append(Paragraph("Billing &amp; Contracts", styles["SubsectionTitle"]))
    bill_qs = [
        "What Webflow plan/tier is the site on? Monthly cost?",
        "What\u2019s the GoDaddy renewal cost?",
        "Are there annual contracts with the designer/agency that need to be wound down?",
        "Is there Google Workspace or email hosting tied to the domain?",
    ]
    for q in bill_qs:
        story.append(bullet(q, styles))

    story.append(Paragraph("Transition Readiness", styles["SubsectionTitle"]))
    tr_qs = [
        "Are there draft pages, staging versions, or A/B tests not visible to the public?",
        "Are there forms that submit to external services (HubSpot, email, Zapier)?",
        "Does the site use Webflow-specific integrations (Logic, Memberships, Ecommerce)?",
        "Is there a Google Analytics or Tag Manager account connected? Who owns it?",
    ]
    for q in tr_qs:
        story.append(bullet(q, styles))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Most urgent:</b> GoDaddy account owner (domain expires Aug 2026), "
        "designer/agency relationship (affects decommission timeline), "
        "and Webflow subscription cost (informs ROI).",
        styles["Callout"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 11. DRAFT EMAIL
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("11. Draft Email to Michael", styles["SectionTitle"]))
    story.append(green_hr())
    story.append(Paragraph(
        "Ready to send. Non-technical language. CC\u2019d to Alex for visibility.",
        styles["BodyText2"]
    ))
    story.append(Spacer(1, 8))

    email_style = ParagraphStyle("email", parent=styles["BodyText2"], fontSize=9.5, leading=13.5,
                                  leftIndent=12, rightIndent=12, backColor=LIGHT_GRAY,
                                  borderColor=BORDER_GRAY, borderWidth=0.5, borderPadding=10)
    email_bold = ParagraphStyle("emailbold", parent=email_style, fontName="Helvetica-Bold")
    email_header = ParagraphStyle("emailhdr", parent=email_style, fontSize=8.5, textColor=TEXT_LIGHT)

    story.append(Paragraph(
        "<b>To:</b> Michael Nguyen (mnguyen@greenmarkwaste.com)<br/>"
        "<b>CC:</b> Alex Kaye (akaye@greenmarkwaste.com)<br/>"
        "<b>From:</b> Daniel Shanklin<br/>"
        "<b>Subject:</b> Website accounts + new greenmarkwaste.com \u2014 need your input",
        email_header
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Michael,", email_style))
    story.append(Paragraph(
        "Quick update on the website front, and a few things I need from you.", email_style))
    story.append(Paragraph(
        "<b>The short version:</b> AI tools have changed what\u2019s possible for a small team without a web agency. "
        "We used them to rebuild the greenmarkwaste.com homepage, and the performance improvement is significant "
        "enough that I think it\u2019s worth finishing the job and replacing the Webflow site entirely. "
        "But first I need some information from you.", email_style))
    story.append(Paragraph("<b>What changed:</b>", email_bold))
    story.append(Paragraph(
        "When the Webflow site was built, it was a solid choice\u2014good-looking site, quick to launch, no developers "
        "needed. But two things have shifted since then:", email_style))
    story.append(Paragraph(
        "<b>1. Google got stricter about mobile speed.</b> The current site scores 47/100 on Google\u2019s mobile test "
        "with a 17.5-second load time. That\u2019s in the \u201cPoor\u201d category\u2014Google is actively pushing "
        "Greenmark down in search results. This isn\u2019t a configuration issue; it\u2019s how the platform works.<br/><br/>"
        "<b>2. AI tools can now do what used to require a web agency.</b> We rebuilt the homepage on a modern framework "
        "and it scores 92/100 with a 2.7-second load time. Runs on Railway\u2014same as Cerebro, no new cost.",
        email_style))
    story.append(Paragraph(
        "<b>What this is NOT:</b> This isn\u2019t a criticism of whoever built the current site. They did good work with "
        "the tools available. The game just changed.", email_style))
    story.append(Paragraph("<b>What I need from you:</b>", email_bold))
    story.append(Paragraph(
        "<b>1. GoDaddy access</b> \u2014 Who owns the account? I need admin access for DNS and to confirm "
        "domain renewal. Expires August\u2014not urgent, but I want eyes on it.<br/><br/>"
        "<b>2. Webflow ownership</b> \u2014 Who owns the workspace? Need to transfer to it@greenmarkwaste.com, "
        "same pattern as Railway/Supabase/GitHub.<br/><br/>"
        "<b>3. A few questions:</b> Who designed the site? Ongoing support contract? Who\u2019s been making edits? "
        "Is htdisposal.com on the same accounts? Webflow subscription cost?",
        email_style))
    story.append(Paragraph(
        "Happy to do a 15-minute call if easier. No rush on the actual switch\u2014Webflow stays live until the new "
        "site is ready and you\u2019ve approved it. I\u2019m also planning for how to make updates easy for whoever "
        "needs to maintain the site down the road\u2014your team, a future hire, or us.",
        email_style))
    story.append(Paragraph("Thanks,<br/>Daniel", email_style))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 12. NEXT STEPS
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("12. Next Steps", styles["SectionTitle"]))
    story.append(green_hr())
    story.append(Paragraph(
        "Immediate actions\u2014listed in priority order. The first item unblocks everything else.",
        styles["BodyText2"]
    ))
    story.append(Spacer(1, 8))

    ns_data = [
        ["Priority", "Action", "Owner", "Timeline"],
        ["1 \u2014 CRITICAL", "Send discovery email to Michael", "Daniel", "Today"],
        ["2", "Michael responds with GoDaddy owner + Webflow info", "Michael", "This week"],
        ["3", "Get admin access to GoDaddy, verify auto-renewal", "Daniel", "Within 1 week of response"],
        ["4", "Transfer Webflow workspace to it@greenmarkwaste.com", "Daniel", "Within 1 week of response"],
        ["5", "Create Cloudflare account, add greenmarkwaste.com", "Daniel", "Can start immediately"],
        ["6", "Build remaining Astro pages (services, about, contact, FAQ)", "Daniel", "Ongoing \u2014 2\u20134 weeks"],
        ["7", "Set up GA4 + Google Search Console", "Daniel", "Before cutover"],
        ["8", "Michael approves new site for cutover", "Michael", "After pages complete"],
        ["9", "DNS cutover: Cloudflare \u2192 Railway", "Daniel", "Same day as approval"],
        ["10", "Monitor, verify, then cancel Webflow", "Daniel", "2 weeks after cutover"],
    ]
    story.append(styled_table(ns_data, [1*inch, 3*inch, 0.8*inch, 1.9*inch], styles))

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "The single most important thing right now is getting Michael\u2019s answers to the discovery questions. "
        "Everything else flows from that.",
        styles["Callout"]
    ))

    story.append(Spacer(1, 24))
    story.append(gray_hr())
    story.append(Paragraph(
        "This report was prepared by AIC Holdings for Greenmark Waste Solutions as part of Project Cerebro. "
        "Questions or feedback: Daniel Shanklin (dshanklin@aicholdings.com).",
        styles["FootnoteStyle"]
    ))

    # ══════════════════════════════════════════════════════════════════════
    # BUILD
    # ══════════════════════════════════════════════════════════════════════
    doc.build(story, onFirstPage=cover_page, onLaterPages=later_pages)
    print(f"Report generated: {output_path}")
    return output_path


if __name__ == "__main__":
    build_report()
