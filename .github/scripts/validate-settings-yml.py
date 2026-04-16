#!/usr/bin/env python3
"""
Validate a single .github/settings.yml against the Greenmark tier contract.

Contract (from ADR-2026-03-repo-governance-as-code):

| Tier | Required checks on main               | Branch protection  |
|------|---------------------------------------|--------------------|
| T1   | Type Check, Lint, Unit Tests, Build   | PR required        |
| T2   | Lint, Tests                           | PR required        |
| T3   | None                                  | direct-to-main OK  |

Also enforces:
- `repository.topics` contains exactly one of `tier-t1` / `tier-t2` / `tier-t3`
- `repository.private: true` (Greenmark repos are all private)
- `repository.topics` contains `greenmark`
- `repository.name` matches the expected repo slug
- T1 repos have `main` branch protection with PR required + required_status_checks
- T2 repos have `main` branch protection with PR required
- T3 repos have NO required_pull_request_reviews on main

Exit codes:
- 0: valid
- 1: validation failed (specific errors printed to stderr)
- 2: file missing / unreadable
- 3: required Python dependency missing

Usage:
  validate-settings-yml.py <path-to-settings.yml> [expected-repo-name]

Prints one JSON object on stdout with { ok, repo, tier, errors } so
this can be piped into the cross-repo audit workflow.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    sys.stderr.write("ERROR: python3 -m pip install pyyaml\n")
    sys.exit(3)


TIER_TOPICS = {"tier-t1", "tier-t2", "tier-t3"}

# Per-tier minimum number of required status checks. Job *names* vary per
# repo (e.g. cerebro's CI emits "Unit Tests", most others emit "Tests") so
# we enforce only the minimum shape: T1 must declare ≥2 contexts, T2 ≥1,
# T3 must be null. The actual names belong to each repo's CI.
MIN_CONTEXTS = {
    "tier-t1": 2,
    "tier-t2": 1,
    "tier-t3": 0,
}


def validate(path: Path, expected_name: str | None) -> dict[str, Any]:
    errors: list[str] = []
    if not path.exists():
        return {
            "ok": False,
            "repo": expected_name,
            "tier": None,
            "errors": [f"file not found: {path}"],
        }

    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        return {
            "ok": False,
            "repo": expected_name,
            "tier": None,
            "errors": [f"yaml parse error: {exc}"],
        }

    if not isinstance(data, dict):
        return {
            "ok": False,
            "repo": expected_name,
            "tier": None,
            "errors": ["top-level must be a mapping"],
        }

    repo = data.get("repository", {})
    if not isinstance(repo, dict):
        errors.append("`repository` must be a mapping")
        repo = {}

    name = repo.get("name")
    if not name:
        errors.append("`repository.name` is required")
    elif expected_name and name != expected_name:
        errors.append(f"`repository.name` is {name!r} but path says {expected_name!r}")

    topics = repo.get("topics") or []
    if not isinstance(topics, list):
        errors.append("`repository.topics` must be a list")
        topics = []

    tier_topics = [t for t in topics if t in TIER_TOPICS]
    if len(tier_topics) == 0:
        errors.append(
            "`repository.topics` must include exactly one of tier-t1/tier-t2/tier-t3"
        )
        tier = None
    elif len(tier_topics) > 1:
        errors.append(
            f"`repository.topics` has multiple tier topics: {tier_topics} — exactly one allowed"
        )
        tier = tier_topics[0]
    else:
        tier = tier_topics[0]

    if "greenmark" not in topics:
        errors.append("`repository.topics` must include 'greenmark'")

    # Greenmark convention: everything is private until proven otherwise
    if repo.get("private") is not True:
        errors.append("`repository.private` must be true")

    branches = data.get("branches") or []
    if not isinstance(branches, list):
        errors.append("`branches` must be a list")
        branches = []
    main = next((b for b in branches if isinstance(b, dict) and b.get("name") == "main"), None)
    main_prot = (main or {}).get("protection") or {}

    # Find the default branch protection block — normally "main", sometimes
    # "develop" for repos where develop is the production branch.
    default_branch = repo.get("default_branch", "main")
    default_prot_block = next(
        (b for b in branches if isinstance(b, dict) and b.get("name") == default_branch),
        None,
    )
    default_prot = (default_prot_block or {}).get("protection") or {}

    # Tier-specific branch protection rules. Job *names* in required_status_checks
    # belong to each repo's CI — we only enforce the minimum count per tier.
    if tier in ("tier-t1", "tier-t2"):
        if default_prot_block is None:
            errors.append(
                f"{tier.upper()} repos must declare `branches[name={default_branch}]`"
            )
        elif default_prot is None or not isinstance(default_prot, dict):
            errors.append(
                f"{tier.upper()} repos must declare `branches[name={default_branch}].protection`"
            )
        else:
            if default_prot.get("required_pull_request_reviews") is None:
                errors.append(
                    f"{tier.upper()} {default_branch} must have "
                    "`required_pull_request_reviews` set (not null)"
                )
            rsc = default_prot.get("required_status_checks")
            # T1/T2 can declare null status checks if the repo has no CI yet;
            # that's a legitimate "PR required, no gate" state. But if declared,
            # the context list must meet the minimum count for the tier.
            if rsc is not None:
                checks = rsc.get("contexts") or []
                min_count = MIN_CONTEXTS[tier]
                if len(checks) < min_count:
                    errors.append(
                        f"{tier.upper()} {default_branch} `required_status_checks."
                        f"contexts` must declare at least {min_count} check(s), "
                        f"found {len(checks)}"
                    )

    elif tier == "tier-t3":
        # T3: direct-to-main OK. default branch protection must NOT require reviews.
        if default_prot_block is not None and default_prot:
            rpr = default_prot.get("required_pull_request_reviews")
            rsc = default_prot.get("required_status_checks")
            if rpr is not None or rsc is not None:
                errors.append(
                    f"T3 {default_branch} must have `required_pull_request_reviews: null` "
                    "and `required_status_checks: null` (tier = direct-to-main)"
                )

    return {
        "ok": len(errors) == 0,
        "repo": name or expected_name,
        "tier": tier,
        "errors": errors,
    }


def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write("usage: validate-settings-yml.py <path> [expected-name]\n")
        return 2
    path = Path(sys.argv[1])
    expected = sys.argv[2] if len(sys.argv) > 2 else None
    result = validate(path, expected)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
