"""
Tests for AKF Phase 2.1 — Commit Gate (S4)
ADR-001: Validation Layer Architecture
"""

import pytest
from pathlib import Path
from akf.commit_gate import commit, CommitResult, SCHEMA_VERSION, _extract_schema_version
from akf.validation_error import (
    ValidationError, ErrorCode, Severity,
    missing_field, schema_violation,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_doc(schema_version: str = SCHEMA_VERSION, extra: str = "") -> str:
    return (
        f"---\n"
        f"title: Test Document\n"
        f"type: concept\n"
        f"domain: ai-system\n"
        f"schema_version: {schema_version}\n"
        f"---\n"
        f"## Content\n{extra}"
    )


def no_errors() -> list[ValidationError]:
    return []


def blocking_error() -> list[ValidationError]:
    return [missing_field("title")]


def warning_only() -> list[ValidationError]:
    return [
        ValidationError(
            code=ErrorCode.SCHEMA_VIOLATION,
            field="version",
            expected="vX.Y",
            received="1.0",
            severity=Severity.WARNING,
        )
    ]


# ---------------------------------------------------------------------------
# Commit success
# ---------------------------------------------------------------------------

class TestCommitSuccess:

    def test_commits_valid_document(self, tmp_path):
        doc = make_doc()
        result = commit(doc, tmp_path / "output.md", no_errors())
        assert result.committed is True
        assert result.path == tmp_path / "output.md"
        assert (tmp_path / "output.md").exists()

    def test_committed_file_contains_document(self, tmp_path):
        doc = make_doc(extra="unique content 12345")
        commit(doc, tmp_path / "output.md", no_errors())
        content = (tmp_path / "output.md").read_text()
        assert "unique content 12345" in content

    def test_warnings_do_not_block_commit(self, tmp_path):
        doc = make_doc()
        result = commit(doc, tmp_path / "output.md", warning_only())
        assert result.committed is True

    def test_creates_parent_directories(self, tmp_path):
        doc = make_doc()
        deep_path = tmp_path / "a" / "b" / "c" / "output.md"
        result = commit(doc, deep_path, no_errors())
        assert result.committed is True
        assert deep_path.exists()

    def test_schema_version_in_result(self, tmp_path):
        doc = make_doc()
        result = commit(doc, tmp_path / "output.md", no_errors())
        assert result.schema_version == SCHEMA_VERSION


# ---------------------------------------------------------------------------
# Commit blocked by errors
# ---------------------------------------------------------------------------

class TestCommitBlocked:

    def test_blocking_error_prevents_commit(self, tmp_path):
        doc = make_doc()
        result = commit(doc, tmp_path / "output.md", blocking_error())
        assert result.committed is False
        assert not (tmp_path / "output.md").exists()

    def test_blocking_error_returns_errors(self, tmp_path):
        doc = make_doc()
        result = commit(doc, tmp_path / "output.md", blocking_error())
        assert len(result.blocking_errors) == 1
        assert result.blocking_errors[0].code == ErrorCode.MISSING_FIELD

    def test_path_is_none_when_not_committed(self, tmp_path):
        doc = make_doc()
        result = commit(doc, tmp_path / "output.md", blocking_error())
        assert result.path is None


# ---------------------------------------------------------------------------
# schema_version enforcement
# ---------------------------------------------------------------------------

class TestSchemaVersionEnforcement:

    def test_missing_schema_version_blocks_commit(self, tmp_path):
        doc = "---\ntitle: Test\ntype: concept\n---\n## Content"
        result = commit(doc, tmp_path / "output.md", no_errors())
        assert result.committed is False
        assert any(
            e.field == "schema_version" for e in result.blocking_errors
        )

    def test_wrong_schema_version_blocks_commit(self, tmp_path):
        doc = make_doc(schema_version="0.0.1")
        result = commit(doc, tmp_path / "output.md", no_errors())
        assert result.committed is False
        assert any(
            e.field == "schema_version" for e in result.blocking_errors
        )

    def test_correct_schema_version_passes(self, tmp_path):
        doc = make_doc(schema_version=SCHEMA_VERSION)
        result = commit(doc, tmp_path / "output.md", no_errors())
        assert result.committed is True

    def test_schema_version_not_auto_upgraded(self, tmp_path):
        """Commit gate does not rewrite schema_version — it enforces or rejects."""
        doc = make_doc(schema_version="0.9.9")
        result = commit(doc, tmp_path / "output.md", no_errors())
        assert result.committed is False
        # File must NOT exist — gate did not write and silently upgrade
        assert not (tmp_path / "output.md").exists()


# ---------------------------------------------------------------------------
# _extract_schema_version helper
# ---------------------------------------------------------------------------

class TestExtractSchemaVersion:

    def test_extracts_version_from_frontmatter(self):
        doc = make_doc(schema_version="1.0.0")
        assert _extract_schema_version(doc) == "1.0.0"

    def test_returns_none_when_missing(self):
        doc = "---\ntitle: Test\n---\ncontent"
        assert _extract_schema_version(doc) is None

    def test_handles_quoted_value(self):
        doc = '---\nschema_version: "1.0.0"\n---\ncontent'
        assert _extract_schema_version(doc) == "1.0.0"

    def test_ignores_version_outside_frontmatter(self):
        doc = "---\ntitle: Test\n---\nschema_version: 9.9.9"
        assert _extract_schema_version(doc) is None


# ---------------------------------------------------------------------------
# CommitResult contract
# ---------------------------------------------------------------------------

class TestCommitResultContract:

    def test_str_success(self, tmp_path):
        doc = make_doc()
        result = commit(doc, tmp_path / "output.md", no_errors())
        assert "committed=True" in str(result)

    def test_str_failure(self, tmp_path):
        doc = make_doc()
        result = commit(doc, tmp_path / "output.md", blocking_error())
        assert "committed=False" in str(result)

    def test_no_blocking_errors_on_success(self, tmp_path):
        doc = make_doc()
        result = commit(doc, tmp_path / "output.md", no_errors())
        assert result.blocking_errors == []
