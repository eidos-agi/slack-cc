"""Verification run reporting."""

from datetime import datetime

from . import evidence


def build_report(
    environment: str,
    page_results: list[dict],
    badge_results: list[dict] | None = None,
    ground_truth_results: list[dict] | None = None,
) -> dict:
    """Build a verification run report."""
    run_id = evidence.get_run_id()

    total = len(page_results)
    passed = sum(1 for r in page_results if r.get("status") == "pass")
    failed = sum(1 for r in page_results if r.get("status") == "fail")
    errors = sum(1 for r in page_results if r.get("status") == "error")

    report = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "environment": environment,
        "summary": {
            "total_pages": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "all_green": failed == 0 and errors == 0,
        },
        "pages": page_results,
    }

    if badge_results:
        live_count = sum(1 for b in badge_results if b.get("badge") == "LIVE")
        mock_count = sum(1 for b in badge_results if b.get("badge") == "MOCK")
        report["badges"] = {
            "live": live_count,
            "mock": mock_count,
            "details": badge_results,
        }

    if ground_truth_results:
        gt_pass = sum(1 for g in ground_truth_results if g.get("match"))
        gt_fail = sum(1 for g in ground_truth_results if not g.get("match"))
        report["ground_truth"] = {
            "passed": gt_pass,
            "failed": gt_fail,
            "details": ground_truth_results,
        }

    evidence.save_run_report(report)
    return report
