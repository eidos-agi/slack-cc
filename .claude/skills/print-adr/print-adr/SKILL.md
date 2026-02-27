---
name: print-adr
description: "Render Greenmark Architecture Decision Records (ADRs) as branded PDFs with logo, brand green accents, embedded diagrams, and styled tables. Triggers: '/print-adr', '/print-adr 2026-01', 'print this ADR', 'PDF this ADR', 'render ADR as PDF'. Works with any ADR in infra/decisions/."
---

# Print ADR — Branded Greenmark PDF Renderer

Render any ADR markdown file as a polished, branded Greenmark PDF.

## Paths

- **ADR source**: `~/repos-greenmark-waste-solutions/infra/decisions/ADR-{number}.md`
- **Logo**: `~/repos-greenmark-waste-solutions/infra/brand/greenmark-full-dark.png`
- **Render script**: `scripts/render_adr.py` (bundled with this skill)
- **Output**: PDF saved next to the source `.md` file

## Workflow

1. **Resolve the ADR path** from user input:
   - `/print-adr 2026-01` → `infra/decisions/ADR-2026-01.md`
   - `/print-adr path/to/file.md` → use the literal path
   - `/print-adr` with no args → list ADRs in `infra/decisions/` and ask which one

2. **Run the render script**:
   ```bash
   python3 <skill-dir>/scripts/render_adr.py \
     "<adr-path>" \
     --logo ~/repos-greenmark-waste-solutions/infra/brand/greenmark-full-dark.png
   ```

3. **Open the PDF**:
   ```bash
   open "<adr-path-without-ext>.pdf"
   ```

4. **Report** the output path to the user.

## Brand Spec

- Primary color: `#193B2D` (dark green) — headings, rules, header line
- Light accent: `#E8F5E9` — alternating table rows
- Border: `#C8E6C9` — table grid, footer rule
- Logo: `greenmark-full-dark.png` in top-left header
- Footer: "Greenmark Waste Solutions — Architecture Decision Record" + page number

## What the Script Handles

- H1 title in brand green
- Metadata block (Status, Date, Owner, Related)
- H2/H3 sections with green accent rules
- Markdown tables with branded header row and alternating shading
- Embedded images (relative paths resolved from ADR directory)
- Bullet and numbered lists
- Inline bold, italic, code, and links
- Multi-page with consistent header/footer
