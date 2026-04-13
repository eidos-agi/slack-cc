"""Tests for the Rhea token-gate pattern."""

import time
from cerebro_github.gate import (
    GateContext,
    create_gate_token,
    validate_gate_token,
    validate_rhea_decision,
    build_merge_gate,
    build_milestone_gate,
    build_credential_gate,
)


class TestGateToken:
    """Token creation and validation."""

    def _make_context(self, **overrides):
        defaults = dict(
            action="merge_to_production",
            repo="cerebro",
            tier=1,
            environment="production",
            pr_number=42,
        )
        defaults.update(overrides)
        return GateContext(**defaults)

    def test_create_token_format(self):
        ctx = self._make_context()
        token = create_gate_token(ctx)
        assert token.startswith("gate-")
        parts = token.split("-")
        assert len(parts) == 3
        assert len(parts[1]) == 16  # hash

    def test_validate_valid_token(self):
        ctx = self._make_context()
        token = create_gate_token(ctx)
        valid, reason = validate_gate_token(token, ctx)
        assert valid, reason

    def test_validate_expired_token(self):
        ctx = self._make_context(timestamp=time.time() - 700)  # 11+ minutes old
        token = create_gate_token(ctx)
        valid, reason = validate_gate_token(token, ctx)
        assert not valid
        assert "expired" in reason.lower()

    def test_validate_wrong_context(self):
        ctx1 = self._make_context(pr_number=42)
        ctx2 = self._make_context(pr_number=99)
        token = create_gate_token(ctx1)
        valid, reason = validate_gate_token(token, ctx2)
        assert not valid
        assert "mismatch" in reason.lower()

    def test_validate_garbage_token(self):
        ctx = self._make_context()
        valid, reason = validate_gate_token("not-a-token", ctx)
        assert not valid

    def test_validate_empty_token(self):
        ctx = self._make_context()
        valid, reason = validate_gate_token("", ctx)
        assert not valid


class TestRheaDecisionValidation:
    """Rhea decision structure checks."""

    def test_valid_decision(self):
        decision = (
            "Accept the proposal with medium confidence. "
            "The ruling is to proceed with the merge. "
            "No critical risks identified."
        )
        valid, reason = validate_rhea_decision(decision)
        assert valid, reason

    def test_empty_decision(self):
        valid, reason = validate_rhea_decision("")
        assert not valid

    def test_too_short(self):
        valid, reason = validate_rhea_decision("ok")
        assert not valid

    def test_no_markers(self):
        decision = "This is a long enough string but has no debate markers in it whatsoever."
        valid, reason = validate_rhea_decision(decision)
        assert not valid
        assert "markers" in reason.lower()

    def test_fabricated_but_has_markers(self):
        # An agent could technically fake this — but that's the accepted threat model
        decision = "I accept this with high confidence. The ruling is to proceed."
        valid, reason = validate_rhea_decision(decision)
        assert valid


class TestGateBuilders:
    """Gate context builders for specific actions."""

    def test_merge_gate_structure(self):
        result = build_merge_gate("cerebro", 42, "main")
        assert result["gate"] == "rhea_review_required"
        assert result["gate_token"].startswith("gate-")
        assert "challenge_prompt" in result
        assert "instructions" in result
        assert result["context"]["action"] == "merge_to_production"
        assert result["context"]["repo"] == "cerebro"
        assert result["context"]["tier"] == 1

    def test_merge_gate_includes_deploy_target(self):
        result = build_merge_gate("cerebro", 42, "main")
        assert "jettaintelligence" in result["context"]["deploy_target"]

    def test_merge_gate_includes_dependencies(self):
        result = build_merge_gate("cerebro", 42, "main")
        # cerebro comes after cerebro-migrations in DEPLOY_ORDER
        assert "cerebro-migrations" in result["context"]["upstream_dependencies"]

    def test_milestone_gate_structure(self):
        result = build_milestone_gate("data-daemon", 8)
        assert result["gate"] == "rhea_review_required"
        assert result["context"]["action"] == "close_milestone"
        assert result["context"]["milestone_number"] == 8

    def test_credential_gate_structure(self):
        result = build_credential_gate("sage-intacct", ["develop", "production"])
        assert result["gate"] == "rhea_review_required"
        assert result["context"]["action"] == "provision_credentials"
        assert "SAGE_SENDER_ID" in result["context"]["credential_scope"]

    def test_credential_gate_notes_isolation(self):
        result = build_credential_gate("sage-intacct", ["develop", "production"])
        assert "same_both_envs" in result["instructions"].lower() or "Same both envs" in result["instructions"]


class TestChallengePrompt:
    """Challenge prompt generation."""

    def test_prompt_includes_key_info(self):
        ctx = GateContext(
            action="merge_to_production",
            repo="cerebro",
            tier=1,
            environment="production",
            pr_number=42,
            deploy_target="cerebro.greenmark.jettaintelligence.com",
        )
        prompt = ctx.to_challenge_prompt()
        assert "cerebro" in prompt
        assert "production" in prompt
        assert "#42" in prompt
        assert "jettaintelligence" in prompt

    def test_prompt_omits_empty_fields(self):
        ctx = GateContext(
            action="merge_to_production",
            repo="cerebro",
            tier=1,
            environment="production",
        )
        prompt = ctx.to_challenge_prompt()
        assert "PR:" not in prompt  # No PR number set
        assert "Dependencies:" not in prompt  # No deps
