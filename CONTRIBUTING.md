# Contributing to AI Knowledge Filler

Thank you for your interest in contributing!

## Quick Start

```bash
# 1. Fork and clone
git clone https://github.com/yourusername/ai-knowledge-filler.git
cd ai-knowledge-filler

# 2. Create branch
git checkout -b feature/your-feature-name

# 3. Make changes (follow standards below)

# 4. Validate
python validate_yaml.py

# 5. Commit and push
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature-name

# 6. Create Pull Request on GitHub
```

---

## What to Contribute

### 1. New Domains

Add to `00-Core_System/Domain_Taxonomy.md`:
- Domain name (lowercase-hyphenated)
- Description and scope
- Example use cases
- Related domains

### 2. Example Files

Add to `02-Examples/` following:
- YAML frontmatter with all required fields
- Structured content with clear sections
- Cross-references to related files
- Real-world applicable examples

### 3. Documentation

Add to `01-Documentation/`:
- Use cases and scenarios
- Integration guides
- Best practices
- Troubleshooting guides

### 4. Tools and Scripts

Add to `03-Scripts/`:
- Validation utilities
- Automation scripts
- Integration helpers
- Testing tools

### 5. Bug Fixes

- Submit PR with description and test case
- Reference related issue if exists
- Include before/after examples

---

## Standards and Guidelines

### Metadata Standards

All `.md` files must have YAML frontmatter following `00-Core_System/Metadata_Template_Standard.md`:

```yaml
---
title: "Clear Descriptive Title"
type: concept|guide|reference|checklist|project|roadmap|template|audit
domain: from-domain-taxonomy
level: beginner|intermediate|advanced
status: draft|active|completed|archived
tags: [tag1, tag2, tag3]  # minimum 3 tags
related:
  - [[Related File 1]]
  - [[Related File 2]]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

### Content Guidelines

**Structure:**
- Clear heading hierarchy (##, ###, ####)
- Sections with focused content
- Code blocks with language tags
- Tables for comparisons
- Lists for steps or criteria

**Style:**
- Concise over verbose
- Actionable over theoretical
- Examples over abstractions
- Professional tone

**Links:**
- Use `[[WikiLinks]]` for internal references
- Use standard Markdown links for external URLs
- Validate all links work

### Validation

Before submitting:

```bash
# Validate YAML metadata
python validate_yaml.py

# Check for required fields
grep -r "^title:" 00-Core_System/*.md

# Validate no broken links (manual check in Obsidian)
```

---

## Commit Message Format

Follow conventional commits:

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` — New feature or content
- `fix:` — Bug fix or correction
- `docs:` — Documentation only
- `refactor:` — Code restructuring
- `test:` — Adding tests
- `chore:` — Maintenance tasks

**Examples:**
```bash
git commit -m "feat: add OAuth 2.0 implementation guide"
git commit -m "fix: correct YAML frontmatter in API design guide"
git commit -m "docs: expand troubleshooting section in deployment guide"
```

---

## Pull Request Process

### Before Submitting

- [ ] All changes follow metadata standards
- [ ] Validation passes: `python validate_yaml.py`
- [ ] New files include proper YAML frontmatter
- [ ] Internal links use `[[WikiLink]]` format
- [ ] No broken references
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main/master

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature (domain, example, guide)
- [ ] Bug fix (correction, typo, broken link)
- [ ] Documentation (clarification, expansion)
- [ ] Refactoring (restructuring, optimization)

## Testing
- [ ] Validated with `python validate_yaml.py`
- [ ] Tested in Obsidian (if applicable)
- [ ] Links verified

## Related Issues
Fixes #123 (if applicable)
```

### Review Process

1. Automated validation (GitHub Actions)
2. Maintainer review
3. Feedback and iteration
4. Approval and merge

---

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- Text editor (VS Code, Obsidian, or similar)
- (Optional) Obsidian for testing

### Local Setup

```bash
# Clone repository
git clone https://github.com/yourusername/ai-knowledge-filler.git
cd ai-knowledge-filler

# Install Python dependencies
pip install -r requirements.txt

# Validate existing files
python validate_yaml.py

# Open in Obsidian (optional)
# File → Open folder → Select ai-knowledge-filler directory
```

---

## Code of Conduct

### Guidelines

- Be respectful and constructive
- Provide helpful feedback
- Follow metadata standards
- Document your changes
- Test before submitting
- Respond to review feedback

### Expectations

- **Respectful:** Treat all contributors with respect
- **Collaborative:** Work together to improve quality
- **Standards-focused:** Maintain consistency and quality
- **Helpful:** Assist others when possible

---

## Artifact-First Contributions

When contributing code or configurations:

1. **Create artifact first** — No inline code in PR descriptions
2. **Provide checklist** — For multi-step changes
3. **Brief context only** — 2-3 sentences maximum
4. **Executable immediately** — No clarification needed

**Example PR:**

✅ **Good:**
```
Attached: update_workflow.yml, deployment_checklist.md

Updates CI/CD to use centralized Python validation. 
Follow checklist for deployment.
```

❌ **Bad:**
```
So I changed the workflow because the old one had issues with... 
[500 words of explanation with inline code snippets]
```

---

## Questions?

- **Issues:** [GitHub Issues](https://github.com/yourusername/ai-knowledge-filler/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/ai-knowledge-filler/discussions)
- **Documentation:** See `01-Documentation/` folder

---

## Recognition

Contributors will be:
- Listed in project acknowledgments
- Credited in release notes
- Mentioned in relevant documentation

Thank you for contributing to AI Knowledge Filler! 🚀
