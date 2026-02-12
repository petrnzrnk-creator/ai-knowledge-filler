"""Unit tests for validate_yaml.py"""
import pytest
from pathlib import Path
import sys

# Add Scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Scripts'))

from validate_yaml import validate_date_format, validate_file


class TestDateValidation:
    """Test date format validation."""
    
    def test_valid_date_format(self):
        """Test valid ISO 8601 date."""
        assert validate_date_format('2026-02-12') is True
    
    def test_invalid_date_format_dd_mm_yyyy(self):
        """Test invalid DD-MM-YYYY format."""
        assert validate_date_format('12-02-2026') is False
    
    def test_invalid_date_format_slashes(self):
        """Test invalid MM/DD/YYYY format."""
        assert validate_date_format('02/12/2026') is False
    
    def test_invalid_date_value(self):
        """Test invalid date value (month 13)."""
        assert validate_date_format('2026-13-01') is False
    
    def test_invalid_date_feb_30(self):
        """Test invalid February 30."""
        assert validate_date_format('2026-02-30') is False


class TestFileValidation:
    """Test file validation logic."""
    
    def test_valid_file(self, tmp_path):
        """Test validation of valid file."""
        # Create valid test file
        test_file = tmp_path / "test.md"
        test_file.write_text("""---
title: "Test File"
type: concept
domain: ai-system
level: intermediate
status: active
tags: [test, example, valid]
created: 2026-02-12
updated: 2026-02-12
---

# Test Content
""")
        
        errors, warnings = validate_file(str(test_file))
        assert len(errors) == 0
    
    def test_missing_frontmatter(self, tmp_path):
        """Test file without YAML frontmatter."""
        test_file = tmp_path / "no_yaml.md"
        test_file.write_text("# Just a heading\n\nNo YAML here.")
        
        errors, warnings = validate_file(str(test_file))
        assert len(errors) > 0
        assert any('frontmatter' in e.lower() for e in errors)
    
    def test_missing_title_field(self, tmp_path):
        """Test file missing required 'title' field."""
        test_file = tmp_path / "missing_title.md"
        test_file.write_text("""---
type: concept
domain: ai-system
level: intermediate
status: active
tags: [test]
created: 2026-02-12
updated: 2026-02-12
---

# Content
""")
        
        errors, warnings = validate_file(str(test_file))
        assert len(errors) > 0
        assert any('title' in e.lower() for e in errors)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
