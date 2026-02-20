#!/usr/bin/env python3
"""YAML Metadata Validator for AI Knowledge Filler.

This module validates Markdown files against the Metadata Template Standard
defined in the AI Knowledge Filler system. It checks for required fields,
valid enum values, proper date formats, and structural compliance.

Example:
    Run validation on all Markdown files in the repository::

        $ python validate_yaml.py

    The script will output validation results for each file and exit with
    code 0 if all files are valid, or code 1 if any errors are found.

Attributes:
    VALID_TYPES (list): Valid values for the 'type' metadata field.
    VALID_LEVELS (list): Valid values for the 'level' metadata field.
    VALID_STATUSES (list): Valid values for the 'status' metadata field.
    VALID_DOMAINS (list): Valid values for the 'domain' metadata field.
"""

import glob
import sys
from datetime import datetime
from typing import List, Tuple

import yaml

# Valid enum values
VALID_TYPES = [
    "concept",
    "guide",
    "reference",
    "checklist",
    "project",
    "roadmap",
    "template",
    "audit",
]
VALID_LEVELS = ["beginner", "intermediate", "advanced"]
VALID_STATUSES = ["draft", "active", "completed", "archived"]

# Valid domains (extend as needed)
VALID_DOMAINS = [
    "ai-system",
    "system-design",
    "api-design",
    "data-engineering",
    "security",
    "devops",
    "product-management",
    "consulting",
    "workflow-automation",
    "prompt-engineering",
    "business-strategy",
    "project-management",
    "knowledge-management",
    "documentation",
    "frontend-engineering",
    "backend-engineering",
    "infrastructure",
    "machine-learning",
    "data-science",
]


