---
title: "CI/CD Workflow Configuration — AI Knowledge Filler"
type: reference
domain: devops
level: intermediate
status: active
version: v1.0
tags: [cicd, github-actions, automation, validation, workflow]
related:
  - "[[Deployment_Guide]]"
  - "[[validate_yaml.py]]"
  - "[[Metadata_Template_Standard]]"
created: 2026-02-10
updated: 2026-02-10
---
## Purpose

GitHub Actions workflow for automated validation of YAML metadata in Markdown files on every push and pull request.

---

## Workflow Configuration

**File Location:** `.github/workflows/validate-metadata.yml`

```yaml
name: Validate Metadata

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run YAML validator
      run: python validate_yaml.py
      
    - name: Check for missing frontmatter
      run: |
        files_without_yaml=$(find . -name "*.md" \
          ! -path "./.github/*" \
          ! -name "README.md" \
          ! -name "CONTRIBUTING.md" \
          ! -name "DEPLOYMENT_READY.md" \
          -exec grep -L "^---$" {} \;)
        
        if [ -n "$files_without_yaml" ]; then
          echo "Files missing YAML frontmatter:"
          echo "$files_without_yaml"
          exit 1
        fi
        
    - name: Validate required fields
      run: |
        missing_fields=$(grep -r "^title:\|^type:\|^domain:\|^level:\|^status:\|^created:\|^updated:" \
          --include="*.md" \
          --exclude-dir=.github \
          --exclude=README.md \
          --exclude=CONTRIBUTING.md \
          --exclude=DEPLOYMENT_READY.md \
          . | wc -l)
        
        total_md=$(find . -name "*.md" \
          ! -path "./.github/*" \
          ! -name "README.md" \
          ! -name "CONTRIBUTING.md" \
          ! -name "DEPLOYMENT_READY.md" | wc -l)
        
        expected_fields=$((total_md * 7))
        
        if [ "$missing_fields" -lt "$expected_fields" ]; then
          echo "Some files missing required metadata fields"
          exit 1
        fi
```

---

## Workflow Triggers

### Push Events
- Activates on pushes to `main` and `develop` branches
- Validates all Markdown files in repository
- Blocks merge if validation fails

### Pull Request Events
- Runs on PRs targeting `main` and `develop`
- Provides validation feedback before merge
- Prevents invalid files from entering main branch

---

## Validation Steps

### 1. Repository Checkout
Clones repository with full history for comprehensive validation

### 2. Python Environment
- Uses Python 3.11 (latest stable)
- Installs dependencies from `requirements.txt`
- Caches pip packages for faster builds

### 3. YAML Validator Execution
- Runs `validate_yaml.py` script
- Checks all YAML frontmatter fields
- Validates enum values (type, level, status, domain)
- Verifies date formats (ISO 8601)
- Ensures tags are arrays with 3+ items

### 4. Frontmatter Presence Check
- Scans all `.md` files
- Excludes GitHub documentation and READMEs
- Fails if any file lacks YAML frontmatter

### 5. Required Fields Validation
- Verifies presence of mandatory fields:
  - `title`
  - `type`
  - `domain`
  - `level`
  - `status`
  - `created`
  - `updated`

---

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | All validations passed | Merge allowed |
| 1 | Validation errors found | Merge blocked |

---

## Local Testing

Run validation locally before pushing:

```bash
# Install dependencies
pip install -r requirements.txt

# Run validator
python validate_yaml.py

# Check exit code
echo $?
```

---

## Excluded Files

Workflow excludes:
- `.github/` directory
- `README.md`
- `CONTRIBUTING.md`
- `DEPLOYMENT_READY.md`
- Any non-Markdown files

---

## Error Handling

### Missing Frontmatter
```
Files missing YAML frontmatter:
  ./Documentation/invalid_file.md
```

**Fix:** Add YAML frontmatter to listed files

### Invalid Metadata
```
❌ Documentation/invalid_file.md
   ERROR: Invalid type: document. Must be one of: concept, guide, reference, checklist, project, roadmap, template, audit
```

**Fix:** Correct invalid field values per [[Metadata_Template_Standard]]

### Missing Required Fields
```
Some files missing required metadata fields
```

**Fix:** Add all required fields to affected files

---

## Performance Optimization

### Caching Strategy
```yaml
- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

### Parallel Execution
```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11']
```

---

## Status Badge

Add to `README.md`:

```markdown
[![Validate Metadata](https://github.com/USERNAME/ai-knowledge-filler/workflows/Validate%20Metadata/badge.svg)](https://github.com/USERNAME/ai-knowledge-filler/actions)
```

---

## Extending Workflow

### Add Code Linting
```yaml
- name: Lint Python code
  run: |
    pip install flake8
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

### Add Security Scanning
```yaml
- name: Security scan
  run: |
    pip install bandit
    bandit -r . -f json -o bandit-report.json
```

### Add Dependency Scanning
```yaml
- name: Check dependencies
  run: |
    pip install safety
    safety check --json
```

---

## Troubleshooting

### Workflow Fails on Valid Files
- Check `requirements.txt` has correct versions
- Verify `validate_yaml.py` is in repository root
- Confirm Python version compatibility

### False Positives on Excluded Files
- Update exclusion patterns in workflow
- Add files to `.gitignore` if needed

### Slow Validation
- Enable pip caching
- Use matrix strategy for parallel execution
- Consider incremental validation (changed files only)

---

## Integration

### Required Files
- `.github/workflows/validate-metadata.yml` — This workflow
- `validate_yaml.py` — Validation script
- `requirements.txt` — Python dependencies
- `Metadata_Template_Standard.md` — Validation rules

### Branch Protection Rules

Configure on GitHub:
```
Settings → Branches → Branch protection rules
- Require status checks to pass: ✅
- Require branches to be up to date: ✅
- Status checks: validate / ubuntu-latest
```

---

## Maintenance

### Update Python Version
```yaml
python-version: '3.12'  # Update when new version stable
```

### Update Actions Versions
```yaml
actions/checkout@v5  # Check quarterly for updates
actions/setup-python@v6
```

### Expand Validation
Add custom validators in `validate_yaml.py` for:
- Link validation (WikiLinks exist)
- Domain taxonomy compliance
- Version format validation
- Custom field validation

---

## Conclusion

Automated validation ensures metadata consistency across all knowledge files, preventing invalid files from entering the repository and maintaining system integrity.
