"""Smoke tests for the CLI entry points.

These tests ensure the two `assassin.py` entry points respond to the `-h`
flag without throwing exceptions. The CLI modules have historically executed
code at import time, so having a regression suite for the entry scripts helps
catch similar bugs in the future.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_cli(script_relative_path: str) -> subprocess.CompletedProcess[str]:
    """Execute the CLI with ``-h`` and capture its output."""
    script_path = PROJECT_ROOT / script_relative_path
    return subprocess.run(
        [sys.executable, str(script_path), "-h"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


class AssassinCLITests(unittest.TestCase):
    """Basic behavioral checks for the CLI entry points."""

    def test_root_assassin_help(self) -> None:
        result = _run_cli("assassin.py")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("usage", result.stdout.lower())

    def test_package_assassin_help(self) -> None:
        result = _run_cli("2fassassin/assassin.py")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("usage", result.stdout.lower())


if __name__ == "__main__":  # pragma: no cover - convenience for local runs
    unittest.main()
