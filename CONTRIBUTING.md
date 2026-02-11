# Contributing to AI Knowledge Filler

Thank you for your interest in contributing!

## How to Contribute

### 1. Fork the Repository
```bash
git clone https://github.com/yourusername/ai-knowledge-filler.git
cd ai-knowledge-filler
```

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes

Follow the metadata standards in `Core_System/Metadata_Template_Standard.md`:
- All .md files must have YAML frontmatter
- Use ISO 8601 dates (YYYY-MM-DD)
- Follow domain taxonomy in `Core_System/Domain_Taxonomy.md`

### 4. Test Your Changes

```bash
# Validate YAML
grep -r "^---$" *.md

# Check required fields
grep -r "^title:" *.md
```

### 5. Submit Pull Request

- Describe changes clearly
- Reference related issues
- Ensure CI checks pass

## What to Contribute

### New Domains
Add to `Core_System/Domain_Taxonomy.md` with:
- Domain name (lowercase-hyphenated)
- Description
- Example use cases

### Example Files
Add to `Examples/` following metadata standards

### Use Cases
Add to `Documentation/Use_Cases_Documentation.md`

### Bug Fixes
Submit PR with description and test case

## Code of Conduct

- Be respectful
- Provide constructive feedback
- Follow metadata standards
- Document changes

## Questions?

Open an issue or discussion on GitHub.
