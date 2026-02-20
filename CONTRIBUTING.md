# Contributing to AKF

Thank you for contributing to AI Knowledge Filler.

---

## Quick Start

```bash
git clone https://github.com/petrnzrnk-creator/ai-knowledge-filler
cd ai-knowledge-filler
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Verify setup:
```bash
pytest --tb=short        # all tests pass
akf --help               # CLI available
```

---

## Development Environment

**Requirements:** Python 3.10+, pip, git

**Install dev dependencies:**
```bash
pip install pytest pytest-cov black pylint mypy
# or via pyproject.toml extras:
pip install -e ".[dev]"
```

**Environment variables** (set at least one for live provider tests):
```bash
export GROQ_API_KEY="gsk_..."       # free, recommended for dev
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## Quality Gates

All PRs must pass these gates before merge:

```bash
# 1. Tests — 100% must pass
pytest --tb=short

# 2. Coverage — must not decrease
pytest --cov=. --cov-report=term-missing

# 3. Format check
black --check .

# 4. Lint — score ≥ 9.0
pylint *.py --fail-under=9.0

# 5. Type check
mypy *.py --ignore-missing-imports
```

Run all at once:
```bash
black . && pylint *.py --fail-under=9.0 && mypy *.py --ignore-missing-imports && pytest
```

CI runs the same gates on every push via `.github/workflows/tests.yml` and `lint.yml`.

---

## Project Structure

```
ai-knowledge-filler/
├── cli.py                  # Entry point, orchestration
├── llm_providers.py        # Provider abstractions and implementations
├── validate_yaml.py        # YAML frontmatter validator
├── exceptions.py           # Typed exception hierarchy
├── logger.py               # Logging factory (human + JSON)
├── akf/
│   ├── __init__.py         # Package namespace
│   └── system_prompt.md    # Bundled LLM instruction set (asset)
├── tests/
│   ├── test_cli.py
│   ├── test_llm_providers.py
│   ├── test_validate_yaml.py
│   └── test_exceptions.py
├── docs/
│   ├── user-guide.md
│   ├── cli-reference.md
│   └── examples/
├── .github/workflows/
│   ├── tests.yml
│   ├── lint.yml
│   └── release.yml
├── pyproject.toml
├── ARCHITECTURE.md
└── CONTRIBUTING.md         # this file
```

For a deeper module-by-module breakdown, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Adding a New LLM Provider

1. **Subclass `LLMProvider`** in `llm_providers.py`:

```python
class MyProvider(LLMProvider):
    name = "myprovider"
    display_name = "My Provider"
    model_name = "my-model-v1"

    def is_available(self) -> bool:
        return bool(os.getenv("MYPROVIDER_API_KEY")) and _has_package("myprovider_sdk")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        import myprovider_sdk
        client = myprovider_sdk.Client(api_key=os.getenv("MYPROVIDER_API_KEY"))
        response = client.complete(prompt=prompt, system=system_prompt)
        return response.text
```

2. **Register** in `PROVIDERS` dict and add to `FALLBACK_ORDER` if appropriate:

```python
PROVIDERS["myprovider"] = MyProvider
FALLBACK_ORDER.append("myprovider")  # position matters
```

3. **Add to CLI** — `argparse` choices and `cmd_models()` env var hint in `cli.py`.

4. **Add to `pyproject.toml`** optional dependencies:

```toml
[project.optional-dependencies]
all-providers = [
    ...
    "myprovider-sdk>=1.0.0",
]
```

5. **Write tests** in `tests/test_llm_providers.py` — mock the SDK, test `is_available()`, `generate()`, error handling, and retry behaviour.

---

## Adding a New Domain

Edit `Domain_Taxonomy.md` — add a `####` heading:

```markdown
#### my-new-domain
Brief description of what files belong here.
```

`validate_yaml.py` picks it up at runtime via regex — no code change required. Run `akf validate` after to confirm the domain is recognised.

---

## Writing Tests

Tests live in `tests/`. Use `pytest` with mocking for external calls.

**Test a provider (mock API call):**
```python
from unittest.mock import patch, MagicMock
from llm_providers import GroqProvider

def test_groq_generate(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value.choices[0].message.content = "# Output"
    with patch("llm_providers.Groq", return_value=mock_client):
        provider = GroqProvider()
        result = provider.generate("prompt", "system")
    assert result == "# Output"
```

**Test validation:**
```python
from validate_yaml import validate_file

def test_valid_file(tmp_path):
    f = tmp_path / "test.md"
    f.write_text("---\ntitle: Test\ntype: concept\ndomain: ai-system\n"
                 "level: intermediate\nstatus: active\ntags: [a,b,c]\n"
                 "created: 2026-01-01\nupdated: 2026-01-01\n---\n## Content\n")
    errors, warnings = validate_file(str(f))
    assert errors == []
```

**Coverage requirement:** do not decrease existing coverage. Check with:
```bash
pytest --cov=. --cov-report=term-missing --cov-fail-under=95
```

---

## Fixing a Bug

1. Reproduce with a failing test first
2. Fix the code
3. Confirm the test passes and no regressions introduced
4. Run full quality gate suite

**Known issues** are documented in [ARCHITECTURE.md — Known Issues](ARCHITECTURE.md#known-issues). If you fix one, remove it from that section in the same PR.

---

## Pull Request Process

1. Fork the repo and create a branch: `git checkout -b fix/my-fix` or `git checkout -b feat/my-feature`
2. Make changes with tests
3. Run the full quality gate suite locally
4. Push and open a PR using the template (`.github/pull_request_template.md`)
5. CI will run tests and lint automatically
6. One approval required before merge

**Branch naming:**
- `feat/short-description` — new feature
- `fix/short-description` — bug fix
- `docs/short-description` — documentation only
- `refactor/short-description` — no behaviour change
- `chore/short-description` — tooling, deps, CI

---

## Commit Style

```
type: short description (≤72 chars)

Optional longer explanation.
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

Examples:
```
feat: add XAI Grok provider with retry support
fix: ProviderUnavailableError signature — add reason parameter
docs: add ARCHITECTURE.md module map
test: add validate_yaml edge cases for empty frontmatter
```

---

## Release Process (maintainers)

1. Bump `version` in `pyproject.toml`
2. Commit: `chore: bump version to X.Y.Z`
3. Tag: `git tag vX.Y.Z && git push origin main --tags`
4. GitHub Actions `release.yml` builds and publishes to PyPI automatically

---

## Questions

Open a GitHub Issue with the `question` label.
