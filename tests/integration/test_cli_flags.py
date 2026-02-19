"""Integration tests for Phase 1.6 CLI flags: --strict and --path.

Placed in integration/ so cli.py is included in coverage measurement.
"""

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

# ─── PATHS ───────────────────────────────────────────────────────────────────

# tests/integration/ → tests/ → project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
CLI_PATH = str(PROJECT_ROOT / "cli.py")

VALID_FM = textwrap.dedent("""\
    ---
    title: "Test File"
    type: concept
    domain: ai-system
    level: intermediate
    status: active
    tags: [ai, test, validation]
    related:
      - "[[Valid Link]]"
      - "[[Another Link]]"
    created: 2026-02-19
    updated: 2026-02-19
    ---

    ## Overview

    Content here.
""")

# Valid YAML but missing related → produces warning
WARN_FM = textwrap.dedent("""\
    ---
    title: "Test"
    type: concept
    domain: ai-system
    level: intermediate
    status: active
    tags: [a, b, c]
    created: 2026-02-19
    updated: 2026-02-19
    ---

    ## Content
""")

BAD_FM = textwrap.dedent("""\
    ---
    title: "Bad"
    type: INVALID_TYPE
    domain: ai-system
    level: intermediate
    status: active
    tags: [a, b, c]
    created: 2026-02-19
    updated: 2026-02-19
    ---

    ## Content
""")


# ─── HELPERS ─────────────────────────────────────────────────────────────────


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, CLI_PATH] + list(args),
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )


# ─── TESTS ───────────────────────────────────────────────────────────────────


class TestCLIValidateStrict:
    """Tests for akf validate --strict flag."""

    def test_strict_flag_promotes_warnings_to_errors(self, tmp_path):
        """--strict: file with only warnings → exit 1."""
        f = tmp_path / "warn.md"
        f.write_text(WARN_FM)
        result = run_cli("validate", "--file", str(f), "--strict")
        assert result.returncode == 1

    def test_no_strict_warnings_exit_zero(self, tmp_path):
        """Without --strict: file with only warnings → exit 0."""
        f = tmp_path / "warn.md"
        f.write_text(WARN_FM)
        result = run_cli("validate", "--file", str(f))
        assert result.returncode == 0

    def test_strict_valid_file_exits_zero(self, tmp_path):
        """--strict: fully valid file → exit 0."""
        f = tmp_path / "valid.md"
        f.write_text(VALID_FM)
        result = run_cli("validate", "--file", str(f), "--strict")
        assert result.returncode == 0

    def test_strict_real_errors_exit_one(self, tmp_path):
        """--strict: file with real errors → exit 1 regardless."""
        f = tmp_path / "bad.md"
        f.write_text(BAD_FM)
        result = run_cli("validate", "--file", str(f), "--strict")
        assert result.returncode == 1


class TestCLIValidatePath:
    """Tests for akf validate --path flag (folder scan)."""

    def test_path_all_valid_exits_zero(self, tmp_path):
        (tmp_path / "valid.md").write_text(VALID_FM)
        result = run_cli("validate", "--path", str(tmp_path))
        assert result.returncode == 0

    def test_path_with_error_exits_one(self, tmp_path):
        (tmp_path / "valid.md").write_text(VALID_FM)
        (tmp_path / "bad.md").write_text(BAD_FM)
        result = run_cli("validate", "--path", str(tmp_path))
        assert result.returncode == 1

    def test_path_error_output_names_bad_file(self, tmp_path):
        (tmp_path / "valid.md").write_text(VALID_FM)
        (tmp_path / "bad.md").write_text(BAD_FM)
        result = run_cli("validate", "--path", str(tmp_path))
        combined = result.stdout + result.stderr
        assert "bad.md" in combined

    def test_path_recursive_finds_nested_files(self, tmp_path):
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested_bad.md").write_text(BAD_FM)
        result = run_cli("validate", "--path", str(tmp_path))
        assert result.returncode == 1

    def test_path_strict_combines_with_folder(self, tmp_path):
        """--path + --strict: folder with warn-only file → exit 1."""
        (tmp_path / "warn.md").write_text(WARN_FM)
        result = run_cli("validate", "--path", str(tmp_path), "--strict")
        assert result.returncode == 1
