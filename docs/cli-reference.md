---
title: "AKF CLI Reference"
type: reference
domain: ai-system
level: intermediate
status: active
version: v1.0
tags: [cli, reference, commands, akf, llm, validate, generate]
related:
  - "[[docs/user-guide]]"
  - "[[07-REFERENCE/AKF_System_Docs/System_Prompt_AI_Knowledge_Filler]]"
  - "[[07-REFERENCE/Domain_Taxonomy]]"
created: 2026-02-19
updated: 2026-02-19
---

## Purpose

Complete reference for all `akf` CLI commands, flags, environment variables, and exit codes.  
Generated from `cli.py` + `llm_providers.py` — reflects actual behaviour.

---

## Commands Overview

```
akf <command> [options]

Commands:
  generate    Generate a structured Markdown knowledge file
  validate    Validate YAML frontmatter in Markdown files
  models      List available LLM providers and their status
```

---

## `akf generate`

Generate a knowledge file from a natural language prompt using an LLM provider.

**Usage:**
```bash
akf generate PROMPT [--model MODEL] [--output PATH]
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `PROMPT` | ✅ Yes | Natural language description of the file to generate |

**Options:**

| Flag | Short | Default | Values | Description |
|------|-------|---------|--------|-------------|
| `--model` | `-m` | `auto` | `auto` `claude` `gemini` `gpt4` `groq` `grok` `ollama` | LLM provider to use |
| `--output` | `-o` | see below | any path | Custom output directory |

**Default output path:**
```
/storage/emulated/0/Download/WorkingprogressAKF_Vault/04-DELIVERABLES/Code/
```
Override with `--output` to write anywhere.

**Filename resolution:**
Filename is extracted from the `title:` field in the generated YAML frontmatter.  
Format: `Title_Words.md` (spaces and hyphens → underscores, special chars stripped).  
If title extraction fails: first 4 words of the prompt, lowercased.  
If file already exists: timestamp suffix appended (`Name_143022.md`).

**Auto-validation:**
After saving, `akf validate` runs automatically on the output file.  
Result printed to stdout. Does not block save on failure — warnings only.

**Examples:**
```bash
# Auto-select provider (fastest available)
akf generate "Create a concept file about API Rate Limiting for the api-design domain"

# Specify provider
akf generate -m claude "Create a guide for Docker multi-stage builds"

# Custom output directory
akf generate -o /tmp/drafts "Create a security checklist for Python production deployments"

# Groq (fastest, free tier)
akf generate -m groq "Create a reference file for Git branching strategies"
```

---

## `akf validate`

Validate YAML frontmatter in one file, a directory, or current working directory.

**Usage:**
```bash
akf validate [--file FILE] [--path PATH] [--strict]
```

**Options:**

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--file` | `-f` | — | Validate a single Markdown file |
| `--path` | `-p` | — | Validate all `.md` files recursively in folder |
| `--strict` | `-s` | `False` | Promote warnings to errors (stricter gate) |

If neither `--file` nor `--path` is provided, validates all `**/*.md` in the current directory recursively.

**Exclusions (always skipped):**
- Files in `.github/` directories
- `README.md` files

**Output format:**
```
✅ path/to/file.md          — valid
⚠  path/to/file.md          — warnings (shown below)
❌ path/to/file.md          — errors (shown below)

→  Total: N | OK: N | Warnings: N | Errors: N
```

**Exit codes:**

| Code | Meaning |
|------|---------|
| `0` | All files valid (errors = 0) |
| `1` | One or more files have errors |

**Examples:**
```bash
# Single file
akf validate -f 02-ACTIVE-PHASE/Tasks/Task_Type_Hints.md

# Entire folder
akf validate -p 02-ACTIVE-PHASE/Tasks/

# Strict mode (warnings become errors)
akf validate -p 07-REFERENCE/ --strict

# Current directory (recursive)
akf validate
```

---

## `akf models`

List all LLM providers, their availability status, and active model names.

**Usage:**
```bash
akf models
```

