#!/usr/bin/env python3
"""
render_adr.py — Convert an ADR markdown file to a branded Greenmark PDF.

Usage:
    python3 render_adr.py <adr-path.md> [--logo <logo.png>] [--output <output.pdf>]

Produces a PDF with:
  - Greenmark logo header
  - Brand green (#193B2D) accents on headings and rules
  - Markdown tables rendered as styled PDF tables
  - Embedded images (relative paths resolved from the ADR's directory)
  - Proper typography and spacing
"""

import argparse
import os
import re
import sys
import textwrap

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# ── Brand Constants ──────────────────────────────────────────────────────────
BRAND_GREEN = colors.HexColor('#193B2D')
BRAND_GREEN_LIGHT = colors.HexColor('#E8F5E9')
BRAND_GREEN_MED = colors.HexColor('#A5D6A7')
TEXT_COLOR = colors.HexColor('#1a1a1a')
TEXT_SECONDARY = colors.HexColor('#4a4a4a')
BORDER_COLOR = colors.HexColor('#C8E6C9')

PAGE_MARGIN = 0.75 * inch


def build_styles():
    """Create branded paragraph styles."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'ADR_Title', parent=styles['Title'],
        fontSize=20, leading=26, textColor=BRAND_GREEN,
        spaceAfter=6, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'ADR_Meta', parent=styles['Normal'],
        fontSize=9, leading=13, textColor=TEXT_SECONDARY,
        spaceAfter=2, fontName='Helvetica'
    ))
    styles.add(ParagraphStyle(
        'ADR_H2', parent=styles['Heading2'],
        fontSize=14, leading=18, textColor=BRAND_GREEN,
        spaceBefore=16, spaceAfter=6, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'ADR_H3', parent=styles['Heading3'],
        fontSize=11, leading=15, textColor=BRAND_GREEN,
        spaceBefore=12, spaceAfter=4, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'ADR_Body', parent=styles['Normal'],
        fontSize=10, leading=14, textColor=TEXT_COLOR,
        spaceAfter=6, fontName='Helvetica'
    ))
    styles.add(ParagraphStyle(
        'ADR_Bullet', parent=styles['Normal'],
        fontSize=10, leading=14, textColor=TEXT_COLOR,
        spaceAfter=3, fontName='Helvetica',
        leftIndent=18, bulletIndent=6
    ))
    styles.add(ParagraphStyle(
        'ADR_Code', parent=styles['Code'],
        fontSize=8, leading=11, textColor=colors.HexColor('#333333'),
        backColor=colors.HexColor('#f5f5f5'),
        borderColor=BORDER_COLOR, borderWidth=0.5, borderPadding=6,
        fontName='Courier', spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        'ADR_TableCell', parent=styles['Normal'],
        fontSize=9, leading=12, textColor=TEXT_COLOR,
        fontName='Helvetica'
    ))
    styles.add(ParagraphStyle(
        'ADR_TableHeader', parent=styles['Normal'],
        fontSize=9, leading=12, textColor=colors.white,
        fontName='Helvetica-Bold'
    ))
    return styles


def parse_markdown(md_text):
    """Parse markdown into a list of block tokens."""
    blocks = []
    lines = md_text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Blank line
        if not line.strip():
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^---+\s*$', line):
            blocks.append({'type': 'hr'})
            i += 1
            continue

        # Headings
        m = re.match(r'^(#{1,4})\s+(.*)', line)
        if m:
            level = len(m.group(1))
            blocks.append({'type': f'h{level}', 'text': m.group(2).strip()})
            i += 1
            continue

        # Image
        m = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)', line.strip())
        if m:
            blocks.append({'type': 'image', 'alt': m.group(1), 'src': m.group(2)})
            i += 1
            continue

        # Table (detect by pipe-delimited lines)
        if '|' in line and line.strip().startswith('|'):
            table_lines = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            blocks.append({'type': 'table', 'lines': table_lines})
            continue

        # Bullet list
        m = re.match(r'^(\s*)[-*]\s+(.*)', line)
        if m:
            items = []
            while i < len(lines) and re.match(r'^(\s*)[-*]\s+(.*)', lines[i]):
                bm = re.match(r'^(\s*)[-*]\s+(.*)', lines[i])
                items.append(bm.group(2).strip())
                i += 1
            blocks.append({'type': 'bullets', 'items': items})
            continue

        # Numbered list
        m = re.match(r'^(\s*)\d+\.\s+(.*)', line)
        if m:
            items = []
            while i < len(lines) and re.match(r'^(\s*)\d+\.\s+(.*)', lines[i]):
                nm = re.match(r'^(\s*)\d+\.\s+(.*)', lines[i])
                items.append(nm.group(2).strip())
                i += 1
            blocks.append({'type': 'numbered', 'items': items})
            continue

        # Metadata line (- **Key**: Value)
        m = re.match(r'^-\s+\*\*(.+?)\*\*:\s*(.*)', line)
        if m:
            blocks.append({'type': 'meta', 'key': m.group(1), 'value': m.group(2).strip()})
            i += 1
            continue

        # Plain paragraph (collect consecutive non-blank lines)
        para_lines = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith('#') \
                and not lines[i].startswith('|') and not re.match(r'^---', lines[i]) \
                and not re.match(r'^[-*]\s+', lines[i]) and not re.match(r'^\d+\.\s+', lines[i]) \
                and not re.match(r'^!\[', lines[i].strip()):
            para_lines.append(lines[i])
            i += 1
        if para_lines:
            blocks.append({'type': 'paragraph', 'text': ' '.join(para_lines)})

    return blocks


def inline_markup(text):
    """Convert inline markdown to reportlab XML markup."""
    # Bold + italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<font face="Courier" size="8" color="#193B2D">\1</font>', text)
    # Links — show text, drop URL
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'<u>\1</u>', text)
    # Escape XML entities that reportlab chokes on
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # Restore our markup tags
    for tag in ['b', 'i', 'u', 'font']:
        text = text.replace(f'&lt;{tag}', f'<{tag}')
        text = text.replace(f'&lt;/{tag}&gt;', f'</{tag}>')
    # Restore font tag attributes
    text = re.sub(r'<font([^&]*?)&gt;', r'<font\1>', text)
    return text


def parse_table(table_lines):
    """Parse pipe-delimited markdown table into header + rows."""
    rows = []
    for line in table_lines:
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append(cells)

    if len(rows) < 2:
        return rows, False

    # Check if second row is separator (---|---|---)
    sep = rows[1]
    if all(re.match(r'^[-:]+$', c.strip()) for c in sep if c.strip()):
        return [rows[0]] + rows[2:], True

    return rows, False


def build_pdf_table(table_lines, styles):
    """Convert markdown table to a styled reportlab Table."""
    rows, has_header = parse_table(table_lines)
    if not rows:
        return None

    num_cols = max(len(r) for r in rows)
    # Pad short rows
    rows = [r + [''] * (num_cols - len(r)) for r in rows]

    # Convert to Paragraphs
    cell_style = styles['ADR_TableCell']
    header_style = styles['ADR_TableHeader']

    data = []
    for ri, row in enumerate(rows):
        pdf_row = []
        for cell in row:
            style = header_style if (ri == 0 and has_header) else cell_style
            pdf_row.append(Paragraph(inline_markup(cell), style))
        data.append(pdf_row)

    # Calculate column widths
    avail = letter[0] - 2 * PAGE_MARGIN
    col_width = avail / num_cols

    t = Table(data, colWidths=[col_width] * num_cols)

    style_cmds = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
    ]

    if has_header:
        style_cmds += [
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_GREEN),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ]

    # Alternate row shading
    for ri in range(1 if has_header else 0, len(data)):
        if ri % 2 == 0:
            style_cmds.append(('BACKGROUND', (0, ri), (-1, ri), BRAND_GREEN_LIGHT))

    t.setStyle(TableStyle(style_cmds))
    return t


def header_footer(canvas, doc, logo_path=None):
    """Draw branded header and footer on each page."""
    canvas.saveState()
    width, height = letter

    # Header line
    canvas.setStrokeColor(BRAND_GREEN)
    canvas.setLineWidth(2)
    canvas.line(PAGE_MARGIN, height - 0.5 * inch, width - PAGE_MARGIN, height - 0.5 * inch)

    # Logo in header
    if logo_path and os.path.exists(logo_path):
        try:
            canvas.drawImage(logo_path, PAGE_MARGIN, height - 0.48 * inch,
                             width=1.2 * inch, height=0.35 * inch,
                             preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # Footer
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(TEXT_SECONDARY)
    canvas.drawString(PAGE_MARGIN, 0.4 * inch,
                      'Greenmark Waste Solutions — Architecture Decision Record')
    canvas.drawRightString(width - PAGE_MARGIN, 0.4 * inch,
                           f'Page {doc.page}')

    # Footer line
    canvas.setStrokeColor(BORDER_COLOR)
    canvas.setLineWidth(0.5)
    canvas.line(PAGE_MARGIN, 0.55 * inch, width - PAGE_MARGIN, 0.55 * inch)

    canvas.restoreState()


def render_adr(md_path, logo_path=None, output_path=None):
    """Main render function: markdown → branded PDF."""
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(md_path, 'r') as f:
        md_text = f.read()

    adr_dir = os.path.dirname(os.path.abspath(md_path))

    if not output_path:
        output_path = os.path.splitext(md_path)[0] + '.pdf'

    styles = build_styles()
    blocks = parse_markdown(md_text)

    # Build story
    story = []
    story.append(Spacer(1, 0.3 * inch))  # Space below header

    for block in blocks:
        btype = block['type']

        if btype == 'h1':
            story.append(Paragraph(inline_markup(block['text']), styles['ADR_Title']))
            story.append(Spacer(1, 4))

        elif btype == 'meta':
            key = block['key']
            val = inline_markup(block['value'])
            story.append(Paragraph(
                f'<b>{key}:</b>  {val}', styles['ADR_Meta']
            ))

        elif btype == 'h2':
            story.append(Spacer(1, 4))
            story.append(HRFlowable(
                width='100%', thickness=1, color=BRAND_GREEN,
                spaceAfter=4, spaceBefore=8
            ))
            story.append(Paragraph(inline_markup(block['text']), styles['ADR_H2']))

        elif btype == 'h3':
            story.append(Paragraph(inline_markup(block['text']), styles['ADR_H3']))

        elif btype == 'h4':
            story.append(Paragraph(
                f'<b>{inline_markup(block["text"])}</b>', styles['ADR_Body']
            ))

        elif btype == 'hr':
            story.append(HRFlowable(
                width='100%', thickness=0.5, color=BORDER_COLOR,
                spaceAfter=8, spaceBefore=8
            ))

        elif btype == 'paragraph':
            story.append(Paragraph(inline_markup(block['text']), styles['ADR_Body']))

        elif btype == 'bullets':
            for item in block['items']:
                story.append(Paragraph(
                    f'<bullet>&bull;</bullet> {inline_markup(item)}',
                    styles['ADR_Bullet']
                ))

        elif btype == 'numbered':
            for idx, item in enumerate(block['items'], 1):
                story.append(Paragraph(
                    f'<bullet>{idx}.</bullet> {inline_markup(item)}',
                    styles['ADR_Bullet']
                ))

        elif btype == 'image':
            img_path = os.path.join(adr_dir, block['src'])
            if os.path.exists(img_path):
                try:
                    avail_width = letter[0] - 2 * PAGE_MARGIN
                    img = Image(img_path)
                    # Scale to fit page width, max 4 inches tall
                    ratio = min(avail_width / img.imageWidth, 4 * inch / img.imageHeight)
                    img.drawWidth = img.imageWidth * ratio
                    img.drawHeight = img.imageHeight * ratio
                    story.append(Spacer(1, 6))
                    story.append(img)
                    if block['alt']:
                        story.append(Paragraph(
                            f'<i>{inline_markup(block["alt"])}</i>',
                            styles['ADR_Meta']
                        ))
                    story.append(Spacer(1, 6))
                except Exception as e:
                    story.append(Paragraph(
                        f'[Image: {block["src"]} — {e}]', styles['ADR_Meta']
                    ))

        elif btype == 'table':
            t = build_pdf_table(block['lines'], styles)
            if t:
                story.append(Spacer(1, 4))
                story.append(t)
                story.append(Spacer(1, 8))

    # Build PDF
    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        leftMargin=PAGE_MARGIN, rightMargin=PAGE_MARGIN,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch
    )

    def on_page(canvas, doc):
        header_footer(canvas, doc, logo_path)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"PDF saved: {output_path}")
    return output_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Render ADR markdown to branded Greenmark PDF')
    parser.add_argument('adr_path', help='Path to ADR markdown file')
    parser.add_argument('--logo', help='Path to Greenmark logo PNG', default=None)
    parser.add_argument('--output', '-o', help='Output PDF path (default: same name as .md)', default=None)
    args = parser.parse_args()

    render_adr(args.adr_path, logo_path=args.logo, output_path=args.output)
