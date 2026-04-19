"""Data topology — the complete map of Greenmark's data systems.

Every vendor, every table, every pipeline, every relationship.
This is what makes the data engineer useful: it knows the WHOLE picture.
"""

from dataclasses import dataclass, field


@dataclass
class Table:
    schema: str
    name: str
    description: str
    row_count_hint: str  # "1.38M", "254", "~50"
    refresh_method: str  # "extract", "materialized_view", "gold_view"
    source: str  # which vendor/pipeline produces this
    key_columns: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)


@dataclass
class VendorSystem:
    name: str
    category: str  # "P1 Core", "P2 Operational", "P3 Supporting"
    status: str  # "connected", "pending", "blocked", "deprioritized"
    owner: str  # who at Greenmark owns this system
    api_type: str  # "REST", "SOAP/XML", "none", "unknown"
    auth_method: str
    rate_limit: str
    bronze_schema: str
    tables: list[Table] = field(default_factory=list)
    notes: str = ""


# ── Vendor Systems ──────────────────────────────────────────

SAGE_INTACCT = VendorSystem(
    name="Sage Intacct",
    category="P1 Core",
    status="connected",
    owner="Alex Kaye (CFO)",
    api_type="SOAP/XML",
    auth_method="Web Services credentials (sender_id + sender_password + company_id + user_id + user_password)",
    rate_limit="Governed by Sage — no published limit, but 1000 records per readByQuery page",
    bronze_schema="sage_bronze",
    tables=[
        Table("sage_bronze", "gl_journal_entries", "General ledger entries — the core financial data", "1.38M", "extract", "Sage Intacct", ["RECORDNO"]),
        Table("sage_bronze", "gl_accounts", "Chart of accounts", "254", "extract", "Sage Intacct", ["RECORDNO"]),
        Table("sage_bronze", "ap_bills", "Accounts payable bills", "853", "extract", "Sage Intacct", ["RECORDNO"]),
        Table("sage_bronze", "ar_invoices", "Accounts receivable invoices", "~1", "extract", "Sage Intacct", ["RECORDNO"]),
        Table("sage_bronze", "vendors", "Vendor master list", "423", "extract", "Sage Intacct", ["RECORDNO"]),
        Table("sage_bronze", "customers", "Customer master list", "3", "extract", "Sage Intacct", ["RECORDNO"]),
        Table("sage_silver", "gl_entries", "Typed GL entries with entity/department/location", "1.38M", "materialized_view", "sage_bronze.gl_journal_entries", depends_on=["sage_bronze.gl_journal_entries"]),
        Table("sage_silver", "gl_accounts", "Typed chart of accounts", "254", "materialized_view", "sage_bronze.gl_accounts", depends_on=["sage_bronze.gl_accounts"]),
        Table("sage_silver", "ap_bills", "Typed AP bills", "853", "materialized_view", "sage_bronze.ap_bills", depends_on=["sage_bronze.ap_bills"]),
        Table("sage_silver", "vendors", "Typed vendor records", "423", "materialized_view", "sage_bronze.vendors", depends_on=["sage_bronze.vendors"]),
        Table("sage_gold", "entity_pnl", "P&L by entity and period — THE metric Alex checks", "~50", "gold_view", "sage_silver.gl_entries", depends_on=["sage_silver.gl_entries"]),
        Table("sage_gold", "gl_summary", "GL account balances by entity/period/department", "1000+", "gold_view", "sage_silver.gl_entries", depends_on=["sage_silver.gl_entries"]),
        Table("sage_gold", "ap_aging", "Outstanding AP by vendor", "~200", "gold_view", "sage_silver.ap_bills + sage_silver.vendors", depends_on=["sage_silver.ap_bills", "sage_silver.vendors"]),
    ],
    notes="System of record per Alex. Revenue = 4xxx accounts, COGS = 5xxx, OpEx = 6-9xxx. L-codes map to locations (entity). Cerebro reads but NEVER writes to Sage.",
)

NAVUSOFT = VendorSystem(
    name="Navusoft",
    category="P1 Core",
    status="pending",
    owner="Michael Nguyen (President)",
    api_type="REST (inferred — server being set up Apr 19-20 weekend)",
    auth_method="Unknown — bearer token assumed",
    rate_limit="Unknown",
    bronze_schema="navusoft_bronze",
    tables=[
        Table("navusoft_bronze", "customers", "Customer accounts", "~150", "extract", "Navusoft"),
        Table("navusoft_bronze", "work_orders", "Service work orders", "~30K", "extract", "Navusoft"),
        Table("navusoft_bronze", "invoices", "Customer invoices", "~29K", "extract", "Navusoft"),
        Table("navusoft_bronze", "routes", "Route definitions", "~33", "extract", "Navusoft"),
        Table("navusoft_bronze", "service_agreements", "Service contracts", "~82", "extract", "Navusoft"),
    ],
    notes="API server being set up this weekend (Apr 19-20). Michael approved downtime. Sharae called to confirm. All API specs are INFERRED from AMCS platform patterns — real API may differ. NTX entity operations system.",
)

