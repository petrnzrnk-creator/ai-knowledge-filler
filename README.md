# AI Knowledge Filler

**Deterministic knowledge compiler for LLM output**

[![Tests](https://github.com/petrnzrnk-creator/ai-knowledge-filler/workflows/Tests/badge.svg)](https://github.com/petrnzrnk-creator/ai-knowledge-filler/actions/workflows/tests.yml)
[![Lint](https://github.com/petrnzrnk-creator/ai-knowledge-filler/workflows/Lint/badge.svg)](https://github.com/petrnzrnk-creator/ai-knowledge-filler/actions/workflows/lint.yml)
[![Validate](https://github.com/petrnzrnk-creator/ai-knowledge-filler/workflows/Validate%20Metadata/badge.svg)](https://github.com/petrnzrnk-creator/ai-knowledge-filler/actions/workflows/validate.yml)
[![PyPI](https://img.shields.io/pypi/v/ai-knowledge-filler.svg)](https://pypi.org/project/ai-knowledge-filler/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen.svg)](https://github.com/petrnzrnk-creator/ai-knowledge-filler/actions/workflows/tests.yml)
[![Pylint](https://img.shields.io/badge/pylint-9.55%2F10-brightgreen)](https://github.com/petrnzrnk-creator/ai-knowledge-filler)

---

## What is AKF

**AKF (AI Knowledge Filler)** is an AI-Native Cognitive Operating System —
a deterministic validation pipeline that turns LLM output into schema-compliant, ontology-governed knowledge files.

> LLMs generate text. Text is not knowledge.

**What it is not:** a note-taking app, a chat assistant, a markdown generator, an Obsidian plugin.
**What it is:** the operating contract for a knowledge base that scales.

### The Problem

Without a validation layer, AI-generated content produces:

| Error | Example |
|-------|---------|
| Domain violation | `domain: Technology` → valid: `domain: system-design` |
| Enum violation | `level: expert` → valid: `beginner \| intermediate \| advanced` |
| Type mismatch | `tags: security` → valid: `tags: [security, api, auth]` |
| Date format | `created: 12-02-2026` → valid: `created: 2026-02-12` |

Each error is trivial. Across hundreds of files, they make a vault unsearchable,
Dataview queries return nothing, and the knowledge graph becomes noise.

AKF solves this at the **generation layer**, not the review layer.

### What Every Committed File Guarantees

- Required fields: `title`, `type`, `domain`, `level`, `status`, `tags`, `created`, `updated`
- Valid enums: `type`, `level`, `status` from controlled sets
- Domain from configured taxonomy (`akf.yaml`) — not hardcoded
- ISO 8601 dates with `created ≤ updated`
- `tags` as array (≥3), `title` as string — no type mismatches

Violations produce error codes E001–E007. Retry instructions are derived from those codes, not from free-form prompts.

### Retry = Ontology Signal

Retry pressure is not a failure metric.
When a domain triggers elevated retries, the taxonomy has a boundary problem — not the model.
Telemetry captures this signal. Ontology improves from data, not intuition.
---

## ⚡ Quick Start (60 seconds)

### Option 1: pip install (Recommended)

```bash
pip install ai-knowledge-filler

# Set at least one API key — Groq is free and fastest to start
export GROQ_API_KEY="gsk_..."          # free at console.groq.com (recommended)
# export ANTHROPIC_API_KEY="sk-ant-..." # or any other provider

# Generate
akf generate "Create Docker security checklist"
```

**Output:** `outputs/Docker_Security_Checklist.md` — production-ready, validated.

### Option 2: Claude Projects (No CLI)

```
1. Open Claude.ai → Create new Project
2. Project Knowledge → Upload akf/system_prompt.md
3. Custom Instructions → Paste akf/system_prompt.md
4. Prompt: "Create guide on API authentication"
5. Done. Claude generates structured files.
```

---

## What You Get

### Core System
- **System Prompt** — Transforms LLM from chat to file generator
- **Metadata Standard** — YAML structure specification
- **Domain Taxonomy** — 30+ classification domains
- **Update Protocol** — File merge rules
- **Validation Script** — Automated quality gates
- **CLI** — Multi-LLM interface (Claude, Gemini, GPT-4, Ollama)

### Quality Assurance
- ✅ 97% test coverage (165 tests)
- ✅ Automated YAML validation
- ✅ CI/CD pipelines (GitHub Actions)
- ✅ Type hints (100% coverage)
- ✅ Linting (Pylint 9.55/10)

---

## CLI Commands

### Generate Files

```bash
# Auto-select first available LLM
akf generate "Create Kubernetes deployment guide"

# Specific model
akf generate "Create API checklist" --model claude
akf generate "Create Docker guide" --model gemini
akf generate "Create REST concept" --model gpt4
akf generate "Create microservices reference" --model ollama
```

### Validate Files

```bash
# Single file
akf validate --file outputs/Guide.md

# All files in outputs/
akf validate
```

### List Available Models

```bash
akf models

# Output:
# ✅ groq      Groq — llama-3.3-70b-versatile
# ❌ grok      Grok (xAI) — Set XAI_API_KEY
# ✅ claude    Claude (Anthropic) — claude-sonnet-4-20250514
# ✅ gemini    Gemini (Google) — gemini-3-flash-preview
# ❌ gpt4      GPT-3.5 (OpenAI) — Set OPENAI_API_KEY
# ✅ ollama    Ollama — llama3.2:3b
```

---

## Example Output

**Input:**
```
Create guide on API rate limiting
```

**Output:**
```yaml
---
title: "API Rate Limiting Strategy"
type: guide
domain: api-design
level: intermediate
status: active
version: v1.0
tags: [api, rate-limiting, performance]
related:
  - "[[API Design Principles]]"
  - "[[System Scalability]]"
created: 2026-02-12
updated: 2026-02-12
---

## Purpose
Comprehensive strategy for implementing API rate limits...

## Core Principles
[Structured content with sections, code examples]

## Implementation
[Step-by-step technical guidance]

## Conclusion
[Summary and next steps]
```

**Every file. Same structure. Validated automatically.**

---

## Architecture

```
User Prompt
    ↓
System Prompt (behavior definition)
    ↓
LLM Provider (Claude/Gemini/GPT-4/Ollama)
    ↓
Structured Markdown + YAML
    ↓
Automated Validation
    ↓
Production-Ready File
```

**Key Insight:** System prompt is the source of truth. Same prompt works across all LLMs.

### Validation Pipeline (Phase 2.1)

```
LLM Output
    ↓
Validation Engine  ← deterministic
    ↓
Error Normalizer   ← deterministic
    ↓
Retry Controller   ← non-deterministic (LLM, max 3 attempts)
    ↓
Commit Gate        ← deterministic (schema_version + atomic write)
    ↓
Vault File
```

**Determinism boundary:** LLM is the only non-deterministic component.

---

## Model Selection

| Model | Key | Speed | Cost | Best For |
|-------|-----|-------|------|----------|
| **Groq** | `GROQ_API_KEY` | ⚡ Fastest | Free tier | First installs, CI, high volume |
| **Grok** | `XAI_API_KEY` | Fast | $$ | General purpose |
| **Claude** | `ANTHROPIC_API_KEY` | Medium | $$$ | Technical docs, architecture |
| **Gemini** | `GOOGLE_API_KEY` | Fast | $ | Quick drafts, summaries |
| **GPT-3.5** | `OPENAI_API_KEY` | Medium | $$ | Versatile content |
| **Ollama** | — | Very Fast | Free | Privacy, offline, local |

**Auto-selection:** CLI tries providers in order: Groq → Grok → Claude → Gemini → GPT-4 → Ollama (first available).

---

## Installation

### Via pip (Recommended)

```bash
pip install ai-knowledge-filler
```

### From Source

```bash
git clone https://github.com/petrnzrnk-creator/ai-knowledge-filler.git
cd ai-knowledge-filler
pip install -r requirements.txt
```

### API Keys

```bash
# Set at least one (Groq recommended — free tier available)
export GROQ_API_KEY="gsk_..."          # console.groq.com
export XAI_API_KEY="xai-..."           # console.x.ai
export ANTHROPIC_API_KEY="sk-ant-..."  # console.anthropic.com
export GOOGLE_API_KEY="AIza..."        # aistudio.google.com
export OPENAI_API_KEY="sk-..."         # platform.openai.com

# Or add to ~/.bashrc / ~/.zshrc to persist across sessions:
# export GROQ_API_KEY="gsk_..."
```

---

## Testing

```bash
# Run all tests
pytest --cov=. --cov-report=term-missing -v

# Run validation
akf validate

# Run linting
pylint *.py tests/
```

**Coverage:** 97% (165 tests)
**Linting:** Pylint 9.55/10
**CI/CD:** All checks passing

---

## Use Cases

**1. Technical Documentation**
Generate API docs, architecture decisions, deployment guides.

**2. Knowledge Management**
Structure meeting notes, research findings, learning content.

**3. Consulting Deliverables**
Create frameworks, methodologies, client reports.

**4. Batch Processing**
Generate multiple files programmatically via CLI or API.

---

## File Types

```yaml
type: concept      # Theoretical entity, definition
type: guide        # Step-by-step process
type: reference    # Specification, standard
type: checklist    # Validation criteria
type: project      # Project description
type: template     # Reusable template
```

**30+ domains:** `api-design`, `system-design`, `devops`, `security`, `data-engineering`, etc.

---

## Documentation

- [System Prompt](akf/system_prompt.md) — LLM behavior definition
- [User Guide](docs/user-guide.md) — Installation, quick start, troubleshooting
- [CLI Reference](docs/cli-reference.md) — All commands, flags, env vars, exit codes
- [Architecture](ARCHITECTURE.md) — Module map, data flow, extension points
- [Contributing](CONTRIBUTING.md) — Dev setup, quality gates, adding providers

---

## Advanced Usage

### Programmatic Generation

```python
from llm_providers import get_provider

# Auto-select provider
provider = get_provider("auto")

# Load system prompt
with open('akf/system_prompt.md') as f:
    system_prompt = f.read()

# Generate
content = provider.generate(
    prompt="Create API security checklist",
    system_prompt=system_prompt
)

# Save
with open('outputs/Security_Checklist.md', 'w') as f:
    f.write(content)
```

### Batch Processing

```bash
cat > topics.txt << 'EOF'
Docker deployment best practices
Kubernetes security hardening
API authentication strategies
EOF

while read topic; do
    akf generate "Create guide on $topic" --model gemini
done < topics.txt
```

---

## Validation

**Automated checks:**
- ✅ YAML frontmatter present
- ✅ Required fields (title, type, domain, level, status, created, updated)
- ✅ Valid enum values (type, level, status)
- ✅ Domain in taxonomy
- ✅ ISO 8601 dates (YYYY-MM-DD)
- ✅ Tags array (3+ items)

**Output:**
```
✅ outputs/Guide.md
❌ drafts/incomplete.md
   ERROR: Missing field: domain
   ERROR: Invalid type: document
```

---

## Roadmap

### v0.1.x ✅ (Shipped)
- [x] System Prompt (universal LLM compatibility)
- [x] YAML Metadata Standard
- [x] Domain Taxonomy (30+ domains)
- [x] Validation Script (96% test coverage, 104 tests)
- [x] Multi-LLM CLI (Claude, Gemini, GPT-4, Ollama)
- [x] CI/CD Pipelines (GitHub Actions)
- [x] PyPI package (`pip install ai-knowledge-filler`)

### v0.2.x ✅ (Shipped)
- [x] Validation pipeline (Phase 2.1 — ValidationError, Error Normalizer, Retry Controller, Commit Gate)
- [x] Hard enum enforcement — E001–E006, 97% coverage (Phase 2.2)
- [x] Telemetry layer — append-only JSONL, generation_id, convergence metrics (Phase 2.3)

### v0.3.0 🔄 (Current)
- [x] Config layer — external `akf.yaml`, taxonomy configurable without code changes (Phase 2.4)
- [x] `akf init` — generates `akf.yaml` for a new vault
- [x] Validator Model D — `created ≤ updated` (E007), `title` isinstance str (E004)
- [ ] PyPI publish pending tag

### v1.0.0 (Planned — Phase 2.5)
- [ ] Onboarding & public announcement
---

## License

MIT License — Free for commercial and personal use.

---

## Philosophy

**This is knowledge engineering, not chat enhancement.**

LLMs are **deterministic infrastructure**, not conversational toys.

**Before:** "AI helps me write notes"
**After:** "AI compiles my knowledge base"

---

**Created by:** Petr — AI Solutions Architect
**PyPI:** https://pypi.org/project/ai-knowledge-filler/
**Repository:** https://github.com/petrnzrnk-creator/ai-knowledge-filler
**Version:** 0.3.0

---

## Support

- **Issues:** [GitHub Issues](https://github.com/petrnzrnk-creator/ai-knowledge-filler/issues)
- **Discussions:** [GitHub Discussions](https://github.com/petrnzrnk-creator/ai-knowledge-filler/discussions)

---

**Quick Links:**
[Quick Start](#-quick-start-60-seconds) | [CLI Commands](#cli-commands) | [Documentation](#documentation) | [Examples](#example-output)
