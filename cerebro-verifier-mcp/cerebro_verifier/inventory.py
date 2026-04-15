"""Page inventory — every dashboard page, what feeds it, what to check.

The inventory is the contract. Each page defines:
- Where to navigate
- What KPI labels to look for in the rendered page
- What SQL query produces the expected value
- How much tolerance to allow

The verification engine is generic. Domain knowledge lives here.
"""

from dataclasses import dataclass, field


@dataclass
class PageCheck:
    """A specific value to extract and verify on a page.

    The verifier finds `label` in the rendered page snapshot,
    extracts the adjacent value, then runs `ground_truth_sql`
    and compares the result within `tolerance`.
    """

    label: str  # Text to search for in snapshot, e.g. "Total Revenue"
    value_type: str = "currency"  # "currency" | "percent" | "number" | "text"
    ground_truth_sql: str = ""  # SQL that returns a single value. Empty = extract only, no comparison.
    tolerance: float = 0.01  # Fraction tolerance for numeric (0.01 = 1%)


@dataclass
class PageEntry:
    """A single dashboard page in the inventory."""

    slug: str  # URL-safe identifier, e.g. "financial"
    path: str  # URL path, e.g. "/dashboard/financial"
    title: str  # Human-readable name
    data_source: str  # What feeds it (for humans, not code)
    has_live_badge: bool = False  # Shows LIVE/MOCK DATA badge
    api_endpoint: str = ""  # API endpoint for pre-flight check
    smoke_only: bool = True  # True = just check page loads, no KPI extraction
    checks: list[PageCheck] = field(default_factory=list)


# ── Full verification pages ──────────────────────────────────────

EXECUTIVE = PageEntry(
    slug="executive",
    path="/dashboard",
    title="Executive Overview",
    data_source="sage_gold.entity_pnl via /api/financial",
    has_live_badge=True,
    api_endpoint="/api/financial",
    smoke_only=False,
    checks=[
        PageCheck(
            label="Total Revenue",
            value_type="currency",
            ground_truth_sql="SELECT SUM(revenue) FROM sage_gold.entity_pnl WHERE period = (SELECT MAX(period) FROM sage_gold.entity_pnl)",
        ),
        PageCheck(label="Disposal Cost", value_type="percent"),
        PageCheck(label="R&M", value_type="currency"),
    ],
)

FINANCIAL = PageEntry(
    slug="financial",
    path="/dashboard/financial",
    title="Financial",
    data_source="sage_gold.entity_pnl + gl_summary via /api/financial",
    has_live_badge=True,
    api_endpoint="/api/financial",
    smoke_only=False,
    checks=[
        PageCheck(
            label="Revenue",
            value_type="currency",
            ground_truth_sql="SELECT SUM(revenue) FROM sage_gold.entity_pnl WHERE period = (SELECT MAX(period) FROM sage_gold.entity_pnl)",
        ),
        PageCheck(label="Total Costs", value_type="currency"),
        PageCheck(label="Operating Margin", value_type="currency"),
        PageCheck(label="Disposal Cost", value_type="currency"),
    ],
)

SALES = PageEntry(
    slug="sales",
    path="/dashboard/sales",
    title="Sales",
    data_source="gold.pipeline_summary via /api/sales",
    has_live_badge=True,
    api_endpoint="/api/sales",
    smoke_only=False,
    checks=[
        PageCheck(label="Closed Won", value_type="currency"),
        PageCheck(label="Active Pipeline", value_type="currency"),
    ],
)


# ── Smoke-only pages ────────────────────────────────────────────

def _smoke(slug: str, path: str, title: str) -> PageEntry:
    return PageEntry(slug=slug, path=path, title=title, data_source="mock")


SMOKE_PAGES = [
    _smoke("operations", "/dashboard/operations", "Operations"),
    _smoke("drivers", "/dashboard/drivers", "Drivers"),
    _smoke("maintenance", "/dashboard/maintenance", "Maintenance"),
    _smoke("customers", "/dashboard/customers", "Customers"),
    _smoke("people", "/dashboard/people", "People"),
    _smoke("marketing", "/dashboard/marketing", "Marketing"),
    _smoke("map", "/dashboard/map", "Prospect Map"),
    _smoke("alerts", "/dashboard/alerts", "Alerts"),
    _smoke("ask", "/dashboard/ask", "Ask Cerebro"),
    _smoke("voice", "/dashboard/voice", "Voice"),
    _smoke("changelog", "/dashboard/changelog", "Changelog"),
    _smoke("feedback", "/dashboard/feedback", "Feedback"),
    _smoke("missions", "/dashboard/missions", "Mission Control"),
    _smoke("connections", "/dashboard/connections", "Connections"),
    _smoke("infrastructure", "/dashboard/infrastructure", "Infrastructure"),
    _smoke("architecture", "/dashboard/architecture", "Architecture"),
    _smoke("security", "/dashboard/security", "Security"),
    _smoke("ai-costs", "/dashboard/ai-costs", "AI Costs"),
    _smoke("bookmarks", "/dashboard/bookmarks", "Bookmarks"),
    _smoke("cerebro-mcp", "/dashboard/cerebro-mcp", "CerebroMCP"),
    _smoke("mockups", "/dashboard/mockups", "Mockups"),
    _smoke("training", "/dashboard/training", "Training"),
]

# ── Complete inventory ───────────────────────────────────────────

INVENTORY: list[PageEntry] = [EXECUTIVE, FINANCIAL, SALES] + SMOKE_PAGES

LIVE_PAGES = [p for p in INVENTORY if p.has_live_badge]
BADGED_SLUGS = {p.slug for p in LIVE_PAGES}


def get_page(slug: str) -> PageEntry | None:
    """Look up a page by slug."""
    for p in INVENTORY:
        if p.slug == slug:
            return p
    return None


def get_live_pages() -> list[PageEntry]:
    """Pages with live data and LIVE/MOCK badge."""
    return list(LIVE_PAGES)
