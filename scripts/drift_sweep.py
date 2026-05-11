#!/usr/bin/env python3
"""Mechanical doc-drift sweep.

Verifies that the high-traffic project docs mirror the canonical numbers
sourced from authoritative files (`tests/conftest.py` constants and a live
`pytest --collect-only` count). Prints `[file:line]` lines for every stale
number it finds and exits non-zero if any drift exists.

Safe to run in CI: no network, no LLM dep, no editor required.

Out of scope: this scanner intentionally skips `docs/HANDOFF.md` and
`docs/superpowers/plans/**` because both preserve sprint chronology --
historical tool/test counts in those files are correct as of THEIR
session and must not be rewritten.

Usage:

    python scripts/drift_sweep.py

Exit codes:
    0 -- no drift found
    1 -- drift found (each finding printed on its own line)
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Files that are expected to reflect the current canonical numbers.
# Anything not in this list (HANDOFF, superpowers plans, archived session
# memory) is intentionally NOT scanned -- those files freeze history.
SCAN_FILES = [
    "README.md",
    "CLAUDE.md",
    "AGENTS.md",
    "tests/README.md",
    "docs/INSTALLATION.md",
    "docs/RESTART-RECOVERY.md",
    ".github/copilot-instructions.md",
]


# Each entry is (compiled_regex, canonical_key). The regex must have a
# single capturing group around the number to validate. Patterns are
# deliberately specific (must include a context word like "tools" or
# "pytest cases") to avoid matching unrelated digits.
PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(\d+)\s+tools?\s+total\b", re.IGNORECASE), "tools"),
    (re.compile(r"\ball\s+(\d+)\s+tools?\b", re.IGNORECASE), "tools"),
    (re.compile(r"\b(\d+)\s+tools?\s+live\b", re.IGNORECASE), "tools"),
    (re.compile(r"\b(\d+)\s+tools?\s+shipped\b", re.IGNORECASE), "tools"),
    (re.compile(r"\b(\d+)\s+tools?\s+become\s+available\b", re.IGNORECASE), "tools"),
    (re.compile(r"across\s+all\s+(\d+)\s+tools?\b", re.IGNORECASE), "tools"),
    (re.compile(r"\b(\d+)\s+native\s+C\+\+\s+handlers?\b", re.IGNORECASE), "cpp_handlers"),
    (re.compile(r"\b(\d+)\s+UE\s+C\+\+\s+handlers?\b", re.IGNORECASE), "cpp_handlers"),
    (re.compile(r"\((\d+)\s+C\+\+\s+handlers?", re.IGNORECASE), "cpp_handlers"),
    (re.compile(r"\b(\d+)\s+bridge[- ]side\s+synthetic", re.IGNORECASE), "synthetic_tools"),
    (re.compile(r"\b(\d+)\s+synthetic\s+tools?\b", re.IGNORECASE), "synthetic_tools"),
    (re.compile(r"\b(\d+)\s+bridge\s+synthetic\b", re.IGNORECASE), "synthetic_tools"),
    (re.compile(r"\b(\d+)\s+pytest\s+cases?\b", re.IGNORECASE), "pytest_cases"),
    (re.compile(r"#\s*(\d+)\s+tests,", re.IGNORECASE), "pytest_cases"),
]


def _read_conftest_constants() -> tuple[int, int]:
    """Return (cpp_handler_count, synthetic_tool_count) from conftest."""
    conftest_path = REPO_ROOT / "tests" / "conftest.py"
    text = conftest_path.read_text(encoding="utf-8")
    cpp_match = re.search(r"EXPECTED_CPP_HANDLER_COUNT\s*=\s*(\d+)", text)
    syn_match = re.search(r"EXPECTED_SYNTHETIC_TOOL_COUNT\s*=\s*(\d+)", text)
    if not cpp_match or not syn_match:
        raise RuntimeError(
            "tests/conftest.py is missing EXPECTED_CPP_HANDLER_COUNT or "
            "EXPECTED_SYNTHETIC_TOOL_COUNT -- canonical numbers cannot be "
            "determined."
        )
    return int(cpp_match.group(1)), int(syn_match.group(1))


def _read_live_pytest_count() -> int:
    """Run `pytest --collect-only -q` and parse the trailing count."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    match = re.search(r"(\d+)\s+tests?\s+collected", result.stdout)
    if not match:
        raise RuntimeError(
            "Could not parse pytest --collect-only output:\n"
            + result.stdout
        )
    return int(match.group(1))


def canonical_numbers() -> dict[str, int]:
    """Build the canonical-numbers dict that PATTERNS validate against."""
    cpp, syn = _read_conftest_constants()
    return {
        "tools": cpp + syn,
        "cpp_handlers": cpp,
        "synthetic_tools": syn,
        "pytest_cases": _read_live_pytest_count(),
    }


def scan(canonical: dict[str, int]) -> list[str]:
    """Return one finding string per stale number across the scan list."""
    findings: list[str] = []
    for relpath in SCAN_FILES:
        path = REPO_ROOT / relpath
        if not path.exists():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        for lineno, line in enumerate(lines, start=1):
            for pattern, key in PATTERNS:
                for match in pattern.finditer(line):
                    found = int(match.group(1))
                    expected = canonical[key]
                    if found != expected:
                        findings.append(
                            f"{relpath}:{lineno}: '{match.group(0).strip()}' "
                            f"({key}={found}, expected {expected})"
                        )
    return findings


def main() -> int:
    canonical = canonical_numbers()
    findings = scan(canonical)
    if not findings:
        print(
            "doc-drift sweep: clean ("
            f"tools={canonical['tools']}, "
            f"cpp_handlers={canonical['cpp_handlers']}, "
            f"synthetic_tools={canonical['synthetic_tools']}, "
            f"pytest_cases={canonical['pytest_cases']})."
        )
        return 0
    print("doc-drift sweep: drift detected.")
    for finding in findings:
        print(f"  {finding}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
