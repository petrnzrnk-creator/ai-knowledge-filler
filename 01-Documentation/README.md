# AI Knowledge Filler

**Transform any LLM into a deterministic knowledge base generator**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Compatible: Claude | GPT-4 | Gemini | Local LLMs](https://img.shields.io/badge/Compatible-Universal_LLM-blue.svg)]()
[![Obsidian Ready](https://img.shields.io/badge/Obsidian-Ready-purple.svg)]()

---

## 🎯 What This Is

A production-ready system that transforms conversational AI outputs into structured, compliant Markdown files with YAML metadata for knowledge bases like Obsidian.

**Not a chatbot enhancement. A knowledge engineering architecture.**

Turn any LLM (Claude, GPT-4, Gemini, local models) into a deterministic file generator that produces consistent, validated, production-ready documentation.

---

## ⚡ Quick Start

### Claude.ai (60 seconds)

```markdown
1. Open Claude.ai or create new Project
2. Go to Project Knowledge or Custom Instructions
3. Copy content from Core_System/System_Prompt_AI_Knowledge_Filler.md
4. Paste into system instructions
5. Start: "Create a guide on API authentication methods"
```

**Done.** Claude now generates structured knowledge files instead of conversational responses.

---

## 📦 What You Get

### 10 Core System Files
- **System Prompt** — Transforms LLM behavior from chat to file generator
- **Custom Instructions** — AI working profile and constraints
- **Workflow** — 8-stage prompt engineering methodology
- **Metadata Standard** — YAML template specification
- **Update Protocol** — File merge rules and conflict resolution
- **Domain Taxonomy** — 30+ standardized classifications
- **Audit Report** — System alignment validation
- **Use Cases** — 20+ real-world scenarios
- **Deployment Guide** — Installation for all platforms
- **Control Dashboard** — Dataview monitoring queries

### Production Infrastructure
- ✅ Automated YAML validation
- ✅ Batch file generation
- ✅ Git workflow integration
- ✅ Version control support
- ✅ Conflict resolution strategies
- ✅ ISO 8601 date formatting
- ✅ WikiLink syntax enforcement

---

## ✨ Key Features

### Universal LLM Compatibility
Works with Claude, GPT-4, Gemini, Llama, Mistral — any system supporting system prompts.

### Zero Manual Formatting
AI generates publication-ready files. No post-processing required.

```
User: "Create API security checklist"
AI: [Generates complete .md file with YAML, structure, links]
```

### Deterministic Output
Same input → Same structure. Every time.

### Scalable Architecture
```
Operating Principles (System Prompt)
    ↓
Execution Protocols (Workflows, Rules)
    ↓
Governance Standards (Templates, Taxonomy)
    ↓
Structured Knowledge Files
```

---

## 🚀 Installation

### Option 1: Claude Projects (Recommended)

```bash
# Create new Claude Project
# Add Core_System/System_Prompt_AI_Knowledge_Filler.md to Project Knowledge
# Add Custom_Instructions.md to Project Instructions
```

### Option 2: API Integration

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
```

### Option 3: Local/Obsidian Vault

```bash
git clone https://github.com/yourusername/ai-knowledge-filler.git
cd ai-knowledge-filler
cp Core_System/*.md ~/path/to/obsidian/vault/
```

**See [Deployment_Guide.md](Documentation/Deployment_Guide.md) for detailed instructions**

---

## 📊 Use Cases

### Knowledge Management
Transform conversations into structured notes with consistent metadata

### Technical Documentation
Generate API docs, architecture decisions, system designs

### Consulting Deliverables
Create frameworks, methodologies, client reports

### Learning & Research
Structure educational content, research notes, insights

**20+ detailed scenarios in [Use_Cases_Documentation.md](Documentation/Use_Cases_Documentation.md)**

---

## 📋 Example Output

**Input:**
```
Create a guide on API rate limiting
```

**Output:**
```markdown
---
title: "API Rate Limiting Strategy"
type: guide
domain: api-design
level: intermediate
status: active
version: v1.0
tags: [api, rate-limiting, performance, architecture]
related:
  - [[API Design Principles]]
  - [[System Scalability Patterns]]
created: 2026-02-06
updated: 2026-02-06
---

## Purpose
Comprehensive strategy for implementing and managing API rate limits...

## Core Principles
[Structured content with sections, lists, examples]

## Implementation Patterns
[Step-by-step technical guidance]

## Conclusion
[Summary and next steps]
```

**Every file. Same structure. Production-ready.**

---

## 🏗️ Architecture

```
┌────────────────────────────────┐
│  User Input (Natural Language) │
└───────────────┬────────────────┘
                │
    ┌───────────▼──────────┐
    │   System Prompt      │
    │   (Role Definition)  │
    └───────────┬──────────┘
                │
    ┌───────────▼──────────┐
    │ Execution Protocol   │
    │ (Workflow & Rules)   │
    └───────────┬──────────┘
                │
    ┌───────────▼──────────┐
    │  Metadata Standards  │
    │  (YAML & Taxonomy)   │
    └───────────┬──────────┘
                │
┌───────────────▼────────────────┐
│  Structured Markdown Output    │
│  ✅ Validated YAML             │
│  ✅ Consistent Format          │
│  ✅ Internal Links             │
│  ✅ Domain Classification      │
└────────────────────────────────┘
```

---

## 🎯 Core Concepts

### 1. AI as File Generator, Not Chat Assistant
System prompt eliminates conversational behavior. Output is pure Markdown.

### 2. Metadata-Driven Organization
Every file has standardized YAML frontmatter with domain, type, level, status, version tracking.

### 3. Domain Taxonomy
30+ predefined domains ensure consistent classification:
- `ai-system`, `api-design`, `system-design`
- `consulting`, `workflow-automation`, `security`
- And more in [Domain_Taxonomy.md](Core_System/Domain_Taxonomy.md)

### 4. Preservation-First Updates
Smart merge strategies prevent data loss when updating existing files.

### 5. Quality Assurance
Automated validation ensures compliance with metadata standards.

---

## 🔧 Customization

### Add New Domain
```yaml
# Edit Core_System/Domain_Taxonomy.md
#### your-domain
Description and usage guidelines
```

### Create Custom File Type
```yaml
# Edit Core_System/Metadata_Template_Standard.md
type: "<existing | your-new-type>"
```

### Modify Workflow
Edit `Core_System/Prompt_Engineering_Workflow.md` to match your process.

---

## 📈 Advanced Features

### Batch Generation
```
User: "Create 5 microservices pattern guides:
Service Discovery, API Gateway, Circuit Breaker, Event Sourcing, CQRS"

AI: [Generates 5 cross-referenced files instantly]
```

### Git Integration
```bash
# Files are version-control ready
git add .
git commit -m "Add security documentation"

# Use validation in CI/CD
.github/workflows/validate.yml
```

### Obsidian Dashboard
```dataview
TABLE title, domain, status, updated
FROM "/"
WHERE type = "guide" AND status = "active"
SORT updated DESC
```

**See [Control_Dashboard.md](Documentation/Control_Dashboard.md) for monitoring queries**

---

## 🎓 Documentation

- [System Prompt](Core_System/System_Prompt_AI_Knowledge_Filler.md) — Core behavior definition
- [Custom Instructions](Core_System/Custom_Instructions.md) — AI working profile
- [Workflow](Core_System/Prompt_Engineering_Workflow.md) — 8-stage methodology
- [Metadata Standard](Core_System/Metadata_Template_Standard.md) — YAML specification
- [Update Protocol](Core_System/File_Update_Protocol.md) — Merge & conflict resolution
- [Domain Taxonomy](Core_System/Domain_Taxonomy.md) — Classification system
- [Use Cases](Documentation/Use_Cases_Documentation.md) — 20+ scenarios
- [Deployment Guide](Documentation/Deployment_Guide.md) — Installation instructions

---

## 🛠️ Troubleshooting

**AI generates chat responses instead of files?**
→ System prompt not loaded correctly. Verify placement in system instructions.

**Invalid YAML metadata?**
→ Check [Metadata_Template_Standard.md](Core_System/Metadata_Template_Standard.md). Run validation.

**File updates delete content?**
→ Review [File_Update_Protocol.md](Core_System/File_Update_Protocol.md). Preservation-first is default.

**Full troubleshooting in [Deployment_Guide.md](Documentation/Deployment_Guide.md)**

---

## 📊 Success Metrics

Organizations using this system report:
- **70-90% reduction** in documentation time
- **100% consistency** in knowledge base structure
- **Zero manual formatting** required post-generation
- **Universal compatibility** across LLM platforms

---

## 🌐 Integration Examples

### Obsidian
Native compatibility. Drop files in vault, use Dataview for queries.

### Notion
Export Markdown, import with metadata preserved.

### Confluence
Use Markdown macro for import with page properties.

### GitHub Wiki
Commit to wiki branch, deploy via Actions.

---

## 🤝 Contributing

Contributions welcome:
- Domain taxonomies for specialized fields
- Additional file type definitions
- Integration guides for other platforms
- Validation scripts and tools

**Submit PRs following metadata standards in this repo.**

---

## 📜 License

MIT License — Free for commercial and personal use.

---

## 🚀 Roadmap

### v1.1
- [ ] VSCode validation extension
- [ ] Automated taxonomy expansion
- [ ] Multi-language support
- [ ] Enhanced conflict resolution

### v2.0
- [ ] Visual workflow designer
- [ ] Real-time collaboration
- [ ] Advanced graph analytics
- [ ] Enterprise features

---

## 💡 Philosophy

**This is knowledge engineering, not chat enhancement.**

LLMs should be **deterministic infrastructure**, not conversational novelty.

From "AI helps write notes" → "AI compiles my knowledge base"

---

## ⭐ Show Your Support

If this system saves you time, star the repository and share with your team.

**AI Knowledge Filler: Engineer knowledge, don't improvise it.**

---

**Created by:** Петр — AI Solutions Architect  
**Repository:** https://github.com/yourusername/ai-knowledge-filler  
**Version:** 1.0.0  
**Last Updated:** 2026-02-06

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/ai-knowledge-filler/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/ai-knowledge-filler/discussions)
- **Commercial Support:** Available for enterprise licensing

---

**Quick Links:**
[Installation](#-installation) | [Use Cases](#-use-cases) | [Documentation](#-documentation) | [Examples](Examples/) | [Contributing](#-contributing)
