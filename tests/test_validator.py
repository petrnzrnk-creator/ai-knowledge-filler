"""
Tests for AKF Phase 2.2 — Validation Engine (Model C)
"""

import pytest
from akf.validator import validate, _load_taxonomy, _default_taxonomy
from akf.validation_error import ErrorCode


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_DOC = """\
---
title: "Test Document"
type: concept
domain: ai-system
level: intermediate
status: active
tags: [test, ai, obsidian]
created: 2026-02-22
updated: 2026-02-22
---

## Overview

Test content.
"""

# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_valid_document_returns_no_errors():
    errors = validate(VALID_DOC)
    assert errors == []


def test_all_valid_types():
    valid_types = ["concept", "guide", "reference", "checklist",
                   "project", "roadmap", "template", "audit"]
    for t in valid_types:
        doc = VALID_DOC.replace("type: concept", f"type: {t}")
        errors = validate(doc)
        type_errors = [e for e in errors if e.field == "type"]
        assert type_errors == [], f"type={t} should be valid"


def test_all_valid_levels():
    for level in ["beginner", "intermediate", "advanced"]:
        doc = VALID_DOC.replace("level: intermediate", f"level: {level}")
        errors = validate(doc)
        level_errors = [e for e in errors if e.field == "level"]
        assert level_errors == [], f"level={level} should be valid"


def test_all_valid_statuses():
    for status in ["draft", "active", "completed", "archived"]:
        doc = VALID_DOC.replace("status: active", f"status: {status}")
        errors = validate(doc)
        status_errors = [e for e in errors if e.field == "status"]
        assert status_errors == [], f"status={status} should be valid"


# ---------------------------------------------------------------------------
# Missing fields — E002
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("field", [
    "title", "type", "domain", "level", "status", "tags", "created", "updated"
])
def test_missing_required_field(field):
    lines = [l for l in VALID_DOC.splitlines() if not l.startswith(f"{field}:")]
    doc = "\n".join(lines)
    errors = validate(doc)
    codes = [e.code for e in errors]
    assert ErrorCode.MISSING_FIELD in codes
    missing = [e for e in errors if e.field == field]
    assert missing, f"Expected missing_field error for '{field}'"


# ---------------------------------------------------------------------------
# Enum violations — E001
# ---------------------------------------------------------------------------

def test_invalid_type_returns_e001():
    doc = VALID_DOC.replace("type: concept", "type: document")
    errors = validate(doc)
    assert any(e.code == ErrorCode.INVALID_ENUM and e.field == "type" for e in errors)


def test_invalid_level_returns_e001():
    doc = VALID_DOC.replace("level: intermediate", "level: expert")
    errors = validate(doc)
    assert any(e.code == ErrorCode.INVALID_ENUM and e.field == "level" for e in errors)


def test_invalid_status_returns_e001():
    doc = VALID_DOC.replace("status: active", "status: in-progress")
    errors = validate(doc)
    assert any(e.code == ErrorCode.INVALID_ENUM and e.field == "status" for e in errors)


def test_invalid_enum_includes_valid_values_in_expected():
    doc = VALID_DOC.replace("type: concept", "type: note")
    errors = validate(doc)
    enum_errors = [e for e in errors if e.field == "type"]
    assert enum_errors
    assert "concept" in enum_errors[0].expected


# ---------------------------------------------------------------------------
# Taxonomy violations — E006
# ---------------------------------------------------------------------------

def test_invalid_domain_returns_e006():
    doc = VALID_DOC.replace("domain: ai-system", "domain: technology")
    errors = validate(doc)
    assert any(e.code == ErrorCode.TAXONOMY_VIOLATION and e.field == "domain" for e in errors)


def test_invalid_domain_includes_valid_list():
    doc = VALID_DOC.replace("domain: ai-system", "domain: backend")
    errors = validate(doc)
    tax_errors = [e for e in errors if e.field == "domain"]
    assert tax_errors
    assert isinstance(tax_errors[0].expected, list)
    assert len(tax_errors[0].expected) > 0


def test_all_default_taxonomy_domains_are_valid():
    for domain in _default_taxonomy():
        doc = VALID_DOC.replace("domain: ai-system", f"domain: {domain}")
        errors = validate(doc)
        domain_errors = [e for e in errors if e.field == "domain"]
        assert domain_errors == [], f"domain={domain} should be valid"


# ---------------------------------------------------------------------------
# Date format — E003
# ---------------------------------------------------------------------------

