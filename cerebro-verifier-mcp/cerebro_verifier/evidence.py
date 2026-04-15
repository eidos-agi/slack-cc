"""Evidence management — screenshots and extracted values per run."""

import json
import re
from datetime import datetime
from pathlib import Path

EVIDENCE_DIR = Path(__file__).parent.parent / "evidence"
RUNS_DIR = Path(__file__).parent.parent / "runs"


def _current_run_id() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


_active_run_id: str = ""


def start_run() -> str:
    """Start a new verification run. Returns the run ID."""
    global _active_run_id
    _active_run_id = _current_run_id()
    run_dir = EVIDENCE_DIR / _active_run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return _active_run_id


def get_run_id() -> str:
    """Get the current run ID, starting one if needed."""
    global _active_run_id
    if not _active_run_id:
        _active_run_id = start_run()
    return _active_run_id


def screenshot_path(slug: str) -> str:
    """Get the path for a page screenshot."""
    run_id = get_run_id()
    run_dir = EVIDENCE_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return str(run_dir / f"{slug}.png")


def save_extraction(slug: str, data: dict):
    """Save extracted values for a page."""
    run_id = get_run_id()
    run_dir = EVIDENCE_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(run_dir / f"{slug}.json", "w") as f:
        json.dump(data, f, indent=2, default=str)


def save_run_report(report: dict):
    """Save the final run report."""
    run_id = get_run_id()
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RUNS_DIR / f"{run_id}.json", "w") as f:
        json.dump(report, f, indent=2, default=str)


def load_run_report(run_id: str = "") -> dict | None:
    """Load a run report. Empty run_id = latest."""
    if not RUNS_DIR.exists():
        return None

    if not run_id:
        files = sorted(RUNS_DIR.glob("*.json"), reverse=True)
        if not files:
            return None
        with open(files[0]) as f:
            return json.load(f)

    path = RUNS_DIR / f"{run_id}.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def parse_currency(text: str) -> float | None:
    """Parse a currency string to float.

    Handles: $872,850  $872.9K  $1.2M  872850.23  -$12,345
    """
    if not text:
        return None

    text = text.strip()

    # Handle K/M suffixes
    multiplier = 1.0
    if text.upper().endswith("K"):
        multiplier = 1_000
        text = text[:-1]
    elif text.upper().endswith("M"):
        multiplier = 1_000_000
        text = text[:-1]

    # Strip currency symbols and commas
    cleaned = re.sub(r"[,$\s]", "", text)

    try:
        return float(cleaned) * multiplier
    except ValueError:
        return None


def parse_percent(text: str) -> float | None:
    """Parse a percentage string to float.

    Handles: 13.2%  -5.1%  13.2
    """
    if not text:
        return None

    text = text.strip().rstrip("%")
    try:
        return float(text)
    except ValueError:
        return None
