"""Token-gate pattern — Rhea pre-flight challenges at production boundaries.

Two-call handshake:
  1. Gate call → returns context snapshot + challenge prompt + gate_token
  2. Agent runs Rhea with the context
  3. Execution call → validates gate_token + rhea_decision, then executes

The gate_token ties the context snapshot to the execution. The rhea_decision
proves the agent ran adversarial reasoning before proceeding.
"""

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict

from .topology import (
    ENVIRONMENTS, SERVICES, VENDOR_CREDENTIALS, DEPLOY_ORDER,
    CHANGE_LIFECYCLE,
)
from .config import TIER_MAP, GH_ORG


@dataclass
class GateContext:
    """Snapshot of system state at the moment of the gate check."""
    action: str                    # "merge_to_production", "close_milestone", "provision_credentials"
    repo: str
    tier: int
    environment: str               # "production"
    pr_number: int | None = None
    milestone_number: int | None = None
    what_changes: str = ""
    deploy_target: str = ""
    rollback_path: str = ""
    credential_scope: str = ""
    upstream_dependencies: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_challenge_prompt(self) -> str:
        """Generate the prompt for Rhea to challenge."""
        lines = [
            f"Action: {self.action}",
            f"Repo: {self.repo} (T{self.tier})",
            f"Environment: {self.environment}",
        ]
        if self.pr_number:
            lines.append(f"PR: #{self.pr_number}")
        if self.milestone_number:
            lines.append(f"Milestone: #{self.milestone_number}")
        if self.what_changes:
            lines.append(f"What changes: {self.what_changes}")
        if self.deploy_target:
            lines.append(f"Deploy target: {self.deploy_target}")
        if self.rollback_path:
            lines.append(f"Rollback path: {self.rollback_path}")
        if self.credential_scope:
            lines.append(f"Credential scope: {self.credential_scope}")
        if self.upstream_dependencies:
            lines.append(f"Dependencies: {', '.join(self.upstream_dependencies)}")

        return "\n".join(lines)


def _hash_context(context: GateContext) -> str:
    """Deterministic hash of the gate context — ties the token to the snapshot."""
    payload = json.dumps(asdict(context), sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def create_gate_token(context: GateContext) -> str:
    """Create a gate token from the context snapshot."""
    return f"gate-{_hash_context(context)}-{int(context.timestamp)}"


def validate_gate_token(token: str, context: GateContext, max_age_seconds: int = 600) -> tuple[bool, str]:
    """Validate a gate token against the context.

    Returns (valid, reason).
    Token expires after max_age_seconds (default 10 minutes).
    """
    if not token or not token.startswith("gate-"):
        return False, "Invalid token format. Must start with 'gate-'."

    parts = token.split("-")
    if len(parts) != 3:
        return False, "Invalid token format. Expected gate-<hash>-<timestamp>."

    token_hash = parts[1]
    try:
        token_time = int(parts[2])
    except ValueError:
        return False, "Invalid timestamp in token."

    # Check age
    age = time.time() - token_time
    if age > max_age_seconds:
        return False, f"Token expired ({int(age)}s old, max {max_age_seconds}s)."

    # Check hash matches context
    expected_hash = _hash_context(context)
    if token_hash != expected_hash:
        return False, "Token hash mismatch — context has changed since gate was issued."

    return True, "Valid."


def validate_rhea_decision(decision: str) -> tuple[bool, str]:
    """Validate that a Rhea decision looks real (not fabricated).

    This is an integrity check, not a security boundary.
    We check for structure, not cryptographic proof.
    """
    if not decision or len(decision) < 20:
        return False, "Rhea decision is empty or too short. Run rhea_challenge() first."

    # A real Rhea decision contains these markers from the debate format
    expected_markers = ["confidence", "accept", "reject", "modify", "ruling", "proceed"]
    found = sum(1 for m in expected_markers if m.lower() in decision.lower())
    if found < 2:
        return False, (
            "Rhea decision doesn't look like debate output. "
            "Expected markers like 'confidence', 'ruling', 'proceed'. "
            "Run mcp__rhea__rhea_challenge() with the gate context."
        )

    return True, "Decision accepted."


# ── Gate builders for specific actions ──────────────────────

def build_merge_gate(repo: str, pr_number: int, base_branch: str) -> dict:
    """Build gate context for a production merge."""
    tier = TIER_MAP.get(repo, 3)
    service = SERVICES.get(repo)
    domain = service.domains.get("production", "") if service else ""

    # Find upstream dependencies
    deps = []
    if repo in DEPLOY_ORDER:
        idx = DEPLOY_ORDER.index(repo)
        deps = DEPLOY_ORDER[:idx]  # Everything that deploys before this

    context = GateContext(
        action="merge_to_production",
        repo=repo,
        tier=tier,
        environment="production",
        pr_number=pr_number,
        what_changes=f"Merging PR #{pr_number} to {base_branch} on {repo}",
        deploy_target=domain or f"{repo} production service",
        rollback_path=f"git revert on {base_branch}, or Railway rollback via railguey",
        upstream_dependencies=deps,
    )

    token = create_gate_token(context)

    return {
        "gate": "rhea_review_required",
        "gate_token": token,
        "context": asdict(context),
        "challenge_prompt": context.to_challenge_prompt(),
        "instructions": (
            "This merge targets production on a T1 repo. "
            "Run mcp__rhea__rhea_challenge with the challenge_prompt above, "
            "then call execute_gated_merge() with the gate_token and rhea_decision."
        ),
    }


def build_milestone_gate(repo: str, milestone_number: int) -> dict:
    """Build gate context for closing a milestone."""
    tier = TIER_MAP.get(repo, 3)

    context = GateContext(
        action="close_milestone",
        repo=repo,
        tier=tier,
        environment="both",
        milestone_number=milestone_number,
        what_changes=f"Closing milestone #{milestone_number} on {repo}",
    )

    token = create_gate_token(context)

    return {
        "gate": "rhea_review_required",
        "gate_token": token,
        "context": asdict(context),
        "challenge_prompt": context.to_challenge_prompt(),
        "instructions": (
            "Closing a milestone declares work complete. "
            "Run mcp__rhea__rhea_challenge to verify all sub-issues are truly done, "
            "then call execute_gated_close() with the gate_token and rhea_decision."
        ),
    }


def build_credential_gate(vendor: str, environments: list[str]) -> dict:
    """Build gate context for credential provisioning."""
    vc = next((v for v in VENDOR_CREDENTIALS if v.vendor == vendor), None)

    context = GateContext(
        action="provision_credentials",
        repo="",
        tier=1,
        environment=", ".join(environments),
        credential_scope=f"{vendor}: {vc.env_vars if vc else 'unknown vars'}",
        what_changes=f"Setting {vendor} credentials on {', '.join(environments)}",
    )

    token = create_gate_token(context)

    return {
        "gate": "rhea_review_required",
        "gate_token": token,
        "context": asdict(context),
        "challenge_prompt": context.to_challenge_prompt(),
        "instructions": (
            "Credential provisioning affects system access. "
            f"Vendor: {vendor}. Same both envs: {vc.same_both_envs if vc else 'unknown'}. "
            "Run mcp__rhea__rhea_challenge to verify scope and isolation, "
            "then call the provisioning tool with gate_token and rhea_decision."
        ),
    }
