# AI Knowledge Filler

**Validation pipeline for LLM-generated structured Markdown**

[![Tests](https://github.com/petrnzrnk-creator/ai-knowledge-filler/workflows/Tests/badge.svg)](https://github.com/petrnzrnk-creator/ai-knowledge-filler/actions/workflows/tests.yml)
[![Lint](https://github.com/petrnzrnk-creator/ai-knowledge-filler/workflows/Lint/badge.svg)](https://github.com/petrnzrnk-creator/ai-knowledge-filler/actions/workflows/lint.yml)
[![PyPI](https://img.shields.io/pypi/v/ai-knowledge-filler.svg)](https://pypi.org/project/ai-knowledge-filler/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Coverage](https://img.shields.io/badge/coverage-94.6%25-brightgreen.svg)](https://github.com/petrnzrnk-creator/ai-knowledge-filler/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## The Problem

LLMs generate text. You need structured, schema-compliant files.

Without a validation layer, AI-generated Markdown produces:

| Error | Raw LLM output | What you need |
|-------|---------------|---------------|
| Enum violation | `level: expert` | `beginner \| intermediate \| advanced` |
| Domain violation | `domain: Technology` | `domain: system-design` |
| Type mismatch | `tags: security` | `tags: [security, api, auth]` |
| Date format | `created: 12-02-2026` | `created: 2026-02-12` |

One file? Fixable manually. A hundred files? The schema collapses.

**AKF enforces the contract at generation time, not review time.**

---

## How It Works

```
Prompt
  → LLM                  (only non-deterministic component)
  → Validation Engine    (binary: VALID or INVALID + typed E-codes)
  → Error Normalizer     (deterministic repair instructions from E-codes)
  → Retry Controller     (max 3 attempts — aborts on identical failure hash)
  → Commit Gate          (atomic write — only VALID output reaches disk)
```

No silent failures. No partial commits. No guessing.

**Retry = ontology signal.** When a domain triggers elevated retries, the taxonomy has a boundary problem — not the model. Telemetry captures this.

---

## Quick Start

```bash
pip install ai-knowledge-filler

# Groq is free and fastest to start
export GROQ_API_KEY="gsk_..."

akf generate "Create a Docker networking guide"
# → outputs/Docker_Networking_Guide.md (validated, schema-compliant)
```

---

## Python API

```python
from akf import Pipeline

pipeline = Pipeline(output="./vault/", model="groq")

# Single file
result = pipeline.generate("Create API rate limiting guide")
print(result.success)        # True
print(result.path)           # PosixPath('vault/API_Rate_Limiting_Guide.md')
print(result.attempts)       # 1 (retried if schema violation)
print(result.generation_id)  # uuid4 — join to telemetry log

# Batch
results = pipeline.batch_generate([
    "Docker deployment best practices",
    "Kubernetes security hardening",
    "API authentication strategies",
])

# Validate existing file
v = pipeline.validate("vault/my_file.md")
print(v.valid, v.errors)
```

---

## REST API

```bash
akf serve --port 8000

# Generate
curl -X POST http://localhost:8000/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create Docker security checklist", "model": "groq"}'

# Batch
curl -X POST http://localhost:8000/v1/batch \
  -H "Content-Type: application/json" \
  -d '{"prompts": ["Docker guide", "Kubernetes guide"]}'

# Validate
curl -X POST http://localhost:8000/v1/validate \
  -H "Content-Type: application/json" \
  -d '{"content": "---\ntitle: Test\n..."}'
```

Endpoints: `POST /v1/generate` · `POST /v1/validate` · `POST /v1/batch` · `GET /v1/models` · `GET /health`

Swagger UI: `http://localhost:8000/docs`

---

## What Every Committed File Guarantees

- Required fields: `title`, `type`, `domain`, `level`, `status`, `tags`, `created`, `updated`
- Valid enums: `type`, `level`, `status` from controlled sets
- Domain from configured taxonomy (`akf.yaml`) — not hardcoded
- ISO 8601 dates with `created ≤ updated`
- `tags` as array (≥3), `title` as string

Violations produce error codes E001–E007. Repair instructions are derived from those codes.

### Error Codes

| Code | Field | Meaning |
|------|-------|---------|
| E001 | type / level / status | Invalid enum value |
| E002 | any | Required field missing |
| E003 | created / updated | Date not ISO 8601 |
| E004 | title / tags | Type mismatch |
| E005 | frontmatter | General schema violation |
| E006 | domain | Not in taxonomy |
| E007 | created / updated | `created > updated` |

---

## Example Output

**Input:**
```
Create guide on API rate limiting
```

**Output (`outputs/API_Rate_Limiting_Guide.md`):**
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
## Core Principles
## Implementation
## Conclusion
```

Schema-valid on first attempt (or retried until it is).

---

## Configuration

Taxonomy is external — no code changes needed:

```yaml
# akf.yaml
schema_version: "1.0.0"
vault_path: "./vault"

enums:
  type: [concept, guide, reference, checklist, project, roadmap, template, audit]
  level: [beginner, intermediate, advanced]
  status: [draft, active, completed, archived]
  domain:
    - ai-system
    - api-design
    - devops
    - security
    - system-design
    # add your own
```

Initialize for a new project:
```bash
akf init          # creates akf.yaml in current directory
akf init --force  # overwrite existing
```

---

## CLI Reference

```bash
# Generate
akf generate "prompt"
akf generate "prompt" --model groq|claude|gemini|gpt4|ollama
akf generate "prompt" --output ./my-vault/

# Validate
akf validate                    # all files in outputs/
akf validate --file path/to.md  # single file

# Server
akf serve
akf serve --port 8001
akf serve --host 0.0.0.0 --port 8000

# Models
akf models  # show available providers + status

# Init
akf init
```

---

## Model Selection

| Model | Key | Speed | Cost | Notes |
|-------|-----|-------|------|-------|
| **Groq** | `GROQ_API_KEY` | ⚡ | Free tier | Recommended for CI, high volume |
| **Claude** | `ANTHROPIC_API_KEY` | Medium | $$$ | Technical docs, architecture |
| **Gemini** | `GOOGLE_API_KEY` | Fast | $ | Quick drafts |
| **GPT-4** | `OPENAI_API_KEY` | Medium | $$ | General purpose |
| **Grok** | `XAI_API_KEY` | Fast | $$ | General purpose |
| **Ollama** | — | Fast | Free | Local / offline / private |

Auto-selection order: Groq → Grok → Claude → Gemini → GPT-4 → Ollama (first key found).

---

## Telemetry

Each generation appends a structured event to `telemetry/akf_telemetry.jsonl`:

```json
{
  "generation_id": "uuid-v4",
  "document_id": "abc123",
  "schema_version": "1.0.0",
  "attempt": 1,
  "max_attempts": 3,
  "errors": [],
  "converged": true,
  "timestamp": "2026-02-27T14:22:01Z",
  "model": "groq",
  "temperature": 0
}
```

Telemetry is append-only and never influences the pipeline at runtime. Use it to measure ontology friction per domain, detect prompt drift, and validate schema changes.

---

## Security

```bash
# Optional API key — if unset, server runs in dev mode (all requests pass)
export AKF_API_KEY="your-secret"

# CORS
export AKF_CORS_ORIGINS="https://your-app.com,https://another.com"
```

Rate limits (per IP): `POST /v1/generate` 10/min · `POST /v1/validate` 30/min · `POST /v1/batch` 3/min

---

## Quality

- **487 tests**, 94.6% coverage
- CI green on Python 3.10 / 3.11 / 3.12
- Type hints: 100%
- Pylint: 9.55/10

```bash
pytest --cov=. --cov-report=term-missing
akf validate
pylint *.py tests/
```

---

## Roadmap

### Shipped
- [x] CLI — multi-provider (`akf generate`, `akf validate`, `akf serve`, `akf init`)
- [x] Validation pipeline — E001–E007, retry loop, commit gate
- [x] Telemetry — append-only JSONL, generation_id, convergence metrics
- [x] Config layer — external `akf.yaml`, taxonomy configurable without code changes
- [x] Pipeline API — `from akf import Pipeline`
- [x] REST API — FastAPI, Swagger UI, rate limiting, optional auth

### Planned
- [ ] `akf generate --batch topics.txt`
- [ ] Graph extraction layer
- [ ] n8n / Make integration templates

---

## Documentation

- [Architecture](https://github.com/petrnzrnk-creator/ai-knowledge-filler/blob/main/ARCHITECTURE.md) — Module map, data flow, extension points
- [CLI Reference](https://github.com/petrnzrnk-creator/ai-knowledge-filler/blob/main/docs/cli-reference.md) — All commands, flags, env vars, exit codes
- [Contributing](https://github.com/petrnzrnk-creator/ai-knowledge-filler/blob/main/CONTRIBUTING.md) — Dev setup, adding providers

---

## License

MIT — Free for commercial and personal use.

---

**PyPI:** https://pypi.org/project/ai-knowledge-filler/ | **Version:** 0.4.2