**No options.** Output example:
```
→  Available LLM providers:

✅ groq       Groq (Llama 3.3)
   Model: llama-3.3-70b-versatile

❌ grok       Grok (xAI)
   Set XAI_API_KEY

✅ claude     Claude (Anthropic)
   Model: claude-sonnet-4-20250514

❌ gemini     Gemini (Google)
   Set GOOGLE_API_KEY

❌ gpt4       GPT-3.5 (OpenAI)
   Set OPENAI_API_KEY

❌ ollama     Ollama (llama3.2:3b)
   Run Ollama server
```

---

## Environment Variables

### API Keys

| Variable | Provider | Required for |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Claude (Anthropic) | `akf generate -m claude` |
| `GOOGLE_API_KEY` | Gemini (Google) | `akf generate -m gemini` |
| `OPENAI_API_KEY` | GPT-3.5 (OpenAI) | `akf generate -m gpt4` |
| `GROQ_API_KEY` | Groq (Llama 3.3) | `akf generate -m groq` |
| `XAI_API_KEY` | Grok (xAI) | `akf generate -m grok` |

### Ollama Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL` | `llama3.2:3b` | Model name to use with Ollama |
| `OLLAMA_BASE_URL` | `http://0.0.0.0:8080` | Ollama server address |

### Setting Keys (Termux / bash)

```bash
# Temporary (current session)
export ANTHROPIC_API_KEY="sk-ant-..."
export GROQ_API_KEY="gsk_..."

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
source ~/.bashrc
```

---

## Provider Reference

### Auto-select Priority

When `--model auto` (default), providers are tried in this order — first available wins:

```
groq → grok → claude → gemini → gpt4 → ollama
```

Groq is first because it's the fastest and has a free tier.

### Provider Details

| Key | Display Name | Model | Env Var | Install |
|-----|-------------|-------|---------|---------|
| `claude` | Claude (Anthropic) | `claude-sonnet-4-20250514` | `ANTHROPIC_API_KEY` | `pip install anthropic` |
| `gemini` | Gemini (Google) | `gemini-3-flash-preview` | `GOOGLE_API_KEY` | `pip install google-genai` |
| `gpt4` | GPT-3.5 (OpenAI) | `gpt-3.5-turbo` | `OPENAI_API_KEY` | `pip install openai` |
| `groq` | Groq (Llama 3.3) | `llama-3.3-70b-versatile` | `GROQ_API_KEY` | `pip install groq` |
| `grok` | Grok (xAI) | `grok-beta` | `XAI_API_KEY` | `pip install openai` |
| `ollama` | Ollama (local) | `llama3.2:3b` (default) | none | run Ollama server |

### Optional Provider Installs

Core install (`pip install ai-knowledge-filler`) includes only `anthropic`, `pyyaml`, `click`.  
Install extras as needed:

```bash
# All cloud providers
pip install ai-knowledge-filler[all-providers]

# Individual
pip install groq
pip install google-genai
pip install openai    # covers gpt4 + grok
```

---

## Retry Behaviour

On transient errors (timeout, rate limit, 429, 502, 503), `akf generate` retries automatically:

```
Attempt 1 → wait 1s → Attempt 2 → wait 2s → Attempt 3 → fail
```

Non-retryable errors (401, 403, invalid API key) fail immediately.

---

## Exit Codes

| Code | Command | Meaning |
|------|---------|---------|
| `0` | all | Success |
| `1` | `validate` | One or more validation errors found |
| `1` | `generate` | Provider unavailable, generation error, or missing system prompt |

---

## Common Error Messages

| Message | Cause | Fix |
|---------|-------|-----|
| `No LLM providers available` | No API keys set | `export GROQ_API_KEY=...` (fastest option) |
| `System prompt not found at: ...` | Package install incomplete | `pip install --force-reinstall ai-knowledge-filler` |
| `❌ Check API key and dependencies` | Key missing or wrong | Run `akf models` to diagnose |
| `Generation error: 401` | Invalid API key | Verify key at provider dashboard |
| `Validation found N issues` | Generated file has YAML errors | Check output file; re-run with different prompt if needed |
