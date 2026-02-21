"""
AKF Phase 2.1 — Commit Gate
ADR-001: Validation Layer Architecture

Final safety lock. Deterministic. Boring and strict.

Does:
  - Final validation pass
  - schema_version enforcement (immutability)
  - Atomic file write

Does NOT:
  - Retry
  - Mutate document content
  - Normalize errors
  - Make decisions about what to fix
"""

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from akf.validation_error import ValidationError, Severity


SCHEMA_VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# Output contract
# ---------------------------------------------------------------------------

@dataclass
class CommitResult:
    """Outcome of a commit attempt."""
    committed: bool
    path: Optional[Path]          # set when committed=True
    blocking_errors: list[ValidationError]  # set when committed=False
    schema_version: str           # always set

    def __str__(self) -> str:
        if self.committed:
            return f"CommitResult(committed=True, path={self.path})"
        return (
            f"CommitResult(committed=False, "
            f"errors={len(self.blocking_errors)})"
        )


# ---------------------------------------------------------------------------
# Commit Gate
# ---------------------------------------------------------------------------

def commit(
    document: str,
    output_path: Path,
    errors: list[ValidationError],
    expected_schema_version: str = SCHEMA_VERSION,
) -> CommitResult:
    """
    Final gate before writing to disk.

    Args:
        document:                 Validated document string.
        output_path:              Target file path.
        errors:                   Errors from last validation pass.
        expected_schema_version:  Schema version to enforce (default: current).

    Returns:
        CommitResult with committed status and path or blocking errors.
    """
    # 1. Check for blocking errors
    blocking = [e for e in errors if e.severity == Severity.ERROR]
    if blocking:
        return CommitResult(
            committed=False,
            path=None,
            blocking_errors=blocking,
            schema_version=expected_schema_version,
        )

    # 2. Enforce schema_version immutability
    version_error = _check_schema_version(document, expected_schema_version)
    if version_error:
        return CommitResult(
            committed=False,
            path=None,
            blocking_errors=[version_error],
            schema_version=expected_schema_version,
        )

    # 3. Atomic write
    _atomic_write(document, output_path)

    return CommitResult(
        committed=True,
        path=output_path,
        blocking_errors=[],
        schema_version=expected_schema_version,
    )


# ---------------------------------------------------------------------------
# schema_version enforcement (deterministic)
# ---------------------------------------------------------------------------

def _check_schema_version(
    document: str,
    expected: str,
) -> Optional[ValidationError]:
    """
    Verify schema_version in document matches expected.

    schema_version is immutable at commit:
      - Required in document
      - Must match current active schema version
      - NOT auto-upgraded by retry loop
    """
    from akf.validation_error import ErrorCode, schema_violation

    # Extract schema_version from YAML frontmatter
    actual = _extract_schema_version(document)

    if actual is None:
        return schema_violation(
            field="schema_version",
            expected=expected,
            received="absent",
        )

    if actual != expected:
        return schema_violation(
            field="schema_version",
            expected=expected,
            received=actual,
        )

    return None


def _extract_schema_version(document: str) -> Optional[str]:
    """
    Extract schema_version value from YAML frontmatter.
    Returns None if not found.
    """
    in_frontmatter = False
    lines = document.splitlines()

    for i, line in enumerate(lines):
        stripped = line.strip()
        if i == 0 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter and stripped == "---":
            break  # end of frontmatter
        if in_frontmatter and stripped.startswith("schema_version:"):
            value = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            return value if value else None

    return None


# ---------------------------------------------------------------------------
# Atomic write (deterministic)
# ---------------------------------------------------------------------------

def _atomic_write(content: str, target: Path) -> None:
    """
    Write content to target path atomically.
    Uses temp file + rename to prevent partial writes.
    """
    target.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(
        dir=target.parent,
        prefix=".akf_tmp_",
        suffix=".md",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, target)  # atomic on POSIX
    except Exception:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
