#!/usr/bin/env python3
"""YAML Metadata Validator for AI Knowledge Filler.

This module validates Markdown files against the Metadata_Template_Standard,
checking for proper YAML frontmatter, required fields, and valid enum values.

Example:
    Run validation on all Markdown files in the repository:

        $ python validate_yaml.py

Exit codes:
    0: All files valid
    1: One or more files have validation errors
"""

import yaml
import glob
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Any, Dict

# Valid enum values
VALID_TYPES: List[str] = [
    "concept",
    "guide",
    "reference",
    "checklist",
    "project",
    "roadmap",
    "template",
    "audit",
]
VALID_LEVELS: List[str] = ["beginner", "intermediate", "advanced"]
VALID_STATUSES: List[str] = ["draft", "active", "completed", "archived"]

# Valid domains
VALID_DOMAINS: List[str] = [
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


def validate_date_format(date_str: Any) -> bool:
    """Validate date string against ISO 8601 format (YYYY-MM-DD).

    Args:
        date_str: Date string to validate. Can be any type, will be converted to string.

    Returns:
        True if date string matches YYYY-MM-DD format, False otherwise.

    Example:
        >>> validate_date_format('2025-02-12')
        True
        >>> validate_date_format('02-12-2025')
        False
    """
    try:
        datetime.strptime(str(date_str), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_file(filepath: str) -> Tuple[List[str], List[str]]:
    """Validate a single Markdown file's YAML metadata.

    Checks for:
        - YAML frontmatter presence
        - Required metadata fields
        - Valid enum values (type, level, status)
        - Proper domain classification
        - Date format compliance
        - Tag and related fields structure

    Args:
        filepath: Path to the Markdown file to validate.

    Returns:
        A tuple of (errors, warnings):
            - errors: List of validation errors (blocking issues)
            - warnings: List of warnings (non-blocking suggestions)

    Example:
        >>> errors, warnings = validate_file('example.md')
        >>> if not errors:
        ...     print('File is valid')
    """
    errors: List[str] = []
    warnings: List[str] = []

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Check for YAML frontmatter
    if not content.startswith("---"):
        return ["No YAML frontmatter found"], []

    try:
        # Extract and parse YAML
        parts = content.split("---")
        if len(parts) < 3:
            return ["Invalid YAML frontmatter structure"], []

        yaml_content = parts[1]
        metadata: Dict[str, Any] = yaml.safe_load(yaml_content)

        if not metadata:
            return ["Empty YAML frontmatter"], []

        # Required fields
        required_fields: List[str] = [
            "title",
            "type",
            "domain",
            "level",
            "status",
            "created",
            "updated",
        ]
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing required field: {field}")

        # Validate type
        if "type" in metadata and metadata["type"] not in VALID_TYPES:
            errors.append(
                f"Invalid type: {metadata['type']}. " f"Must be one of: {', '.join(VALID_TYPES)}"
            )

        # Validate level
        if "level" in metadata and metadata["level"] not in VALID_LEVELS:
            errors.append(
                f"Invalid level: {metadata['level']}. " f"Must be one of: {', '.join(VALID_LEVELS)}"
            )

        # Validate status
        if "status" in metadata and metadata["status"] not in VALID_STATUSES:
            errors.append(
                f"Invalid status: {metadata['status']}. "
                f"Must be one of: {', '.join(VALID_STATUSES)}"
            )

        # Validate domain
        if "domain" in metadata and metadata["domain"] not in VALID_DOMAINS:
            warnings.append(f"Domain '{metadata['domain']}' not in standard taxonomy")

        # Validate dates
        if "created" in metadata and not validate_date_format(metadata["created"]):
            errors.append(f"Invalid created date format: {metadata['created']}. Use YYYY-MM-DD")

        if "updated" in metadata and not validate_date_format(metadata["updated"]):
            errors.append(f"Invalid updated date format: {metadata['updated']}. Use YYYY-MM-DD")

        # Validate tags is array
        if "tags" in metadata and not isinstance(metadata["tags"], list):
            errors.append("Tags must be an array")

        # Validate related is array (if present)
        if "related" in metadata and metadata["related"] is not None:
            if not isinstance(metadata["related"], list):
                errors.append("Related must be an array or null")

        # Warnings for best practices
        if "tags" in metadata and len(metadata["tags"]) < 3:
            warnings.append("Fewer than 3 tags (recommended: 3-10)")

        if "related" not in metadata or not metadata["related"]:
            warnings.append("No related links (recommended for knowledge graph)")

    except yaml.YAMLError as e:
        errors.append(f"YAML parsing error: {str(e)}")
    except Exception as e:
        errors.append(f"Unexpected error: {str(e)}")

    return errors, warnings


def main() -> None:
    """Run validation on all Markdown files in the repository.

    Scans the current directory recursively for .md files (excluding
    .github, README.md, and CONTRIBUTING.md), validates each file's
    metadata, and reports results.

    Prints validation summary and exits with appropriate code:
        - Exit 0: All files valid
        - Exit 1: One or more files have errors

    Output includes:
        - Per-file validation status (✅/⚠️/❌)
        - Detailed error and warning messages
        - Summary statistics
    """
    print("🔍 AI Knowledge Filler - YAML Metadata Validator\n")

    all_files: List[str] = glob.glob("**/*.md", recursive=True)

    # Filter out README and GitHub files
    md_files: List[str] = [
        f for f in all_files if not any(x in f for x in [".github", "README.md", "CONTRIBUTING.md"])
    ]

    total_files: int = len(md_files)
    valid_files: int = 0
    files_with_errors: int = 0
    files_with_warnings: int = 0

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

    print(f"\n📊 Validation Summary:")
    print(f"   Total files: {total_files}")
    print(f"   ✅ Valid: {valid_files}")
    print(f"   ⚠️  Warnings: {files_with_warnings}")
    print(f"   ❌ Errors: {files_with_errors}")

    if files_with_errors > 0:
        print(f"\n❌ Validation failed: {files_with_errors} file(s) with errors")
        sys.exit(1)
    else:
        print(f"\n✅ All files valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
