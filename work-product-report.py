#!/usr/bin/env python3
"""Generate a branded Greenmark work product + acquisition thesis report PDF."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus.flowables import Flowable
from pathlib import Path

# Brand
BRAND_GREEN = HexColor("#193B2D")
BRAND_LIGHT = HexColor("#E8F0EC")
ACCENT_GREEN = HexColor("#2D6B4A")
MUTED = HexColor("#6B7B73")
DARK = HexColor("#1A1A1A")
WHITE = white
AMBER = HexColor("#92700A")
AMBER_BG = HexColor("#FDF8EC")
AMBER_BORDER = HexColor("#D4A843")

BRAND_DIR = Path("/Users/dshanklinbv/repos-greenmark-waste-solutions/infra/brand")
LOGO_PATH = str(BRAND_DIR / "greenmark-full-white.png")
OUTPUT = Path("/Users/dshanklinbv/repos-greenmark-waste-solutions/greenmark-cockpit/work-product-report.pdf")

W, H = letter
MARGIN = 0.5 * inch
USABLE = W - 2 * MARGIN


# ── Flowables ────────────────────────────────────────────────────────

class BrandHeader(Flowable):
    def __init__(self, width, title, subtitle):
        super().__init__()
        self.width = width
        self.title = title
        self.subtitle = subtitle
        self.height = 0.95 * inch

    def draw(self):
        c = self.canv
        c.setFillColor(BRAND_GREEN)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=0)
        try:
            c.drawImage(LOGO_PATH, 0.3 * inch, self.height - 0.46 * inch,
                        width=1.35 * inch, height=0.28 * inch, mask='auto',
                        preserveAspectRatio=True)
        except Exception:
            pass
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(0.3 * inch, 0.18 * inch, self.title)
        c.setFillColor(HexColor("#A8C4B5"))
        c.setFont("Helvetica", 8)
        c.drawRightString(self.width - 0.3 * inch, 0.2 * inch, self.subtitle)


class StatRow(Flowable):
    def __init__(self, width, stats):
        super().__init__()
        self.width = width
        self.stats = stats
        self.height = 0.78 * inch

    def draw(self):
        c = self.canv
        n = len(self.stats)
        gap = 0.08 * inch
        bw = (self.width - gap * (n - 1)) / n
        for i, (num, label) in enumerate(self.stats):
            x = i * (bw + gap)
            c.setFillColor(BRAND_LIGHT)
            c.roundRect(x, 0, bw, self.height, 4, fill=1, stroke=0)
            c.setFillColor(ACCENT_GREEN)
            c.rect(x, self.height - 3, bw, 3, fill=1, stroke=0)
            c.setFillColor(BRAND_GREEN)
            c.setFont("Helvetica-Bold", 19)
            c.drawCentredString(x + bw / 2, 0.3 * inch, str(num))
            c.setFillColor(MUTED)
            c.setFont("Helvetica", 7)
            c.drawCentredString(x + bw / 2, 0.12 * inch, label)


class AccentBox(Flowable):
    """Colored box with left border accent."""
    def __init__(self, width, text, bg, border, text_color, font='Helvetica', size=8.5, bold=False):
        super().__init__()
        self.width = width
        self.text = text
        self.bg = bg
        self.border = border
        self.tc = text_color
        self.font = 'Helvetica-Bold' if bold else font
        self.size = size
        # Estimate height from text length
        chars_per_line = int((width - 0.6 * inch) / (size * 0.45))
        lines = max(1, len(text) // chars_per_line + 1)
        self.height = max(0.38 * inch, lines * (size + 3) / 72 * inch + 0.18 * inch)

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=0)
        c.setFillColor(self.border)
        c.roundRect(0, 0, 4, self.height, 2, fill=1, stroke=0)
        # Draw text with simple wrapping
        c.setFillColor(self.tc)
        c.setFont(self.font, self.size)
        max_w = self.width - 0.5 * inch
        words = self.text.split()
        lines = []
        current = ""
        for w in words:
            test = current + " " + w if current else w
            if c.stringWidth(test, self.font, self.size) < max_w:
                current = test
            else:
                lines.append(current)
                current = w
        if current:
            lines.append(current)
        y = self.height - 0.18 * inch
        for line in lines:
            c.drawString(0.25 * inch, y, line)
            y -= (self.size + 3)


# ── Styles ───────────────────────────────────────────────────────────

def S():
    """Build all paragraph styles."""
    d = {}
    d['sh'] = ParagraphStyle('sh', fontName='Helvetica-Bold', fontSize=11,
        textColor=BRAND_GREEN, spaceBefore=8, spaceAfter=4)
    d['sh2'] = ParagraphStyle('sh2', fontName='Helvetica-Bold', fontSize=9,
        textColor=ACCENT_GREEN, spaceBefore=6, spaceAfter=2)
    d['body'] = ParagraphStyle('body', fontName='Helvetica', fontSize=8.5,
        textColor=DARK, leading=12, spaceAfter=3)
    d['sm'] = ParagraphStyle('sm', fontName='Helvetica', fontSize=7.5,
        textColor=DARK, leading=10.5, spaceAfter=2)
    d['tiny'] = ParagraphStyle('tiny', fontName='Helvetica', fontSize=7,
        textColor=DARK, leading=9.5, spaceAfter=1.5)
    d['fn'] = ParagraphStyle('fn', fontName='Helvetica', fontSize=6.5,
        textColor=MUTED, leading=8.5, spaceAfter=1)
    d['big'] = ParagraphStyle('big', fontName='Helvetica-Bold', fontSize=16,
        textColor=BRAND_GREEN, alignment=TA_CENTER, spaceBefore=4, spaceAfter=2,
        leading=20)
    d['bigsub'] = ParagraphStyle('bigsub', fontName='Helvetica', fontSize=8.5,
        textColor=MUTED, alignment=TA_CENTER, spaceAfter=4)
    d['emph'] = ParagraphStyle('emph', fontName='Helvetica-Oblique', fontSize=8,
        textColor=ACCENT_GREEN, leading=11, alignment=TA_CENTER, spaceBefore=4)
    d['footer'] = ParagraphStyle('footer', fontName='Helvetica', fontSize=6.5,
        textColor=MUTED, alignment=TA_CENTER)
    return d


# ── Table builder ────────────────────────────────────────────────────

def tbl(header, rows, widths, grade_col=None):
    """Build a styled table. grade_col = index of column to color-code grades."""
    th = ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=7, textColor=WHITE, leading=9)
    tc = ParagraphStyle('tc', fontName='Helvetica', fontSize=7, textColor=DARK, leading=9.5)
    tcb = ParagraphStyle('tcb', fontName='Helvetica-Bold', fontSize=7, textColor=DARK, leading=9.5)

    grade_colors = {
        'A': HexColor("#1B8C4E"), 'A-': HexColor("#27AE60"),
        'B+': HexColor("#2E86C1"), 'B': HexColor("#2980B9"), 'B-': HexColor("#D4A843"),
        'C+': HexColor("#C0392B"), 'C': HexColor("#C0392B"),
    }

    data = [[Paragraph(h, th) for h in header]]
    for row in rows:
        cells = []
        for j, cell in enumerate(row):
            if grade_col is not None and j == grade_col:
                color = grade_colors.get(str(cell).strip(), DARK)
                gs = ParagraphStyle('g', fontName='Helvetica-Bold', fontSize=9,
                                     textColor=color, leading=11, alignment=TA_CENTER)
                cells.append(Paragraph(str(cell), gs))
            else:
                cells.append(Paragraph(str(cell), tcb if j == 0 else tc))
        data.append(cells)

    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_GREEN),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.4, HexColor("#D0D8D4")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, BRAND_LIGHT]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return t


def hr():
    return HRFlowable(width="100%", thickness=0.5, color=HexColor("#D0D8D4"), spaceAfter=6, spaceBefore=4)


def footer_func(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 6.5)
    canvas.drawCentredString(W / 2, 0.28 * inch,
        f"Greenmark Waste Solutions  \u2022  Confidential  \u2022  Page {doc.page}")
    canvas.restoreState()


# ── Build ────────────────────────────────────────────────────────────

def build_pdf():
    s = S()
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=letter,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=0.35*inch, bottomMargin=0.42*inch)
    story = []

    # ============================================================
    # PAGE 1 — WORK PRODUCT PROOF
    # ============================================================
    story.append(BrandHeader(USABLE, "Work Product Assessment",
        "Feb 11\u201326, 2026  |  16 Calendar Days  |  1 Engineer + Claude Code"))
    story.append(Spacer(1, 0.12 * inch))

    story.append(StatRow(USABLE, [
        ("~1,400", "Equivalent Hours"),
        ("13", "Repositories"),
        ("171", "Commits"),
        ("465", "Source Files"),
        ("143K", "Lines Written"),
    ]))
    story.append(Spacer(1, 0.06 * inch))

    story.append(Paragraph("8\u201310 months of senior engineering in 16 days", s['big']))
    story.append(Paragraph(
        "One engineer + Claude Code. Net estimate after 20\u201325% self-grading adjustment (see page 2).",
        s['bigsub']))

    story.append(hr())

    # Hours table — compact
    story.append(Paragraph("Hours by Work Category", s['sh']))
    story.append(tbl(
        ["Category", "Repos", "Lines", "Rate", "Hours"],
        [
            ["Production Code", "cerebro, data-daemon, portal, QA", "39,000", "80 lines/hr", "488"],
            ["Project Management", "cockpit, kickoff, director, cost-acctg", "30,500", "60 lines/hr", "508"],
            ["Infra Research", "infra (vendor APIs, ADRs, specs)", "11,000", "40 lines/hr", "275"],
            ["Design", "tech-deck (slides, visual assets)", "3,700", "30 lines/hr", "123"],
            ["Generated", "weekly-updates, test fixtures", "52,800", "Setup only", "20"],
            ["Overhead", "Meetings, comms, context-switching", "\u2014", "+25%", "354"],
            ["Gross Total", "", "137,000", "", "1,768"],
            ["Self-Grading Adj.", "Scorecard, page 2", "", "\u221220\u201325%", "\u2212354\u2013442"],
            ["Net Estimate", "", "", "", "1,326\u20131,414"],
        ],
        [1.15*inch, 2.15*inch, 0.65*inch, 0.8*inch, 0.8*inch],
    ))
    story.append(Spacer(1, 0.08 * inch))

    # Deliverables list
    story.append(Paragraph("What Was Delivered", s['sh']))
    for d in [
        "<b>Cerebro Dashboard</b> \u2014 Next.js 16, React 19, 3 views, ECharts, entity toggling, dark mode, Railway deploy",
        "<b>Video Feedback System</b> \u2014 Screen+camera PiP recording, Supabase Storage, Whisper transcription, GPT-4o extraction",
        "<b>data-daemon ETL</b> \u2014 Python pipeline, YAML config, Postgres job queue, 82 tests, medallion architecture",
        "<b>6 Vendor API Deep Dives</b> \u2014 Sage Intacct, Navusoft, HubSpot, Fleetio, Paylocity, WAM \u2014 full data model specs",
        "<b>Project Ops</b> \u2014 AI cockpit with 12+ skills, meeting processing, weekly reports, 3 ADRs, backlog system",
        "<b>Infrastructure</b> \u2014 Railway (2 services), Supabase, DNS, migration tooling, portal with auth, QA dashboard",
    ]:
        story.append(Paragraph("\u2022  " + d, s['sm']))

    story.append(Spacer(1, 0.08 * inch))
    story.append(hr())

    # Financial
    story.append(Paragraph("Financial Equivalent", s['sh']))
    story.append(Paragraph(
        "At a blended rate of <b>$175/hr</b> (senior full-stack + DevOps + PM): "
        "<b>$232K\u2013$247K</b> net equivalent. Gross before adjustment: $309K. "
        "Specialized consultancies bill $200\u2013$350/hr for comparable scope.",
        s['body']
    ))
    story.append(Spacer(1, 0.06 * inch))

    # Repo breakdown — move here to fill page 1
    story.append(Paragraph("Repository Breakdown", s['sh']))
    story.append(tbl(
        ["Repository", "Com.", "Lines", "Files", "Description"],
        [
            ["cerebro", "37", "23,650", "172", "Production Next.js dashboard \u2014 3 views, entity toggling, dark mode, ECharts, feedback system"],
            ["greenmark-cockpit", "52", "24,079", "115", "AI cockpit \u2014 session lifecycle, meeting processing, backlog, 12+ skills"],
            ["data-daemon", "13", "9,374", "78", "Python ETL \u2014 YAML config, Postgres job queue, 82 tests, medallion arch"],
            ["infra", "21", "11,009", "102", "Vendor research \u2014 6 deep-dive API docs, 3 ADRs, data dictionary"],
            ["weekly-updates", "9", "20,534", "22", "Automated weekly engineering reports from GitHub commits"],
            ["portal", "3", "3,819", "12", "Express.js portal with cookie auth, Railway deployment"],
            ["Other (6 repos)", "36", "44,376", "118", "Kickoff artifacts, test data, presentations, QA, cost research, role docs"],
        ],
        [1.15*inch, 0.4*inch, 0.55*inch, 0.4*inch, 4.05*inch],
    ))

    # ============================================================
    # PAGE 2 — HONEST SCORECARD
    # ============================================================
    story.append(PageBreak())
    story.append(BrandHeader(USABLE, "Deliverable Scorecard",
        "Honest self-assessment  |  What\u2019s production-ready and what\u2019s not"))
    story.append(Spacer(1, 0.1 * inch))

    story.append(Paragraph(
        "Every deliverable graded honestly. This is an internal assessment, not a sales deck. "
        "The grades reflect what\u2019s production-ready today, what\u2019s solid scaffolding waiting for "
        "real data, and what\u2019s still just a plan.",
        s['body']
    ))
    story.append(Spacer(1, 0.04 * inch))

    story.append(tbl(
        ["Deliverable", "Grade", "Honest Assessment", "What\u2019s Missing"],
        [
            ["Cerebro Dashboard", "B+",
             "3 real views, entity toggling, ECharts, dark mode, Railway deploy. Functional and polished.",
             "Running on mockup data. No live vendor connections yet."],
            ["data-daemon ETL", "A-",
             "82 tests, YAML-driven, medallion architecture, Postgres job queue. Well-architected and tested.",
             "Not connected to a real vendor API in production."],
            ["Vendor API Research", "A",
             "6 deep dives with full data model specs, auth flows, rate limits, proposed schemas. Genuinely thorough.",
             "3rd Eye is still a complete black box."],
            ["Video Feedback", "B",
             "Screen+camera PiP recording, Supabase upload, Whisper+GPT-4o extraction. Works end-to-end.",
             "Not yet tested by actual users."],
            ["Project Ops / Cockpit", "A-",
             "12+ skills, session lifecycle, meeting processing, weekly reports, backlog. Real operational leverage.",
             "Some skills are overbuilt for current 1-person team."],
            ["Infrastructure", "B+",
             "Railway (2 services), Supabase, DNS, migration tooling, portal with auth. All functional.",
             "Auth is still shared-password stopgap."],
            ["SEO Strategy", "C+",
             "90-day plans written for both websites. Reasonable but entirely theoretical.",
             "No baseline audit done. Plans untested against real data."],
            ["Weekly Reports", "B",
             "Automated from GitHub commits. Useful for stakeholder visibility.",
             "Format is functional, not polished. Needs feedback loop."],
        ],
        [1.1*inch, 0.45*inch, 2.75*inch, 1.8*inch],
        grade_col=1,
    ))
    story.append(Spacer(1, 0.12 * inch))

    story.append(hr())

    # What's real vs scaffolding
    story.append(Paragraph("What\u2019s Real vs. What\u2019s Scaffolding", s['sh']))
    story.append(Spacer(1, 0.04 * inch))

    story.append(AccentBox(USABLE,
        "Production-ready today (70%): Vendor research (directly usable), project ops (running daily), "
        "infrastructure (live, serving traffic), data-daemon architecture (tested, waiting for credentials).",
        BRAND_LIGHT, ACCENT_GREEN, DARK))
    story.append(Spacer(1, 0.06 * inch))

    story.append(AccentBox(USABLE,
        "Functional but incomplete (25%): Cerebro dashboards (great framework, mockup data), feedback system "
        "(works end-to-end, untested by real users), weekly reports (useful, could be sharper).",
        BRAND_LIGHT, HexColor("#2980B9"), DARK))
    story.append(Spacer(1, 0.06 * inch))

    story.append(AccentBox(USABLE,
        "Plans without execution (5%): SEO strategy (written but no baseline measured). "
        "This is the weakest deliverable \u2014 strategy docs without data are just opinions.",
        AMBER_BG, AMBER_BORDER, AMBER))
    story.append(Spacer(1, 0.12 * inch))

    story.append(hr())

    # Underestimates
    story.append(Paragraph("What the Hours Model Underestimates", s['sh2']))
    for item in [
        "<b>Architectural decisions</b> \u2014 Choosing medallion architecture, designing the ETL job queue, Supabase migration strategy. Senior judgment doesn\u2019t show up in line counts.",
        "<b>Vendor discovery</b> \u2014 Determining WAM has no API, Expensify flows through Sage, 3rd Eye is a black box. Discovery that prevents wasted months.",
        "<b>Stakeholder translation</b> \u2014 Converting Michael\u2019s vision into specs, Alex\u2019s financial knowledge into data models, Robert\u2019s operations into dashboards.",
    ]:
        story.append(Paragraph("\u2022  " + item, s['tiny']))

    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph(
        "The exact number matters less than the ratio. Whether 1,300 or 1,800 hours, the 50\u201370x "
        "acceleration is the signal. That ratio creates the acquisition opportunity on the next page.",
        s['emph']))

    # ============================================================
    # PAGE 3 — THE ATOMS THESIS
    # ============================================================
    story.append(PageBreak())
    story.append(BrandHeader(USABLE, "The Atoms Arbitrage",
        "Why AI-native operators should buy physical businesses now"))
    story.append(Spacer(1, 0.12 * inch))

    story.append(Paragraph("The Thesis", s['sh']))
    story.append(AccentBox(USABLE,
        "Physical businesses are priced assuming traditional technology costs. An AI-native operator "
        "eliminates 80-90% of that cost, creating instant margin expansion the seller's asking price doesn't reflect. "
        "The arbitrage window is open now and closes as AI adoption spreads.",
        BRAND_LIGHT, BRAND_GREEN, BRAND_GREEN, bold=True, size=8.5))
    story.append(Spacer(1, 0.1 * inch))

    story.append(Paragraph("The Pricing Gap", s['sh']))
    story.append(Paragraph(
        "Waste haulers, fleet operators, and industrial service companies are valued on historical EBITDA. "
        "Their technology spend is baked into operating costs: $200K\u2013$500K/year for consultants, custom "
        "integrations, IT staff, and vendor management. Buyers and sellers both assume these costs are "
        "structural. They are not.",
        s['body']
    ))
    story.append(Spacer(1, 0.04 * inch))

    story.append(Paragraph("The Math", s['sh2']))
    story.append(tbl(
        ["", "Traditional Operator", "AI-Native Operator", "Delta"],
        [
            ["Annual technology labor", "$300K\u2013$500K", "$30K\u2013$60K", "\u221280\u201390%"],
            ["Time to integrate acquisition", "6\u201312 months", "2\u20134 weeks", "\u221285\u201395%"],
            ["Vendor system connectors", "$50K\u2013$150K each", "$2K\u2013$5K each", "\u221295%+"],
            ["Dashboard / BI development", "$100K\u2013$300K", "$5K\u2013$15K", "\u221295%"],
            ["Data warehouse setup", "$75K\u2013$200K", "$3K\u2013$10K", "\u221295%"],
            ["Ongoing maintenance", "2\u20133 FTEs", "0.25\u20130.5 FTE", "\u221280%"],
        ],
        [1.55*inch, 1.45*inch, 1.35*inch, 0.95*inch],
    ))
    story.append(Spacer(1, 0.06 * inch))

    story.append(Paragraph(
        "These are not projections. The Greenmark engagement is the proof. "
        "The work product on pages 1\u20132 was delivered in 16 days by one engineer. "
        "A traditional consultancy would quote 6\u20139 months and $250K+ for the same scope.",
        ParagraphStyle('proof', fontName='Helvetica-Oblique', fontSize=8,
            textColor=ACCENT_GREEN, leading=11, spaceAfter=6)
    ))

    story.append(hr())

    story.append(Paragraph("Why Atoms, Why Now", s['sh']))
    for p in [
        "<b>Physical businesses have real moats.</b> Waste routes, fleet contracts, municipal permits, "
        "CDL drivers, landfill access. A new entrant can\u2019t download these assets.",
        "<b>Multiples are compressed.</b> Industrial services trade at 4\u20137x EBITDA vs. 15\u201330x for software. "
        "The technology layer that transforms these businesses costs almost nothing to build now.",
        "<b>The arbitrage window is open.</b> Most PE firms still budget technology at 2023 rates. They hire "
        "Deloitte, staff 5-person integration teams, spend 12 months connecting systems. An AI-native "
        "operator does it in weeks. This gap closes as AI adoption spreads.",
        "<b>Sellers don\u2019t know their tech costs are inflated.</b> A waste company spending $400K/year on "
        "IT consulting doesn\u2019t know that number could be $40K. You buy at the old price and operate "
        "at the new one.",
    ]:
        story.append(Paragraph("\u2022  " + p, s['sm']))

    story.append(Spacer(1, 0.08 * inch))

    # Worked example
    story.append(Paragraph("Worked Example: Acquiring a $5M-Revenue Waste Hauler", s['sh']))
    story.append(tbl(
        ["Metric", "At Purchase", "Year 1 (AI-Native)", "Delta"],
        [
            ["Revenue", "$5.0M", "$5.0M", "\u2014"],
            ["Technology opex", "$350K/yr", "$45K/yr", "+$305K to EBITDA"],
            ["EBITDA", "$750K", "$1,055K", "+41%"],
            ["Valuation at 5x", "$3.75M", "$5.28M", "+$1.53M"],
            ["Integration cost", "\u2014", "$25K (one-time)", "\u2014"],
            ["Time to dashboards", "\u2014", "3\u20134 weeks", "\u2014"],
        ],
        [1.65*inch, 1.5*inch, 1.5*inch, 1.3*inch],
    ))
    story.append(Spacer(1, 0.04 * inch))
    story.append(Paragraph(
        "The technology cost reduction alone pays for the integration in the first month and adds "
        "$1.5M+ to enterprise value at the same multiple.",
        s['tiny']
    ))

    # ============================================================
    # PAGE 4 — THE PLAYBOOK
    # ============================================================
    story.append(PageBreak())
    story.append(BrandHeader(USABLE, "The Playbook",
        "Repeatable acquisition integration at 50x speed"))
    story.append(Spacer(1, 0.12 * inch))

    story.append(Paragraph("Acquisition Integration: Week-by-Week", s['sh']))
    story.append(tbl(
        ["Week", "Phase", "Deliverables", "Traditional"],
        [
            ["1", "Discovery", "Map all vendor systems, API access, data flows. Infra inventory. Stakeholder interviews.", "Month 1\u20132"],
            ["2", "Connect", "First 2 data sources live in warehouse. Bronze tables populated. Pipeline running.", "Month 3\u20134"],
            ["3", "Dashboards", "Executive + Financial + Operations dashboards with real data. Stakeholder review.", "Month 5\u20137"],
            ["4", "Operate", "QA monitoring, alerting, weekly reports automated. Feedback system live. Handoff.", "Month 8\u201312"],
        ],
        [0.45*inch, 0.7*inch, 3.7*inch, 0.95*inch],
    ))
    story.append(Spacer(1, 0.08 * inch))

    story.append(Paragraph("The Repeatable Stack", s['sh']))
    story.append(Paragraph(
        "Every acquisition gets the same technology layer, deployed in the same order. "
        "The stack is already built \u2014 it gets configured per acquisition:",
        s['body']
    ))
    for item in [
        "<b>data-daemon</b> \u2014 YAML-driven ETL. Add a vendor by writing a config file, not code. 82 tests. Medallion architecture.",
        "<b>Cerebro</b> \u2014 Dashboard framework. Entity toggling, dark mode, ECharts. New dashboards are configuration, not greenfield.",
        "<b>AI Cockpit</b> \u2014 Session management, meeting processing, vendor research, weekly reports. The operating system for tech.",
        "<b>Migration tooling</b> \u2014 Supabase + psycopg2. Schema changes via numbered SQL files. Idempotent, auditable.",
        "<b>Feedback system</b> \u2014 Screen recording + AI transcription. Non-technical operators report issues without writing tickets.",
    ]:
        story.append(Paragraph("\u2022  " + item, s['sm']))

    story.append(Spacer(1, 0.08 * inch))

    story.append(Paragraph("Unit Economics Per Acquisition", s['sh']))
    story.append(tbl(
        ["Cost Component", "Traditional", "AI-Native", "Notes"],
        [
            ["Integration labor", "$250K\u2013$500K", "$15K\u2013$30K", "1 engineer \u00d7 4 weeks vs. 5-person team \u00d7 9 months"],
            ["Ongoing tech ops", "$300K\u2013$500K/yr", "$30K\u2013$60K/yr", "0.25 FTE + AI tooling vs. 2\u20133 FTEs"],
            ["Time to value", "6\u201312 months", "3\u20134 weeks", "Dashboards live before first board meeting"],
            ["Marginal cost of next acq.", "$250K+", "~$10K", "Stack is built. Each new company is config."],
        ],
        [1.25*inch, 1.15*inch, 1.0*inch, 2.5*inch],
    ))
    story.append(Spacer(1, 0.08 * inch))

    story.append(Paragraph("The Compounding Advantage", s['sh']))
    story.append(Paragraph(
        "Each acquisition makes the next one cheaper and faster. Vendor connectors built for Company A "
        "work for Company B \u2014 waste haulers use the same 10\u201315 systems. Dashboard templates, data models, "
        "and operating playbooks accumulate. By acquisition 3\u20134, integration cost approaches zero and "
        "the timeline approaches days.",
        s['body']
    ))
    story.append(Paragraph(
        "This is the real moat: not any single technology, but the <b>velocity of integration</b>. "
        "A traditional acquirer takes 12 months to integrate one company. An AI-native operator integrates "
        "one per month. Over 3 years: 3 acquisitions vs. 36. Same capital, same team, 12x the portfolio.",
        s['body']
    ))
    story.append(Spacer(1, 0.1 * inch))

    # Closing
    story.append(AccentBox(USABLE,
        "The window is open now. AI capability advances monthly. The acquirers who move first buy at "
        "old-cost multiples and operate at new-cost structures. The arbitrage closes as the market "
        "catches up. The time to buy atoms is today.",
        BRAND_LIGHT, BRAND_GREEN, BRAND_GREEN, bold=True, size=9))

    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(
        "Prepared by Daniel Shanklin, Director of AI & Technology  |  AIC Holdings  |  February 2026",
        s['footer']))

    doc.build(story, onFirstPage=footer_func, onLaterPages=footer_func)
    print(f"PDF written to {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