FLEETIO = VendorSystem(
    name="Fleetio",
    category="P2 Operational",
    status="pending",
    owner="Robert Heath (GM) — unverified provenance (L018)",
    api_type="REST",
    auth_method="Dual-header: Authorization: Token {api_key} + Account-Token: {account_token}",
    rate_limit="Professional: 50 req/min, Premium: 250 req/min",
    bronze_schema="fleet_bronze",
    tables=[
        Table("fleet_bronze", "vehicles", "Vehicle fleet records", "~40", "extract", "Fleetio"),
        Table("fleet_bronze", "maintenance_orders", "Work orders / R&M", "~2K", "extract", "Fleetio"),
        Table("fleet_bronze", "inspections", "Vehicle inspections", "~7K", "extract", "Fleetio"),
        Table("fleet_bronze", "fuel_logs", "Fuel transaction logs", "~6K", "extract", "Fleetio"),
    ],
    notes="Michael approved integration Apr 17. API access included with plan, no extra cost. Need someone with admin access to generate API key (Settings → Manage API Keys). Waiting on Michael/Robert. api@fleetio.com for API-specific questions. developer.fleetio.com for docs.",
)

HUBSPOT = VendorSystem(
    name="HubSpot",
    category="P1 Core",
    status="deprioritized",
    owner="Lannis Nicholson (CRO)",
    api_type="REST",
    auth_method="OAuth 2.0 (token expired)",
    rate_limit="100 req/10s (OAuth apps)",
    bronze_schema="hubspot_bronze",
    tables=[
        Table("hubspot_bronze", "companies", "Company records", "~200", "extract", "HubSpot"),
        Table("hubspot_bronze", "contacts", "Contact records", "~500", "extract", "HubSpot"),
        Table("hubspot_bronze", "deals", "Deal pipeline", "~800", "extract", "HubSpot"),
    ],
    notes="Deprioritized per Michael (Apr 6 call). OAuth token expired. data-daemon still tries and 401s — noisy but harmless. Will reconnect when Sage + Navusoft + Fleetio are stable.",
)

PAYLOCITY = VendorSystem(
    name="Paylocity",
    category="P2 Operational",
    status="pending",
    owner="Alex Kaye (CFO)",
    api_type="REST",
    auth_method="OAuth 2.0 client_credentials",
    rate_limit="Unknown",
    bronze_schema="paylocity_bronze",
    tables=[],
    notes="HR/payroll system. Connected to Cerebro dashboard (connected 6 hrs ago per bookmarks page). API research complete but no connector built yet.",
)

ALL_SYSTEMS = [SAGE_INTACCT, NAVUSOFT, FLEETIO, HUBSPOT, PAYLOCITY]

# ── Pipeline ────────────────────────────────────────────────

MEDALLION_LAYERS = {
    "bronze": "Raw data from vendor APIs. JSONB payloads stored as-is. One schema per vendor (sage_bronze, hubspot_bronze, etc).",
    "silver": "Typed columns extracted from bronze JSONB. Materialized views refreshed after each extraction. NULLIF cleanup, type casting, entity mapping.",
    "gold": "Aggregated business metrics for dashboards. Revenue by period, P&L by entity, AP aging. What Michael and Alex see.",
}

REFRESH_CHAIN = """
data-daemon extracts vendor → bronze (INSERT/UPSERT)
  → sage_gold.refresh_all() triggers:
    → REFRESH MATERIALIZED VIEW sage_silver.gl_entries (non-concurrent)
    → REFRESH MATERIALIZED VIEW sage_silver.gl_accounts
    → REFRESH MATERIALIZED VIEW sage_silver.ap_bills
    → REFRESH MATERIALIZED VIEW sage_silver.vendors
    → REFRESH MATERIALIZED VIEW sage_gold.gl_summary
    → REFRESH MATERIALIZED VIEW sage_gold.entity_pnl
    → REFRESH MATERIALIZED VIEW sage_gold.ap_aging
  → Dashboard reads gold via PostgREST (/api/financial)
"""

KNOWN_PARITY = {
    "2025-12": {
        "hometown": {"revenue": 872850.23, "verified": True, "source": "Alex's Greenmark_Metrics"},
        "ntx": {"revenue": 75246.02, "verified": True, "source": "Alex's Greenmark_Metrics"},
    }
}