def test_invalid_created_date_format():
    doc = VALID_DOC.replace("created: 2026-02-22", "created: 22-02-2026")
    errors = validate(doc)
    assert any(e.code == ErrorCode.INVALID_DATE_FORMAT and e.field == "created" for e in errors)


def test_invalid_updated_date_format():
    doc = VALID_DOC.replace("updated: 2026-02-22", "updated: 2026/02/22")
    errors = validate(doc)
    assert any(e.code == ErrorCode.INVALID_DATE_FORMAT and e.field == "updated" for e in errors)


def test_valid_date_format_passes():
    errors = validate(VALID_DOC)
    date_errors = [e for e in errors if e.code == ErrorCode.INVALID_DATE_FORMAT]
    assert date_errors == []


# ---------------------------------------------------------------------------
# Tags — E004
# ---------------------------------------------------------------------------

def test_tags_not_array_returns_type_mismatch():
    doc = VALID_DOC.replace("tags: [test, ai, obsidian]", "tags: just-a-string")
    errors = validate(doc)
    assert any(e.code == ErrorCode.TYPE_MISMATCH and e.field == "tags" for e in errors)


def test_tags_fewer_than_3_returns_error():
    doc = VALID_DOC.replace("tags: [test, ai, obsidian]", "tags: [test]")
    errors = validate(doc)
    assert any(e.field == "tags" for e in errors)


def test_tags_exactly_3_is_valid():
    doc = VALID_DOC.replace("tags: [test, ai, obsidian]", "tags: [a, b, c]")
    errors = validate(doc)
    tag_errors = [e for e in errors if e.field == "tags"]
    assert tag_errors == []


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

def test_missing_frontmatter_returns_schema_violation():
    doc = "## No frontmatter here\n\nJust content."
    errors = validate(doc)
    assert any(e.code == ErrorCode.SCHEMA_VIOLATION and e.field == "frontmatter" for e in errors)


def test_unclosed_frontmatter_returns_schema_violation():
    doc = "---\ntitle: Test\ntype: concept\n## No closing dashes"
    errors = validate(doc)
    assert any(e.code == ErrorCode.SCHEMA_VIOLATION for e in errors)


def test_invalid_yaml_returns_schema_violation():
    doc = "---\ntitle: [unclosed bracket\n---\n## Content"
    errors = validate(doc)
    assert any(e.code == ErrorCode.SCHEMA_VIOLATION for e in errors)


# ---------------------------------------------------------------------------
# Taxonomy loader
# ---------------------------------------------------------------------------

def test_default_taxonomy_returns_sorted_list():
    taxonomy = _default_taxonomy()
    assert taxonomy == sorted(taxonomy)
    assert len(taxonomy) > 10


def test_load_taxonomy_without_path_returns_default():
    taxonomy = _load_taxonomy(None)
    assert "ai-system" in taxonomy
    assert "devops" in taxonomy


def test_load_taxonomy_nonexistent_path_returns_default(tmp_path):
    taxonomy = _load_taxonomy(tmp_path / "nonexistent.md")
    assert "ai-system" in taxonomy


def test_load_taxonomy_from_file(tmp_path):
    taxonomy_file = tmp_path / "Domain_Taxonomy.md"
    taxonomy_file.write_text(
        "#### custom-domain\nSome description\n#### another-domain\n"
    )
    taxonomy = _load_taxonomy(taxonomy_file)
    assert "custom-domain" in taxonomy
    assert "another-domain" in taxonomy


def test_taxonomy_file_skips_deprecated(tmp_path):
    taxonomy_file = tmp_path / "Domain_Taxonomy.md"
    taxonomy_file.write_text(
        "#### valid-domain\n#### old-domain (DEPRECATED → valid-domain)\n"
    )
    taxonomy = _load_taxonomy(taxonomy_file)
    assert "valid-domain" in taxonomy
    assert "old-domain" not in taxonomy


# ---------------------------------------------------------------------------
# Multiple errors
# ---------------------------------------------------------------------------

def test_multiple_errors_returned_together():
    doc = """\
---
title: "Test"
type: invalid-type
domain: not-a-domain
level: expert
status: active
tags: [a]
created: 2026-02-22
updated: 2026-02-22
---

## Content
"""
    errors = validate(doc)
    codes = [e.code for e in errors]
    assert ErrorCode.INVALID_ENUM in codes       # type
    assert ErrorCode.TAXONOMY_VIOLATION in codes  # domain
    assert ErrorCode.INVALID_ENUM in codes        # level
    assert len(errors) >= 3
