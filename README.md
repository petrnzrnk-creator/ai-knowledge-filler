# AI Knowledge Filler

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Transform any LLM into a deterministic knowledge base generator**

A production-ready system that transforms conversational AI outputs into structured, compliant Markdown files with YAML metadata for knowledge bases like Obsidian.

---

## 🎯 What This Does

Turns any LLM (Claude, GPT-4, Gemini, local models) into a **deterministic file generator** that produces:

- ✅ Structured Markdown with YAML frontmatter
- ✅ Consistent metadata across all files
- ✅ WikiLink-based knowledge graphs
- ✅ Production-ready documentation (zero manual formatting)

**Not a chatbot enhancement. A knowledge engineering architecture.**

---

## ⚡ Quick Start (60 seconds)

### Option 1: Claude.ai (Fastest)

1. Open https://claude.ai
2. Create new Project → "Knowledge Generator"
3. Project Knowledge → Upload `Core_System/System_Prompt_AI_Knowledge_Filler.md`
4. Start generating: `"Create guide on API authentication"`

Done. Claude now generates structured files instead of chat.

### Option 2: Python API

```bash
pip install -r requirements.txt


```python
import anthropic

with open('Core_System/System_Prompt_AI_Knowledge_Filler.md') as f:
    system_prompt = f.read()

client = anthropic.Anthropic(api_key="your-key")
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=system_prompt,
    messages=[{"role": "user", "content": "Create guide on Docker deployment"}]
)

print(response.content[0].text)


---

## 📦 What's Included

- **10 Core System Files** — Complete knowledge engineering framework
- **Automated Validation** — YAML metadata compliance checking
- **30+ Domain Taxonomy** — Standardized classifications
- **20+ Use Cases** — Real-world scenarios
- **GitHub Actions** — CI/CD validation workflow

---

## 🏗️ Architecture


User Request → System Prompt → Execution Protocol → Metadata Standards → Structured Output


**Result:** Same input → Same structure. Every time.

---

## 📊 Key Features

| Feature | Benefit |
|---------|---------|
| **Universal LLM Support** | Works with Claude, GPT-4, Gemini, Llama, Mistral |
| **Zero Manual Formatting** | Publication-ready files on first generation |
| **Deterministic Output** | Consistent structure across all generations |
| **Obsidian Native** | Direct integration with knowledge graphs |
| **Version Control Ready** | Git-friendly Markdown with proper metadata |

---

## 📋 Example Output

**Input:**

Create guide on API rate limiting


**Output:**
```markdown
---
title: "API Rate Limiting Strategy"
type: guide
domain: api-design
level: intermediate
status: active
version: v1.0
tags: [api, rate-limiting, performance]
related:
  - [[API Design Principles]]
created: 2026-02-10
updated: 2026-02-10
---

## Purpose
Comprehensive strategy for implementing API rate limits...

[Structured content with sections, code examples, best practices]


Every file. Same structure. Production-ready.

---

## 🔧 Validation

```bash
cd Scripts
python validate_yaml.py


Checks:
- YAML frontmatter presence
- Required fields (title, type, domain, level, status, dates)
- Valid enum values
- ISO 8601 date format
- Tag array structure

---

## 📚 Documentation

- [Core System](Core_System/) — System prompts and standards
- [Documentation](Documentation/) — Deployment and use cases
- [Examples](Examples/) — Reference implementations
- [Contributing](CONTRIBUTING.md) — Contribution guidelines

---

## 🎓 Use Cases

- **Technical Documentation** — API docs, architecture decisions, system designs
- **Knowledge Management** — Personal knowledge bases, research notes, learning materials
- **Consulting Deliverables** — Frameworks, methodologies, client reports
- **Team Documentation** — SOPs, checklists, onboarding guides

[View 20+ detailed scenarios](Documentation/Use_Cases_Documentation.md)

---

## 🛠️ Requirements

- Python 3.8+
- pyyaml>=6.0
- anthropic>=0.18.0 (for API usage)

---

## 📜 License

MIT License — Free for commercial and personal use.

---

## 🚀 Roadmap

### v2.3
- [ ] CLI tool for batch generation
- [ ] Enhanced search functionality
- [ ] Multi-language support

### v3.0
- [ ] Visual workflow designer
- [ ] Real-time collaboration
- [ ] Enterprise features

---

## 💡 Philosophy

**Knowledge engineering, not chat enhancement.**

LLMs should be deterministic infrastructure, not conversational novelty.

From "AI helps write notes" → "AI compiles my knowledge base"

---

## ⭐ Show Your Support

If this system saves you time, star the repository and share with your team.

---

**Created by:** Petro — AI Knowledge Architect  
**Version:** 2.2.0  
**Last Updated:** 2026-02-10

---

**Quick Links:**
[Installation](#-quick-start-60-seconds) | [Use Cases](Documentation/Use_Cases_Documentation.md) | [Examples](Examples/) | [Contributing](CONTRIBUTING.md)
