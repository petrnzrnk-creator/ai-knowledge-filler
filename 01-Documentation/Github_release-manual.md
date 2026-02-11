---
title: "GitHub Release Manual — AI Knowledge Filler"
type: guide
domain: devops
level: intermediate
status: active
version: v1.0
tags: [github, release, deployment, version-control, ci-cd]
related:
  - "[[Deployment_Guide]]"
  - "[[DEPLOYMENT_READY]]"
  - "[[System_Prompt_AI_Knowledge_Filler]]"
created: 2026-02-10
updated: 2026-02-10
---

## PURPOSE

Complete manual for creating, managing, and automating GitHub releases for AI Knowledge Filler.

---

## PREREQUISITES

### Repository Setup
```bash
# Verify repository state
git status                    # Clean working directory
git log --oneline -5          # Recent commits visible
git remote -v                 # Origin configured

# Verify branch
git branch                    # On main/master
```

### Required Files
- [ ] README.md with version number
- [ ] CHANGELOG.md (recommended)
- [ ] LICENSE file
- [ ] All documentation updated
- [ ] Validation tests passing

### Permissions
- Repository admin or release permissions
- Git configured with credentials

---

## RELEASE WORKFLOW

### 1. Pre-Release Validation

```bash
# Run validation
python validate_yaml.py

# Expected output: ✅ All files valid!
```

```bash
# Check for uncommitted changes
git status

# If changes exist:
git add .
git commit -m "Pre-release: Final updates for v1.0.0"
git push origin main
```

### 2. Version Bump Strategy

**Semantic Versioning: vMAJOR.MINOR.PATCH**

| Change Type | Increment | Example |
|------------|-----------|---------|
| Breaking changes | MAJOR | v1.0.0 → v2.0.0 |
| New features | MINOR | v1.0.0 → v1.1.0 |
| Bug fixes | PATCH | v1.0.0 → v1.0.1 |

**Update Version References:**
```bash
# Files to update
- README.md (version badge, footer)
- Core_System/System_Prompt_AI_Knowledge_Filler.md (metadata)
- DEPLOYMENT_READY.md (if applicable)
```

### 3. Create Git Tag

```bash
# Create annotated tag
git tag -a v1.0.0 -m "AI Knowledge Filler v1.0.0 - Production Release"

# Verify tag
git tag -l
git show v1.0.0

# Push tag to remote
git push origin v1.0.0
```

**Tag Naming Convention:**
- `v1.0.0` — Production release
- `v1.0.0-beta` — Beta release
- `v1.0.0-rc.1` — Release candidate

### 4. Create GitHub Release (Web UI)

**Navigate to Repository:**
```
https://github.com/YOUR_USERNAME/ai-knowledge-filler
→ Code tab
→ Releases (right sidebar)
→ Draft a new release
```

**Release Configuration:**

| Field | Value |
|-------|-------|
| **Tag** | v1.0.0 (select existing or create new) |
| **Target** | main (default branch) |
| **Title** | AI Knowledge Filler v1.0.0 |
| **Description** | See template below |

**Release Description Template:**
```markdown
## AI Knowledge Filler v1.0.0

Transform any LLM into a deterministic knowledge base generator.

### 🎯 What's Included

**Core System (10 files)**
- System Prompt — LLM behavior transformation
- Metadata Standard — YAML specification
- Domain Taxonomy — 30+ classifications
- File Update Protocol — Merge & conflict resolution
- Prompt Engineering Workflow — 8-stage methodology
- Custom Instructions — AI working profile
- Deployment Guide — Multi-platform installation
- Use Cases — 20+ real-world scenarios
- Control Dashboard — Dataview monitoring
- Audit Report — System alignment validation

**Infrastructure**
- Automated YAML validation
- Python validation script
- GitHub Actions CI/CD
- Example files (concept, guide, checklist)
- MIT License

### ✨ Key Features

- ✅ Universal LLM compatibility (Claude, GPT-4, Gemini, local models)
- ✅ Zero manual formatting required
- ✅ Production-ready Markdown with YAML metadata
- ✅ Obsidian native compatibility
- ✅ 70-90% time savings on documentation

### 📦 Installation

**Quick Start (60 seconds):**
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/ai-knowledge-filler.git
cd ai-knowledge-filler

# Copy system prompt to Claude.ai Project Knowledge
# See Deployment_Guide.md for details
```

**For detailed installation:** See [Deployment_Guide.md](Documentation/Deployment_Guide.md)

### 📊 What's New in v1.0.0

- Initial production release
- Complete core system (10 files)
- Comprehensive documentation
- Validation infrastructure
- Example files and templates
- GitHub Actions workflow

### 🐛 Known Issues

None at this time.

### 📞 Support

- Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/ai-knowledge-filler/issues)
- Discussions: [GitHub Discussions](https://github.com/YOUR_USERNAME/ai-knowledge-filler/discussions)

### 📜 License

MIT License — Free for commercial and personal use.

---

**Full Changelog:** https://github.com/YOUR_USERNAME/ai-knowledge-filler/commits/v1.0.0
```

**Attachments:**
- None required (all files in repository)
- Optional: Binary artifacts (if any)

**Release Type:**
- ✅ Set as latest release
- ⬜ Pre-release (for beta/RC)

**Click: Publish release**

---

## 5. Post-Release Tasks

### Verify Release

```bash
# Check release is live
curl -s https://api.github.com/repos/YOUR_USERNAME/ai-knowledge-filler/releases/latest | jq '.tag_name'

# Expected: "v1.0.0"
```

### Update Repository Topics

**Go to:** Repository → About (gear icon)

**Add topics:**
```
llm, knowledge-management, obsidian, claude, 
documentation, markdown, yaml, prompt-engineering, 
ai-tools, productivity
```

### Social Sharing

**LinkedIn Post:**
```markdown
🚀 Just released AI Knowledge Filler v1.0.0

Transform any LLM into a deterministic knowledge base generator.

✅ Universal LLM support (Claude, GPT-4, Gemini, local)
✅ Zero manual formatting
✅ 70-90% faster documentation
✅ Production-ready Markdown with YAML metadata

Open source. MIT licensed. Production ready.

GitHub: [link]

#AI #KnowledgeManagement #OpenSource #Productivity
```

**Twitter/X Post:**
```markdown
Built a knowledge engineering system that transforms LLMs 
into deterministic file generators.

→ Any LLM (Claude, GPT-4, local)
→ Structured Markdown + YAML
→ 70-90% faster docs
→ Zero formatting

Open source, production ready.
[link]
```

### Documentation Updates

- [ ] Update README.md badges if needed
- [ ] Create CHANGELOG.md entry
- [ ] Update any version-dependent documentation

---

## CHANGELOG MANAGEMENT

### CHANGELOG.md Structure

```markdown
# Changelog

All notable changes to AI Knowledge Filler will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Feature X in development

## [1.0.0] - 2026-02-10

### Added
- Initial production release
- Core system (10 files)
- Validation infrastructure
- Example files
- Comprehensive documentation

### Changed
- N/A (initial release)

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

[Unreleased]: https://github.com/YOUR_USERNAME/ai-knowledge-filler/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/YOUR_USERNAME/ai-knowledge-filler/releases/tag/v1.0.0
```

---

## RELEASE TYPES

### 1. Production Release (Stable)

```bash
# Tag format
git tag -a v1.0.0 -m "Production release v1.0.0"

# GitHub release settings
□ Pre-release
✅ Set as latest release
```

**When to use:**
- Stable, tested version
- Ready for production use
- No known critical bugs

---

### 2. Beta Release

```bash
# Tag format
git tag -a v1.1.0-beta -m "Beta release v1.1.0"

# GitHub release settings
✅ Pre-release
□ Set as latest release
```

**When to use:**
- Testing new features
- Gathering feedback
- Not production-ready

**Release notes should include:**
```markdown
⚠️ **BETA RELEASE** — Not recommended for production use

Known limitations:
- Feature X is experimental
- May have breaking changes
- Feedback welcome via Issues
```

---

### 3. Release Candidate

```bash
# Tag format
git tag -a v2.0.0-rc.1 -m "Release candidate 2.0.0 RC1"

# GitHub release settings
✅ Pre-release
□ Set as latest release
```

**When to use:**
- Feature complete
- Final testing phase
- Preparing for production

---

### 4. Hotfix Release

```bash
# Tag format
git tag -a v1.0.1 -m "Hotfix: Critical bug fix"

# GitHub release settings
□ Pre-release
✅ Set as latest release
```

**When to use:**
- Critical bug fixes
- Security patches
- Emergency updates

**Workflow:**
```bash
# Create hotfix branch
git checkout -b hotfix/v1.0.1 v1.0.0

# Apply fixes
git commit -m "Fix: Critical validation bug"

# Merge to main
git checkout main
git merge hotfix/v1.0.1

# Tag and release
git tag -a v1.0.1 -m "Hotfix v1.0.1"
git push origin main --tags
```

---

## GITHUB CLI ALTERNATIVE

### Install GitHub CLI

```bash
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Windows
winget install --id GitHub.cli
```

### Authenticate

```bash
gh auth login
```

### Create Release via CLI

```bash
# Create tag
git tag -a v1.0.0 -m "AI Knowledge Filler v1.0.0"
git push origin v1.0.0

# Create release
gh release create v1.0.0 \
  --title "AI Knowledge Filler v1.0.0" \
  --notes-file release-notes.md \
  --latest

# Alternative: Generate notes automatically
gh release create v1.0.0 \
  --title "AI Knowledge Filler v1.0.0" \
  --generate-notes
```

### List Releases

```bash
gh release list
```

### View Release

```bash
gh release view v1.0.0
```

---

## AUTOMATION WITH GITHUB ACTIONS

### Automated Release on Tag Push

**File:** `.github/workflows/release.yml`

```yaml
name: Create Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    name: Create Release
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Get version from tag
        id: tag_name
        run: echo "VERSION=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT
      
      - name: Validate YAML metadata
        run: |
          pip install pyyaml
          python validate_yaml.py
      
      - name: Generate changelog
        id: changelog
        uses: metcalfc/changelog-generator@v4.0.1
        with:
          myToken: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ steps.tag_name.outputs.VERSION }}
          release_name: AI Knowledge Filler ${{ steps.tag_name.outputs.VERSION }}
          body: |
            ## What's Changed
            ${{ steps.changelog.outputs.changelog }}
            
            ## Installation
            See [Deployment Guide](https://github.com/${{ github.repository }}/blob/main/Documentation/Deployment_Guide.md)
          draft: false
          prerelease: false
```

**Usage:**
```bash
# Just push tag — release created automatically
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# GitHub Actions creates release
```

---

## RELEASE CHECKLIST

### Pre-Release
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Version numbers bumped
- [ ] CHANGELOG.md updated
- [ ] Clean git status
- [ ] Feature branches merged
- [ ] Code review completed

### Release Creation
- [ ] Git tag created locally
- [ ] Tag pushed to remote
- [ ] GitHub release drafted
- [ ] Release notes complete
- [ ] Release type set correctly
- [ ] Release published

### Post-Release
- [ ] Release verified live
- [ ] Repository topics updated
- [ ] Social media posted
- [ ] Team notified
- [ ] Documentation links updated
- [ ] Next version planning started

---

## COMMON ISSUES & SOLUTIONS

### Issue: Tag Already Exists

```bash
# Error: tag 'v1.0.0' already exists

# Solution 1: Delete local and remote tag
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0

# Solution 2: Use new version
git tag -a v1.0.1 -m "Corrected release"
```

### Issue: Wrong Tag Target

```bash
# Tag points to wrong commit

# Delete tag
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0

# Create tag on correct commit
git checkout <correct-commit-hash>
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### Issue: Need to Update Release

```bash
# Use GitHub CLI
gh release edit v1.0.0 --notes-file new-notes.md

# Or edit via web UI
# Releases → Select release → Edit release
```

### Issue: Forgot to Push Tag

```bash
# Tag exists locally but not on GitHub

git push origin v1.0.0
```

---

## BEST PRACTICES

### 1. Consistent Versioning
- Always use semantic versioning
- Document breaking changes clearly
- Increment appropriately

### 2. Meaningful Release Notes
- Highlight user-facing changes
- Include installation instructions
- Link to documentation
- Credit contributors

### 3. Testing Before Release
- Run full test suite
- Validate all documentation
- Check example files work

### 4. Communication
- Announce via appropriate channels
- Update documentation sites
- Notify users of breaking changes

### 5. Security
- Review code for vulnerabilities
- Update dependencies
- Document security fixes clearly

---

## RELEASE METRICS

### Track Via GitHub API

```bash
# Get release download count
curl -s https://api.github.com/repos/YOUR_USERNAME/ai-knowledge-filler/releases | \
  jq '.[] | {name: .name, downloads: .assets[].download_count}'

# Get star count
curl -s https://api.github.com/repos/YOUR_USERNAME/ai-knowledge-filler | \
  jq '.stargazers_count'

# Get fork count
curl -s https://api.github.com/repos/YOUR_USERNAME/ai-knowledge-filler | \
  jq '.forks_count'
```

### Monitor
- GitHub Insights → Traffic
- Release download counts
- Issue/PR activity
- Star/fork growth

---

## ROLLBACK PROCEDURE

### If Release Has Issues

**Option 1: Delete Release**
```bash
# Delete via CLI
gh release delete v1.0.0

# Delete via web UI
Releases → Select → Delete release

# Delete tag
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
```

**Option 2: Mark as Pre-release**
```bash
# Edit release via CLI
gh release edit v1.0.0 --prerelease

# Add warning to release notes
```

**Option 3: Create Hotfix**
```bash
# Better approach for critical issues
git tag -a v1.0.1 -m "Hotfix: Fix critical bug"
git push origin v1.0.1

# Create new release
gh release create v1.0.1 --title "Hotfix v1.0.1" --notes "Fixes critical bug in v1.0.0"
```

---

## MULTI-PLATFORM RELEASE

### If Building Binary Artifacts

```bash
# Build for multiple platforms
make build-linux
make build-windows
make build-mac

# Attach to release
gh release upload v1.0.0 \
  dist/akf-linux-amd64 \
  dist/akf-windows-amd64.exe \
  dist/akf-darwin-amd64
```

### Docker Image Release

```bash
# Tag and push Docker image
docker build -t YOUR_USERNAME/ai-knowledge-filler:v1.0.0 .
docker push YOUR_USERNAME/ai-knowledge-filler:v1.0.0

# Also tag as latest
docker tag YOUR_USERNAME/ai-knowledge-filler:v1.0.0 YOUR_USERNAME/ai-knowledge-filler:latest
docker push YOUR_USERNAME/ai-knowledge-filler:latest
```

---

## CONCLUSION

This manual provides complete coverage of GitHub release management for AI Knowledge Filler.

**Quick Reference:**
1. Validate → Tag → Push → Release → Promote
2. Use semantic versioning
3. Write clear release notes
4. Automate where possible
5. Communicate widely

**Next Steps:**
- Create first release using this guide
- Setup automated release workflow
- Monitor release metrics
- Plan next version