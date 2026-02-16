#!/usr/bin/env python3
"""YAML Metadata Validator for AI Knowledge Filler.

This module validates Markdown files against the Metadata Template Standard
defined in the AI Knowledge Filler system. It checks for required fields,
valid enum values, proper date formats, and structural compliance.

Domains are loaded dynamically from Domain_Taxonomy.md (the single source
of truth), falling back to a hardcoded list if the file is not found.

Example:
    Run validation on all Markdown files in the repository::

        $ python validate_yaml.py

    The script will output validation results for each file and exit with
    code 0 if all files are valid, or code 1 if any errors are found.

Attributes:
    VALID_TYPES (list): Valid values for the 'type' metadata field.
    VALID_LEVELS (list): Valid values for the 'level' metadata field.
    VALID_STATUSES (list): Valid values for the 'status' metadata field.
    TAXONOMY_FILENAME (str): Filename of the domain taxonomy source of truth.
"""

import glob
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import yaml

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

TAXONOMY_FILENAME = "Domain_Taxonomy.md"

# Fallback if Domain_Taxonomy.md not found
_FALLBACK_DOMAINS = [
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
    "learning-systems",
    "frontend-engineering",
    "backend-engineering",
    "infrastructure",
    "machine-learning",
    "data-science",
    "operations",
    "finance",
    "marketing",
    "sales",
    "healthcare",
    "finance-tech",
    "education-tech",
    "e-commerce",
]


def load_domains_from_taxonomy(taxonomy_path: Optional[str] = None) -> List[str]:
    """Load valid domain values from Domain_Taxonomy.md.

    Searches for Domain_Taxonomy.md starting from the current directory
    and walking up to the repository root. Falls back to the hardcoded
    list if the file cannot be found or parsed.

    Args:
        taxonomy_path: Optional explicit path to Domain_Taxonomy.md.
            If not provided, searches automatically.

    Returns:
        List of valid domain strings extracted from the taxonomy file,
        or the fallback list if the file is not found.

    Example:
        >>> domains = load_domains_from_taxonomy()
        >>> "ai-system" in domains
        True
    """
    search_path = None

    if taxonomy_path:
        search_path = Path(taxonomy_path)
    else:
        # Search from cwd upward
        for parent in [Path.cwd()] + list(Path.cwd().parents):
            candidate = parent / TAXONOMY_FILENAME
            if candidate.exists():
                search_path = candidate
                break
        # Also search recursively under cwd
        if not search_path:
            matches = list(Path.cwd().rglob(TAXONOMY_FILENAME))
            if matches:
                search_path = matches[0]

    if not search_path or not search_path.exists():
        print(
            f"⚠️  {TAXONOMY_FILENAME} not found — using fallback domain list",
            file=sys.stderr,
        )
        return _FALLBACK_DOMAINS

    try:
        content = search_path.read_text(encoding="utf-8")
        domains = _parse_domains_from_taxonomy(content)
        if domains:
            print(
                f"📚 Loaded {len(domains)} domains from {search_path}",
                file=sys.stderr,
            )
            return domains
        else:
            print(
                f"⚠️  No domains parsed from {search_path} — using fallback",
                file=sys.stderr,
            )
            return _FALLBACK_DOMAINS
    except (IOError, OSError) as e:
        print(
            f"⚠️  Cannot read {TAXONOMY_FILENAME}: {e} — using fallback",
            file=sys.stderr,
        )
        return _FALLBACK_DOMAINS


def _parse_domains_from_taxonomy(content: str) -> List[str]:
    """Extract domain identifiers from Domain_Taxonomy.md content.

    Parses #### headings in the TAXONOMY STRUCTURE section.
    Only extracts lowercase-hyphenated identifiers, skipping
    section headers like "Core Domains" and deprecated entries.

    Args:
        content: Full text content of Domain_Taxonomy.md.

    Returns:
        Sorted list of unique domain identifier strings.

    Example:
        >>> content = "#### ai-system\\nDescription\\n#### api-design\\n"
        >>> _parse_domains_from_taxonomy(content)
        ['ai-design', 'ai-system']
    """
    domains: List[str] = []

    # Match #### headings that look like domain identifiers:
    # lowercase, hyphens allowed, no spaces — e.g. "#### ai-system"
    # Excludes bolded section headers like "#### **Core Domains**"
    # and deprecated markers like "#### legacy-domain (DEPRECATED → new)"
    pattern = re.compile(r"^####\s+([a-z][a-z0-9-]+)\s*$", re.MULTILINE)

    for match in pattern.finditer(content):
        domain = match.group(1).strip()
        if domain not in domains:
            domains.append(domain)

    return sorted(domains)


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


def _validate_enum_fields(
    metadata: dict,
    errors: List[str],
    warnings: List[str],
    valid_domains: List[str],
) -> None:
    """Validate enum fields: type, level, status, domain.

    Args:
        metadata: Parsed YAML frontmatter dictionary.
        errors: List to append critical errors to.
        warnings: List to append non-critical warnings to.
        valid_domains: List of valid domain strings from taxonomy.
    """
    if "type" in metadata and metadata["type"] not in VALID_TYPES:
        errors.append(
            f"Invalid type: '{metadata['type']}'. " f"Must be one of: {', '.join(VALID_TYPES)}"
        )

    if "level" in metadata and metadata["level"] not in VALID_LEVELS:
        errors.append(
            f"Invalid level: '{metadata['level']}'. " f"Must be one of: {', '.join(VALID_LEVELS)}"
        )

    if "status" in metadata and metadata["status"] not in VALID_STATUSES:
        errors.append(
            f"Invalid status: '{metadata['status']}'. "
            f"Must be one of: {', '.join(VALID_STATUSES)}"
        )

    if "domain" in metadata and metadata["domain"] not in valid_domains:
        # Domain is an error, not a warning — invalid domain breaks Dataview queries
        errors.append(
            f"Invalid domain: '{metadata['domain']}'. "
            f"Must be one of: {', '.join(valid_domains)}"
        )


