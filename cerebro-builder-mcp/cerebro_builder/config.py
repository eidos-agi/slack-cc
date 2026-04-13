"""Ceremony configuration — single source of truth.

Information Hierarchy (most detail → least):

  GitHub repos         All code, commits, CI, PRs, discussions.
    └─ Project Board   Curated: issues + milestones + status + progress bars.
         └─ Wrike      Executive distillation: business outcomes only.

Each layer filters for its audience:
  - GitHub has everything. Engineers live here.
  - The Project Board (#1, "Cerebro Engineering") strips noise into
    actionable items. Daniel sees progress across all repos here.
    Milestones are parent issues; sub-issues fill the progress bar.
  - Wrike strips engineering detail into business language.
    Michael and Alex see "Sage data flowing" not "PR #29 fixes WAL pressure".

Work that isn't on the board doesn't exist. The create_work → open_pr →
merge_pr ceremony exists to enforce this: every code change traces back
to a board item, and closing an issue updates the milestone progress.
"""

import os
from pathlib import Path

GH_ORG = "greenmark-waste-solutions"

# Cerebro Engineering project board — the engineering source of truth.
# Wrike is executive-level for Michael/Alex. This board is task-level for Daniel.
# Every issue created by create_work() lands here. PRs link back via Closes #N.
# The Roadmap view shows the Gantt. Sub-issues show milestone progress.
# URL: https://github.com/orgs/greenmark-waste-solutions/projects/1
PROJECT_NUMBER = 1
PROJECT_ID = "PVT_kwDOD49Jk84BRMz-"
ASSIGNEE = "dshanklin-bv"

# Status field options
STATUS_FIELD_ID = "PVTSSF_lADOD49Jk84BRMz-zg_GOSY"
STATUS_TODO = "f75ad846"
STATUS_IN_PROGRESS = "47fc9ee4"
STATUS_DONE = "98236657"

# Date fields
START_DATE_FIELD_ID = "PVTF_lADOD49Jk84BRMz-zhBasc0"
TARGET_DATE_FIELD_ID = "PVTF_lADOD49Jk84BRMz-zhBasds"

# Tier map — mirrors tools/tier-map.sh
TIER_MAP = {
    # T1 — Production
    "cerebro": 1,
    "cerebro-migrations": 1,
    "data-daemon": 1,
    # T2 — Supporting
    "cerebro-qa": 2,
    "cerebro-warp-speed": 2,
    "cerebro-warp-speed-excel": 2,
    "cerebro-ai-services": 2,
    "cerebro-bot-farm": 2,
    # T3 — Reference
    "infra": 3,
    "greenmark-cockpit": 3,
    "cerebro-mcp": 3,
    "cerebro-vault": 3,
    "cerebro-excel": 3,
}

# T1 repos that have Railway services — used by health_check
T1_SERVICES = {
    "cerebro": "/home/dev/repos/cerebro",
    "data-daemon": "/home/dev/repos/data-daemon",
}

PROTECTED_BRANCHES = {"main", "master", "develop"}

# CI conclusions that don't count as failures
# SKIPPED = step that doesn't run on PRs (e.g., deploy, notify)
# NEUTRAL = informational (e.g., monitoring checks marked non-blocking)
CI_NON_FAILURE_CONCLUSIONS = {"SUCCESS", "SKIPPED", "NEUTRAL"}

# Ledger persistence path
LEDGER_PATH = Path(os.getenv(
    "CEREBRO_GITHUB_LEDGER",
    str(Path(__file__).parent.parent / "ledger.json"),
))