def validate_date_format(date_str: str) -> bool:
    """Validate that a date string is in ISO 8601 format (YYYY-MM-DD).

    Args:
        date_str: The date string to validate.

    Returns:
        True if the date is in valid ISO 8601 format, False otherwise.

    Example:
        >>> validate_date_format("2025-02-12")
        True
        >>> validate_date_format("12-02-2025")
        False
    """
    try:
        datetime.strptime(str(date_str), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _validate_enum_fields(metadata: dict, errors: List[str], warnings: List[str]) -> None:
    """Validate enum fields: type, level, status, domain."""
    if "type" in metadata and metadata["type"] not in VALID_TYPES:
        errors.append(
            f"Invalid type: {metadata['type']}. " f"Must be one of: {', '.join(VALID_TYPES)}"
        )

    if "level" in metadata and metadata["level"] not in VALID_LEVELS:
        errors.append(
            f"Invalid level: {metadata['level']}. " f"Must be one of: {', '.join(VALID_LEVELS)}"
        )

    if "status" in metadata and metadata["status"] not in VALID_STATUSES:
        errors.append(
            f"Invalid status: {metadata['status']}. " f"Must be one of: {', '.join(VALID_STATUSES)}"
        )

    if "domain" in metadata and metadata["domain"] not in VALID_DOMAINS:
        warnings.append(f"Domain '{metadata['domain']}' not in standard taxonomy")


def _validate_dates(metadata: dict, errors: List[str]) -> None:
    """Validate created and updated date fields."""
    if "created" in metadata and not validate_date_format(metadata["created"]):
        errors.append(f"Invalid created date format: {metadata['created']}. Use YYYY-MM-DD")

    if "updated" in metadata and not validate_date_format(metadata["updated"]):
        errors.append(f"Invalid updated date format: {metadata['updated']}. Use YYYY-MM-DD")


def _validate_arrays(metadata: dict, errors: List[str], warnings: List[str]) -> None:
    """Validate tags and related array fields."""
    if "tags" in metadata and not isinstance(metadata["tags"], list):
        errors.append("Tags must be an array")

    if "related" in metadata and metadata["related"] is not None:
        if not isinstance(metadata["related"], list):
            errors.append("Related must be an array or null")

    if "tags" in metadata and isinstance(metadata["tags"], list) and len(metadata["tags"]) < 3:
        warnings.append("Fewer than 3 tags (recommended: 3-10)")

    if "related" not in metadata or not metadata["related"]:
        warnings.append("No related links (recommended for knowledge graph)")


def _parse_frontmatter(content: str) -> Tuple[dict, List[str]]:
    """Extract and parse YAML frontmatter from Markdown content."""
    errors: List[str] = []

    if not content.startswith("---"):
        return {}, ["No YAML frontmatter found"]

    parts = content.split("---")
    if len(parts) < 3:
        return {}, ["Invalid YAML frontmatter structure"]

    metadata = yaml.safe_load(parts[1])
    if not metadata:
        return {}, ["Empty YAML frontmatter"]

    return metadata, errors


def validate_file(filepath: str) -> Tuple[List[str], List[str]]:
    """Validate a single Markdown file's YAML frontmatter.

    Checks for:
        - Presence of YAML frontmatter
        - All required metadata fields
        - Valid enum values for type, level, status, domain
        - Correct date formats (ISO 8601)
        - Proper data types (arrays for tags/related)

    Args:
        filepath: Path to the Markdown file to validate.

    Returns:
        A tuple containing two lists:
            - errors: Critical validation failures
            - warnings: Non-critical issues and best practice violations

    Example:
        >>> errors, warnings = validate_file("example.md")
        >>> if not errors:
        ...     print("File is valid!")
    """
    errors: List[str] = []
    warnings: List[str] = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (IOError, OSError) as e:
        return [f"Cannot read file: {e}"], []

    try:
        metadata, parse_errors = _parse_frontmatter(content)
        if parse_errors:
            return parse_errors, []

        required_fields = ["title", "type", "domain", "level", "status", "created", "updated"]
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing required field: {field}")

        _validate_enum_fields(metadata, errors, warnings)
        _validate_dates(metadata, errors)
        _validate_arrays(metadata, errors, warnings)

    except yaml.YAMLError as e:
        errors.append(f"YAML parsing error: {str(e)}")
    except Exception as e:
        errors.append(f"Unexpected error: {str(e)}")

    return errors, warnings


def main() -> None:
    """Execute validation on all Markdown files in the repository.

    Scans for .md files recursively, excludes system files (README, .github),
    validates each file, and outputs results with color-coded status indicators.

    Exit codes:
        0: All files valid
        1: One or more files have validation errors

    Example:
        >>> main()
        🔍 AI Knowledge Filler - YAML Metadata Validator

        ✅ example.md
        ❌ invalid.md
           ERROR: Missing required field: title

        📊 Validation Summary:
           Total files: 2
           ✅ Valid: 1
           ❌ Errors: 1
    """
    print("🔍 AI Knowledge Filler - YAML Metadata Validator\n")

    all_files = glob.glob("**/*.md", recursive=True)

    md_files = [
        f for f in all_files if not any(x in f for x in [".github", "README.md", "CONTRIBUTING.md", "ARCHITECTURE.md"])
    ]

    total_files = len(md_files)
    valid_files = 0
    files_with_errors = 0
    files_with_warnings = 0

    for filepath in sorted(md_files):
        errors, warnings = validate_file(filepath)

        if errors:
            files_with_errors += 1
            print(f"❌ {filepath}")
            for error in errors:
                print(f"   ERROR: {error}")
        elif warnings:
            files_with_warnings += 1
            print(f"⚠️  {filepath}")
            for warning in warnings:
                print(f"   WARNING: {warning}")
        else:
            valid_files += 1
            print(f"✅ {filepath}")

    print("\n📊 Validation Summary:")
    print(f"   Total files: {total_files}")
    print(f"   ✅ Valid: {valid_files}")
    print(f"   ⚠️  Warnings: {files_with_warnings}")
    print(f"   ❌ Errors: {files_with_errors}")

    if files_with_errors > 0:
        print(f"\n❌ Validation failed: {files_with_errors} file(s) with errors")
        sys.exit(1)
    else:
        print("\n✅ All files valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
