"""CI guard: run the doc-drift sweep and fail if any stale numbers remain.

The actual logic lives in `scripts/drift_sweep.py` so it can also be
invoked directly from a shell or a future pre-commit hook. This test
just shells out to the script and asserts a clean exit.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "drift_sweep.py"


def test_no_doc_drift() -> None:
    """Every scanned doc mirrors the canonical tool/test counts."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        "doc-drift sweep reported stale numbers:\n"
        f"--- stdout ---\n{result.stdout}\n"
        f"--- stderr ---\n{result.stderr}"
    )
