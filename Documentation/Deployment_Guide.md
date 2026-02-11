---
title: "Deployment Guide — AI Knowledge Filler"
type: guide
domain: ai-system
level: intermediate
status: active
version: v1.0
tags: [deployment, installation, setup, configuration]
related:
  - "[[System_Prompt_AI_Knowledge_Filler]]"
  - "[[Custom_Instructions]]"
  - "[[Use_Cases_Documentation]]"
created: 2026-02-06
updated: 2026-02-06
---

## PURPOSE

Step-by-step deployment instructions for AI Knowledge Filler across all supported platforms.

---

## PLATFORM OPTIONS

| Platform | Time | Level | Best For |
|----------|------|-------|----------|
| Claude.ai Web | 2 min | Beginner | Quick start, testing |
| Claude Projects | 3 min | Beginner | Persistent workflows |
| API Integration | 10 min | Intermediate | Automation, batch ops |
| Obsidian Local | 5 min | Beginner | Knowledge management |
| Termux Mobile | 15 min | Advanced | Mobile workflows |

---

## CLAUDE.AI WEB (FASTEST)

### Steps

1. Go to https://claude.ai
2. Start new conversation
3. Copy `Core_System/System_Prompt_AI_Knowledge_Filler.md`
4. Paste into conversation
5. Start generating: "Create guide on API security"

### Limitations
- System prompt resets per conversation
- Manual paste required each session

---

## CLAUDE PROJECTS (RECOMMENDED)

### Setup

1. **Create Project**
   - Claude.ai → Projects → Create Project
   - Name: "Knowledge Generator"

2. **Add System Prompt**
   - Project Knowledge → Add Content
   - Paste `System_Prompt_AI_Knowledge_Filler.md`

3. **Add Instructions**
   - Custom Instructions → Paste `Custom_Instructions.md`

4. **Add References** (Optional)
   - Upload `Metadata_Template_Standard.md`
   - Upload `Domain_Taxonomy.md`
   - Upload `File_Update_Protocol.md`

### Usage
All conversations inherit system configuration. Persistent across sessions.

---

## API INTEGRATION

### Installation

```bash
pip install anthropic
```

### Basic Script

```python
import anthropic
import os

# Load system prompt
with open('Core_System/System_Prompt_AI_Knowledge_Filler.md') as f:
    system_prompt = f.read()

# Initialize
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Generate
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=system_prompt,
    messages=[{"role": "user", "content": "Create guide on Docker"}]
)

# Save
with open('Docker_Guide.md', 'w') as f:
    f.write(message.content[0].text)
```

### Batch Processing

```python
requests = [
    "Create concept: Microservices",
    "Create guide: API design",
    "Create checklist: Security review"
]

for req in requests:
    result = generate_file(req)
    save_file(result)
```

---

## OBSIDIAN VAULT

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/ai-knowledge-filler.git

# Copy to vault
cp -r Core_System ~/Obsidian/Vault/00-system/
cp -r Documentation ~/Obsidian/Vault/01-docs/
```

### Obsidian Configuration

1. Install Plugins:
   - Dataview (required)
   - Templater (recommended)

2. Enable Dataview:
   - Settings → Dataview
   - Enable JavaScript queries

3. Copy Control Dashboard:
   - Place `Control_Dashboard.md` in vault root

### Workflow

1. Generate file with Claude.ai
2. Copy Markdown output
3. Paste into Obsidian
4. Links auto-connect

---

## TERMUX (MOBILE)

### Prerequisites

```bash
# Install Termux from F-Droid
pkg update && pkg upgrade
pkg install python git
pip install anthropic python-dotenv
```

### Setup

```bash
cd ~/storage/shared
git clone https://github.com/yourusername/ai-knowledge-filler.git
cd ai-knowledge-filler

# Configure API key
echo "ANTHROPIC_API_KEY=your-key" > .env

# Test
python generate.py "Create guide on APIs"
```

---

## VALIDATION

### Test Generation

```
Input: "Create concept on REST APIs"

Expected:
✅ YAML frontmatter present
✅ All required fields (title, type, domain, etc.)
✅ Structured content sections
✅ No conversational text
✅ WikiLink format [[links]]
```

### YAML Validation Script

```python
import yaml

def validate(file):
    with open(file) as f:
        content = f.read()
    
    yaml_content = content.split('---')[1]
    metadata = yaml.safe_load(yaml_content)
    
    required = ['title', 'type', 'domain', 'level', 
                'status', 'tags', 'created', 'updated']
    
    for field in required:
        assert field in metadata, f"Missing: {field}"
    
    print("✅ Valid")
```

---

## TROUBLESHOOTING

### AI Generates Chat Responses
**Fix:** Verify system prompt loaded in Project Knowledge

### Invalid YAML
**Fix:** Add `Metadata_Template_Standard.md` to context

### Files Delete Content on Update
**Fix:** Upload `File_Update_Protocol.md` to enforce preservation

### API Rate Limits
**Fix:** Implement exponential backoff, batch operations

---

## SECURITY

```bash
# Never commit keys
echo ".env" >> .gitignore

# Use environment variables
export ANTHROPIC_API_KEY="key"

# Rotate keys regularly
```

---

## NEXT STEPS

1. Choose platform
2. Run validation test
3. Generate first file
4. Review quality
5. Scale to production

See [Use_Cases_Documentation.md](Use_Cases_Documentation.md) for applications.