def _validate_dates(metadata: dict, errors: List[str]) -> None:
    """Validate created and updated date fields.

    Args:
        metadata: Parsed YAML frontmatter dictionary.
        errors: List to append critical errors to.
    """
    if "created" in metadata and not validate_date_format(metadata["created"]):
        errors.append(f"Invalid created date format: '{metadata['created']}'. Use YYYY-MM-DD")

    if "updated" in metadata and not validate_date_format(metadata["updated"]):
        errors.append(f"Invalid updated date format: '{metadata['updated']}'. Use YYYY-MM-DD")


def _validate_arrays(metadata: dict, errors: List[str], warnings: List[str]) -> None:
    """Validate tags and related array fields.

    Args:
        metadata: Parsed YAML frontmatter dictionary.
        errors: List to append critical errors to.
        warnings: List to append non-critical warnings to.
    """
    if "tags" in metadata and not isinstance(metadata["tags"], list):
        errors.append("'tags' must be an array, e.g. tags: [api, rest, design]")

    if "related" in metadata and metadata["related"] is not None:
        if not isinstance(metadata["related"], list):
            errors.append("'related' must be an array or null")

    if "tags" in metadata and isinstance(metadata["tags"], list) and len(metadata["tags"]) < 3:
        warnings.append(f"Only {len(metadata['tags'])} tag(s) found (recommended: 3-10)")

    if not metadata.get("related"):
        warnings.append("No related links — recommended for knowledge graph connectivity")


def _parse_frontmatter(content: str) -> Tuple[dict, List[str]]:
    """Extract and parse YAML frontmatter from Markdown content.

    Args:
        content: Full text content of a Markdown file.

    Returns:
        Tuple of (metadata dict, list of parse errors).
    """
    if not content.startswith("---"):
        return {}, ["No YAML frontmatter found"]

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, ["Invalid YAML frontmatter structure (missing closing ---)"]

    metadata = yaml.safe_load(parts[1])
    if not metadata:
        return {}, ["Empty YAML frontmatter"]

    return metadata, []


def validate_file(
    filepath: str,
    valid_domains: Optional[List[str]] = None,
) -> Tuple[List[str], List[str]]:
    """Validate a single Markdown file's YAML frontmatter.

    Checks for:
        - Presence of YAML frontmatter
        - All required metadata fields
        - Valid enum values for type, level, status, domain
        - Correct date formats (ISO 8601)
        - Proper data types (arrays for tags/related)

    Args:
        filepath: Path to the Markdown file to validate.
        valid_domains: List of valid domain strings. If not provided,
            loads from Domain_Taxonomy.md automatically.

    Returns:
        A tuple containing two lists:
            - errors: Critical validation failures
            - warnings: Non-critical issues and best practice violations

    Example:
        >>> errors, warnings = validate_file("example.md")
        >>> if not errors:
        ...     print("File is valid!")
    """
    if valid_domains is None:
        valid_domains = load_domains_from_taxonomy()

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
                errors.append(f"Missing required field: '{field}'")

        _validate_enum_fields(metadata, errors, warnings, valid_domains)
        _validate_dates(metadata, errors)
        _validate_arrays(metadata, errors, warnings)

    except yaml.YAMLError as e:
        errors.append(f"YAML parsing error: {e}")
    except Exception as e:
        errors.append(f"Unexpected error: {e}")

    return errors, warnings


def main() -> None:
    """Execute validation on all Markdown files in the repository.

    Loads domain taxonomy from Domain_Taxonomy.md once, then validates
    all .md files recursively. Excludes system files (README, .github).
    Outputs color-coded results and a summary.

    Exit codes:
        0: All files valid (errors = 0)
        1: One or more files have validation errors

    Example:
        >>> main()
        📚 Loaded 27 domains from /path/to/Domain_Taxonomy.md
        🔍 AI Knowledge Filler - YAML Metadata Validator

        ✅ Core_System/example.md
        ❌ Core_System/invalid.md
           ERROR: Missing required field: 'title'

        📊 Validation Summary:
           Total files: 2
           ✅ Valid: 1
           ❌ Errors: 1
    """
    # Load domains once — single source of truth
    valid_domains = load_domains_from_taxonomy()

    print("🔍 AI Knowledge Filler - YAML Metadata Validator\n")

    all_files = glob.glob("**/*.md", recursive=True)
    md_files = [
        f for f in all_files if not any(x in f for x in [".github", "README.md", "CONTRIBUTING.md"])
    ]

    total_files = len(md_files)
    valid_files = 0
    files_with_errors = 0
    files_with_warnings = 0

    for filepath in sorted(md_files):
        errors, warnings = validate_file(filepath, valid_domains=valid_domains)

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
    print(f"\n📚 Domains loaded from: {TAXONOMY_FILENAME} ({len(valid_domains)} domains)")

    if files_with_errors > 0:
        print(f"\n❌ Validation failed: {files_with_errors} file(s) with errors")
        sys.exit(1)
    else:
        print("\n✅ All files valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
