#!/usr/bin/env bash
# AKF — R-1 / R-2 / R-3 / R-4 automation
# Run from root of ai-knowledge-filler repo
# Usage: bash akf_r1_r4.sh

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

echo "→ Repo: $REPO_ROOT"

# ── Safety checks ──────────────────────────────────────────────────────────────
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "⚠  Uncommitted changes detected — staging all (git add -A)"
  git add -A
fi

if git tag | grep -q "^v0.3.0$"; then
  echo "⚠  Tag v0.3.0 already exists. Deleting local + remote..."
  git tag -d v0.3.0
  git push origin :refs/tags/v0.3.0 2>/dev/null || true
fi

# ── R-3: pyproject.toml ────────────────────────────────────────────────────────
echo "→ R-3: bumping pyproject.toml to 0.3.0"
sed -i 's/^version = "0\.2\.[0-9]*"/version = "0.3.0"/' pyproject.toml
grep "^version" pyproject.toml

# ── R-1 + R-2: README.md ──────────────────────────────────────────────────────
echo "→ R-1 / R-2: patching README.md"

python3 - <<'PYEOF'
import re, pathlib

readme = pathlib.Path("README.md")
text = readme.read_text(encoding="utf-8")

OLD_BLOCK = re.compile(
    r"## Problem → Solution\n.*?(?=\n---\n)",
    re.DOTALL
)

NEW_BLOCK = """\
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
| Enum violation | `level: expert` → valid: `beginner \\| intermediate \\| advanced` |
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
Telemetry captures this signal. Ontology improves from data, not intuition."""

if not OLD_BLOCK.search(text):
    print("❌  'Problem → Solution' block not found — already patched?")
    import sys; sys.exit(1)

patched = OLD_BLOCK.sub(NEW_BLOCK, text)

# Footer version
patched = patched.replace("**Version:** 0.2.0", "**Version:** 0.3.0")

# Roadmap: replace v0.2.x Current block
OLD_ROADMAP = re.compile(
    r"### v0\.2\.x ✅ \(Current\)\n.*?(?=\n---\n|\Z)",
    re.DOTALL
)
NEW_ROADMAP = """\
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
- [ ] Onboarding & public announcement"""

patched = OLD_ROADMAP.sub(NEW_ROADMAP, patched)

readme.write_text(patched, encoding="utf-8")
print("✅  README.md patched")
PYEOF

# ── Commit ─────────────────────────────────────────────────────────────────────
echo "→ Committing R-1/R-2/R-3"
git add README.md pyproject.toml
git diff --cached --stat

git commit -m "chore: bump v0.3.0 + Vision block in README

R-1: AINCOS Vision block (The Problem table, Guarantees, Retry=Ontology Signal)
R-2: Remove old Problem→Solution paragraph
R-3: pyproject.toml 0.2.0 → 0.3.0
Roadmap updated: v0.2.x shipped, v0.3.0 current, v1.0.0 planned."

# ── R-4: tag + push ────────────────────────────────────────────────────────────
echo "→ R-4: tagging v0.3.0 and pushing"
git tag v0.3.0
git push origin main
git push origin v0.3.0

echo ""
echo "✅ R-1 → R-4 complete."
echo "   CI will pick up v0.3.0 tag → R-5 (PyPI) runs automatically."
