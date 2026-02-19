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

from logger import get_logger

logger = get_logger(__name__)

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

    Args:
        taxonomy_path: Optional explicit path to Domain_Taxonomy.md.

    Returns:
        List of valid domain strings or fallback list.

    Example:
        >>> domains = load_domains_from_taxonomy()
        >>> "ai-system" in domains
        True
    """
    search_path = None

    if taxonomy_path:
        search_path = Path(taxonomy_path)
    else:
        for parent in [Path.cwd()] + list(Path.cwd().parents):
            candidate = parent / TAXONOMY_FILENAME
            if candidate.exists():
                search_path = candidate
                break
        if not search_path:
            matches = list(Path.cwd().rglob(TAXONOMY_FILENAME))
            if matches:
                search_path = matches[0]

    if not search_path or not search_path.exists():
        logger.warning("%s not found — using fallback domain list", TAXONOMY_FILENAME)
        return _FALLBACK_DOMAINS

    try:
        content = search_path.read_text(encoding="utf-8")
        domains = _parse_domains_from_taxonomy(content)
        if domains:
            logger.info("Loaded %d domains from %s", len(domains), search_path)
            return domains
        else:
            logger.warning("No domains parsed from %s — using fallback", search_path)
            return _FALLBACK_DOMAINS
    except (IOError, OSError) as e:
        logger.warning("Cannot read %s: %s — using fallback", TAXONOMY_FILENAME, e)
        return _FALLBACK_DOMAINS


def _parse_domains_from_taxonomy(content: str) -> List[str]:
    """Extract domain identifiers from Domain_Taxonomy.md content.

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
            f"Invalid type: '{metadata['type']}'. Must be one of: {', '.join(VALID_TYPES)}"
        )
    if "level" in metadata and metadata["level"] not in VALID_LEVELS:
        errors.append(
            f"Invalid level: '{metadata['level']}'. Must be one of: {', '.join(VALID_LEVELS)}"
        )
    if "status" in metadata and metadata["status"] not in VALID_STATUSES:
        errors.append(
            f"Invalid status: '{metadata['status']}'. Must be one of: {', '.join(VALID_STATUSES)}"
        )
    if "domain" in metadata and metadata["domain"] not in valid_domains:
        errors.append(
            f"Invalid domain: '{metadata['domain']}'. Must be one of: {', '.join(valid_domains)}"
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


_WIKILINK_RE = re.compile(r'^\[\[.+\]\]$')


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
        else:
            bad = [
                item for item in metadata["related"]
                if isinstance(item, str) and not _WIKILINK_RE.match(item)
            ]
            if bad:
                errors.append(
                    f"Related links must use [[WikiLink]] format. Invalid: {bad}"
                )
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
    strict: bool = False,
) -> Tuple[List[str], List[str]]:
    """Validate a single Markdown file's YAML frontmatter.

    Args:
        filepath: Path to the Markdown file to validate.
        valid_domains: List of valid domain strings. If not provided,
            loads from Domain_Taxonomy.md automatically.
        strict: If True, warnings are promoted to errors.

    Returns:
        A tuple of (errors, warnings) lists.

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

    if strict and warnings:
        errors.extend([f"[strict] {w}" for w in warnings])
        warnings = []

    return errors, warnings


def main() -> None:
    """Execute validation on all Markdown files in the repository.

    Exit codes:
        0: All files valid
        1: One or more files have errors
    """
    valid_domains = load_domains_from_taxonomy()
    logger.info("AI Knowledge Filler - YAML Metadata Validator")

    all_files = glob.glob("**/*.md", recursive=True)
    md_files = [
        f for f in all_files
        if not any(x in f for x in [".github", "README.md", "CONTRIBUTING.md"])
    ]

    total_files = len(md_files)
    valid_files = 0
    files_with_errors = 0
    files_with_warnings = 0

    for filepath in sorted(md_files):
        errors, warnings = validate_file(filepath, valid_domains=valid_domains)

        if errors:
            files_with_errors += 1
            logger.error("INVALID: %s", filepath)
            for error in errors:
                logger.error("  %s", error)
        elif warnings:
            files_with_warnings += 1
            logger.warning("WARNING: %s", filepath)
            for warning in warnings:
                logger.warning("  %s", warning)
        else:
            valid_files += 1
            logger.info("OK: %s", filepath)

    logger.info(
        "Summary — total: %d | valid: %d | warnings: %d | errors: %d | domains: %d",
        total_files, valid_files, files_with_warnings, files_with_errors, len(valid_domains),
    )

    if files_with_errors > 0:
        logger.error("Validation failed: %d file(s) with errors", files_with_errors)
        sys.exit(1)
    else:
        logger.info("All files valid")
        sys.exit(0)


if __name__ == "__main__":
    main()
