"""
AKF Phase 2.2 — Validation Engine (Model C)
ADR-001: Validation Layer Architecture

Binary judgment: VALID or INVALID. No intermediate states.

Enforces:
  - Required fields (E002)
  - Enum fields: type, level, status (E001)
  - Domain taxonomy (E006)
  - Date format ISO 8601 (E003)
  - Tags array min 3 items (E004)

Changelog:
  - Fix: imports moved to module level (PEP 8, audit finding #1)
  - Fix: datetime.date handling in _check_dates (audit finding #2)

Canon-deferred (pending Canon revision, not to be implemented without ADR update):
  - CANON-DEFER-001: hard-coded enums → external config
    Reason: Canon §3.1 requires determinism. Config = new source of non-determinism.
    Revisit: Phase 2.4 Schema Evolution Tooling
  - CANON-DEFER-002: semantic constraint created ≤ updated
    Reason: requires new E-code and cross-field validation contract.
    Revisit: Phase 2.4
  - CANON-DEFER-003: isinstance check for title (str enforcement)
    Reason: minor, no E-code defined yet.
    Revisit: Phase 2.4
"""

import re
from datetime import date as DateType
from pathlib import Path
from typing import Any

import yaml

from akf.validation_error import (
    ErrorCode,
    Severity,
    ValidationError,
    invalid_date_format,
    invalid_enum,
    missing_field,
    taxonomy_violation,
    type_mismatch,
)

# ---------------------------------------------------------------------------
# Enum constraints (hard-coded, immutable)
# CANON-DEFER-001: intentionally hard-coded per Canon §3.1 (determinism).
# Do not move to config without Canon revision + ADR update.
# ---------------------------------------------------------------------------

VALID_TYPES = [
    "concept", "guide", "reference", "checklist",
    "project", "roadmap", "template", "audit",
]

VALID_LEVELS = ["beginner", "intermediate", "advanced"]

VALID_STATUSES = ["draft", "active", "completed", "archived"]

REQUIRED_FIELDS = [
    "title", "type", "domain", "level",
    "status", "tags", "created", "updated",
]

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

TAGS_MIN = 3

# ---------------------------------------------------------------------------
# Taxonomy loader
# ---------------------------------------------------------------------------

def _load_taxonomy(taxonomy_path: Path | None = None) -> list[str]:
    if taxonomy_path and taxonomy_path.exists():
        return _parse_taxonomy_file(taxonomy_path)
    return _default_taxonomy()


def _parse_taxonomy_file(path: Path) -> list[str]:
    domains = []
    pattern = re.compile(r"^####\s+([\w-]+)")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match and "(DEPRECATED" not in line:
            domains.append(match.group(1).strip())
    return sorted(set(domains)) if domains else _default_taxonomy()


def _default_taxonomy() -> list[str]:
    return sorted([
        "ai-system", "api-design", "backend-engineering",
        "business-strategy", "consulting", "data-engineering",
        "data-science", "devops", "documentation",
        "e-commerce", "education-tech", "finance",
        "finance-tech", "frontend-engineering", "healthcare",
        "infrastructure", "knowledge-management", "learning-systems",
        "machine-learning", "marketing", "operations",
        "product-management", "project-management", "prompt-engineering",
        "sales", "security", "system-design", "workflow-automation",
    ])


# ---------------------------------------------------------------------------
# Validation Engine
# ---------------------------------------------------------------------------

def validate(document: str, taxonomy_path: Path | None = None) -> list[ValidationError]:
    """
    Validate a Markdown document with YAML frontmatter.
    Returns list of ValidationError. Empty = VALID.
    """
    errors: list[ValidationError] = []

    metadata, parse_error = _parse_frontmatter(document)
    if parse_error:
        errors.append(parse_error)
        return errors

    valid_domains = _load_taxonomy(taxonomy_path)

    errors.extend(_check_required_fields(metadata))
    errors.extend(_check_enum_fields(metadata))
    errors.extend(_check_taxonomy(metadata, valid_domains))
    errors.extend(_check_dates(metadata))
    errors.extend(_check_tags(metadata))

    return errors


# ---------------------------------------------------------------------------
# Frontmatter parser
# ---------------------------------------------------------------------------

def _parse_frontmatter(document: str) -> tuple[dict, ValidationError | None]:
    """Parse YAML frontmatter block from Markdown document."""
    lines = document.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, ValidationError(
            code=ErrorCode.SCHEMA_VIOLATION,
            field="frontmatter",
            expected="--- YAML block ---",
            received="missing or malformed",
        )

    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break

    if end is None:
        return {}, ValidationError(
            code=ErrorCode.SCHEMA_VIOLATION,
            field="frontmatter",
            expected="closing ---",
            received="not found",
        )

    yaml_text = "\n".join(lines[1:end])
    try:
        metadata = yaml.safe_load(yaml_text) or {}
    except yaml.YAMLError as exc:
        return {}, ValidationError(
            code=ErrorCode.SCHEMA_VIOLATION,
            field="frontmatter",
            expected="valid YAML",
            received=str(exc),
        )

    return metadata, None


# ---------------------------------------------------------------------------
# Field checkers
# ---------------------------------------------------------------------------

def _check_required_fields(metadata: dict) -> list[ValidationError]:
    return [missing_field(f) for f in REQUIRED_FIELDS if f not in metadata]


def _check_enum_fields(metadata: dict) -> list[ValidationError]:
    errors = []
    checks = [
        ("type",   VALID_TYPES),
        ("level",  VALID_LEVELS),
        ("status", VALID_STATUSES),
    ]
    for field_name, valid_values in checks:
        value = metadata.get(field_name)
        if value is not None and value not in valid_values:
            errors.append(invalid_enum(field_name, valid_values, value))
    return errors


def _check_taxonomy(metadata: dict, valid_domains: list[str]) -> list[ValidationError]:
    domain = metadata.get("domain")
    if domain is not None and domain not in valid_domains:
        return [taxonomy_violation("domain", domain, valid_domains)]
    return []


def _check_dates(metadata: dict) -> list[ValidationError]:
    """
    Validate ISO 8601 date fields.

    Fix (audit finding #2): PyYAML parses unquoted YYYY-MM-DD values as
    datetime.date objects, not strings. We handle both cases explicitly
    rather than relying on str() conversion as accidental correctness.
    """
    errors = []
    for field_name in ("created", "updated"):
        value = metadata.get(field_name)
        if value is None:
            continue
        # PyYAML auto-converts unquoted YYYY-MM-DD → datetime.date
        # That is a valid date by definition — accept it explicitly.
        if isinstance(value, DateType):
            continue
        # All other types must match the string pattern
        if not DATE_PATTERN.match(str(value)):
            errors.append(invalid_date_format(field_name, str(value)))
    return errors


def _check_tags(metadata: dict) -> list[ValidationError]:
    """Validate tags field: must be a list with >= TAGS_MIN items."""
    tags = metadata.get("tags")
    if tags is None:
        return []
    if not isinstance(tags, list):
        return [type_mismatch("tags", list, tags)]
    if len(tags) < TAGS_MIN:
        return [ValidationError(
            code=ErrorCode.TYPE_MISMATCH,
            field="tags",
            expected=f"list with >= {TAGS_MIN} items",
            received=f"list with {len(tags)} items",
        )]
    return []
