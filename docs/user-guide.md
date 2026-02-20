---
title: "AKF User Guide"
type: guide
domain: ai-system
level: beginner
status: active
version: v1.0
tags: [user-guide, onboarding, installation, quickstart, akf, obsidian]
related:
  - "[[docs/cli-reference]]"
  - "[[07-REFERENCE/AKF_System_Docs/System_Prompt_AI_Knowledge_Filler]]"
  - "[[07-REFERENCE/Domain_Taxonomy]]"
  - "[[07-REFERENCE/Metadata_Template_Standard]]"
created: 2026-02-19
updated: 2026-02-19
---

## Purpose

Get from zero to your first generated Obsidian file in under 5 minutes.

---

## Prerequisites

- Python 3.10 or higher
- At least one API key (see [Provider Setup](#provider-setup)) — or a running Ollama instance

Check Python version:
```bash
python3 --version
# Python 3.10.x or higher required
```

---

## Installation

```bash
pip install ai-knowledge-filler
```

Verify:
```bash
akf --help
```

Expected output:
```
usage: akf [-h] {generate,validate,models} ...

positional arguments:
  {generate,validate,models}
    generate    Generate knowledge file
    validate    Check Markdown YAML
    models      List available LLM providers
```

---

## Provider Setup

AKF needs at least one LLM provider configured. Set the API key for your preferred provider.

**Recommended for first use — Groq (free tier, fastest):**
```bash
export GROQ_API_KEY="gsk_..."
```

**Other providers:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."   # Claude
export GOOGLE_API_KEY="AIza..."          # Gemini
export OPENAI_API_KEY="sk-..."           # GPT-3.5
export XAI_API_KEY="xai-..."            # Grok
```

**Make permanent (add to `~/.bashrc` or `~/.zshrc`):**
```bash
echo 'export GROQ_API_KEY="gsk_..."' >> ~/.bashrc
source ~/.bashrc
```

Check which providers are active:
```bash
akf models
```

---

## Quick Start

Five steps, under 5 minutes:

**Step 1 — Install**
```bash
pip install ai-knowledge-filler
```

**Step 2 — Set API key**
```bash
export GROQ_API_KEY="gsk_..."
```

**Step 3 — Generate your first file**
```bash
akf generate "Create a concept file about API Rate Limiting for the api-design domain"
```

**Step 4 — Check the output**
```
✅ Saved to: /path/to/vault/04-DELIVERABLES/Code/API_Rate_Limiting.md
✅ Validation passed!
```

**Step 5 — Open in Obsidian**

Copy or move the generated `.md` file into your Obsidian vault. The file is ready to use — valid YAML frontmatter, structured headings, Dataview-compatible metadata.

---

## Generating Files

### Basic generation

```bash
akf generate "PROMPT"
```

The prompt is a natural language description of the file you want. Be specific about:
- **What** the file should cover
- **Type** (concept, guide, checklist, reference, etc.)
- **Domain** (api-design, devops, security, etc.)

**Good prompts:**
```bash
akf generate "Create a guide for setting up GitHub Actions CI/CD for a Python project"
akf generate "Create a concept file about microservices architecture for the system-design domain"
akf generate "Create a security checklist for REST API production deployment"
akf generate "Create a reference file for Git branching strategies at intermediate level"
```

### Choose a provider

```bash
akf generate -m groq "Create a concept about OAuth 2.0"      # Groq (fastest)
akf generate -m claude "Create a concept about OAuth 2.0"    # Claude
akf generate -m gemini "Create a concept about OAuth 2.0"    # Gemini
```

Default (`-m auto`) tries providers in order: `groq → grok → claude → gemini → gpt4 → ollama`.

### Custom output directory

```bash
akf generate -o /path/to/my/vault/drafts "Create a guide for Docker networking"
```

Without `--output`, files go to `AKF_OUTPUT_DIR` (default: Termux vault path). Set it once to point at your vault:

```bash
export AKF_OUTPUT_DIR="/path/to/your/vault/04-DELIVERABLES/Code"
```

Add to `~/.bashrc` or `~/.zshrc` to persist across sessions.

---

## Validating Files

Validate YAML frontmatter in generated (or hand-written) files:

```bash
# Single file
akf validate -f my-note.md

# Entire folder
akf validate -p 02-ACTIVE-PHASE/Tasks/

# Current directory (recursive)
akf validate

# Strict mode — warnings become errors
akf validate -p 07-REFERENCE/ --strict
```

**Output:**
```
✅ Task_Type_Hints.md
✅ Task_Black_Format.md
⚠  Task_Pylint.md
   Missing recommended field: version
❌ Draft_Note.md
   Missing field: domain
   tags must be an array with at least 3 items

→  Total: 4 | OK: 2 | Warnings: 1 | Errors: 1
```

Exit code `1` if any errors found — use in CI pipelines:
```bash
akf validate -p docs/ && echo "All good" || echo "Fix errors above"
```

---

## Using Generated Files in Obsidian

All AKF-generated files include:

- **YAML frontmatter** — compatible with Dataview, Templater, and Obsidian Properties
- **WikiLink format** in `related:` field — renders as clickable links in Obsidian graph
- **Mermaid diagrams** (where applicable) — rendered natively by Obsidian
- **Structured headings** — `##` / `###` hierarchy, no level skips

**Dataview query example** — list all generated files by domain:
```dataview
TABLE title, status, level
FROM "04-DELIVERABLES"
WHERE domain = "api-design"
SORT updated DESC
```

**Move to your vault:**
```bash
# Copy to Obsidian vault folder
cp /path/to/generated/API_Rate_Limiting.md ~/Documents/MyVault/07-REFERENCE/
```

Or configure `OUTPUT_DIR` in `cli.py` to point directly at your vault.

---

## Example Output

A generated concept file looks like this:

```markdown
---
title: "API Rate Limiting"
type: concept
domain: api-design
level: intermediate
status: active
tags: [api, rate-limiting, performance, throttling, api-design]
related:
  - "[[API Design Principles]]"
  - "[[API Security Review Checklist]]"
  - "[[System Scalability Patterns]]"
created: 2026-02-19
updated: 2026-02-19
---

## Overview

API rate limiting controls the number of requests a client can make in a given
time window. It protects backend services from overload and abuse.

## Core Strategies

### Token Bucket
...

## Conclusion

Choose rate limiting strategy based on traffic pattern and fairness requirements.
```

---

## Troubleshooting

**`akf: command not found`**
```bash
# Verify installation
pip show ai-knowledge-filler

# If installed but not on PATH:
python3 -m akf generate "..."   # workaround
# Or add pip bin to PATH:
export PATH="$PATH:$(python3 -m site --user-base)/bin"
```

**`No LLM providers available`**
```bash
# Check what's configured
akf models

# Set at least one key
export GROQ_API_KEY="gsk_..."   # free at console.groq.com
```

**`System prompt not found`**
```bash
# Reinstall to restore bundled assets
pip install --force-reinstall ai-knowledge-filler
```

**`Generation error: 401`**
API key is invalid or expired. Regenerate at your provider's dashboard.

**`Validation found N issues` after generate**
The generated file has YAML warnings. Open the file and check:
- `tags` must be an array: `[tag1, tag2, tag3]`
- `domain` must match [[Domain_Taxonomy]] (lowercase-hyphenated)
- All dates must be `YYYY-MM-DD`

---

## Next Steps

- **[CLI Reference](cli-reference.md)** — all commands, flags, exit codes
- **[Domain Taxonomy](../07-REFERENCE/Domain_Taxonomy.md)** — valid domain values
- **[Metadata Standard](../07-REFERENCE/Metadata_Template_Standard.md)** — YAML field spec
- **[Contributing](../CONTRIBUTING.md)** — add a provider, run tests, submit PRs
