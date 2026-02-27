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

# 2. Coverage — must not decrease below 94%
pytest --cov=. --cov-report=term-missing --cov-fail-under=94

# 3. Format check
black --check .

# 4. Lint — score ≥ 9.0
pylint cli.py llm_providers.py exceptions.py logger.py akf/ --fail-under=9.0

# 5. Type check
mypy cli.py llm_providers.py exceptions.py logger.py akf/ --ignore-missing-imports
```

Run all at once:
```bash
black . && pylint cli.py llm_providers.py exceptions.py logger.py akf/ --fail-under=9.0 && \
mypy cli.py llm_providers.py exceptions.py logger.py akf/ --ignore-missing-imports && pytest
```

CI runs the same gates on every push via `.github/workflows/tests.yml` and `lint.yml`.

---

## Project Structure

```
ai-knowledge-filler/
├── cli.py                  # Entry point, orchestration
├── llm_providers.py        # Provider abstractions and implementations
├── exceptions.py           # Typed exception hierarchy
├── logger.py               # Logging factory (human + JSON)
├── akf/
│   ├── __init__.py         # Package namespace
│   ├── pipeline.py         # Pipeline class — generate(), validate(), batch_generate()
│   ├── validator.py        # Validation Engine — binary VALID/INVALID, E001–E007
│   ├── validation_error.py # ValidationError dataclass + error constructors
│   ├── error_normalizer.py # Translates ValidationErrors → LLM retry instructions
│   ├── retry_controller.py # run_retry_loop() — convergence protection, max 3 attempts
│   ├── commit_gate.py      # Atomic write — only VALID files reach disk
│   ├── telemetry.py        # TelemetryWriter, append-only JSONL event stream
│   ├── config.py           # get_config() — loads akf.yaml or defaults
│   ├── server.py           # FastAPI REST API — /v1/generate, /v1/validate, /v1/batch
│   ├── system_prompt.md    # Bundled LLM instruction set (asset)
│   └── defaults/
│       └── akf.yaml        # Default taxonomy and enum configuration
├── Scripts/
│   ├── validate_yaml.py    # Standalone YAML frontmatter validator (CLI utility)
│   └── analyze_telemetry.py # Telemetry analysis — retry rates, ontology friction
├── tests/
│   ├── unit/               # Unit tests per module
│   ├── integration/        # End-to-end pipeline tests
│   ├── test_cli.py
│   ├── test_llm_providers.py
│   ├── test_validator.py
│   ├── test_validation_error.py
│   ├── test_error_normalizer.py
│   ├── test_retry_controller.py
│   ├── test_commit_gate.py
│   ├── test_telemetry.py
│   ├── test_config.py
│   ├── test_exceptions.py
│   └── test_logger.py
├── docs/
│   ├── user-guide.md
│   ├── cli-reference.md
│   └── examples/
├── .github/workflows/
│   ├── ci.yml
│   ├── tests.yml
│   ├── lint.yml
│   ├── validate.yml
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

Edit `akf/defaults/akf.yaml` — add the domain to the `enums.domain` list:

```yaml
enums:
  domain:
    - existing-domain
    - my-new-domain      # add here
```

If you also maintain `Domain_Taxonomy.md` in a vault, add a `####` heading there for documentation purposes. The validator reads from `akf.yaml` at runtime — no code change required. Run `akf validate` after to confirm the domain is recognised.

---

## Adding a New YAML Type or Status

1. Update `akf/defaults/akf.yaml` — add to the appropriate enum list
2. Update `Metadata_Template_Standard.md` to document the new value
3. If the change affects validation logic, update `akf/validator.py`

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

**Test validation (via akf.validator):**
```python
from akf.validator import Validator
from akf.config import get_config

def test_valid_file(tmp_path):
    f = tmp_path / "test.md"
    f.write_text("---\ntitle: Test\ntype: concept\ndomain: ai-system\n"
                 "level: intermediate\nstatus: active\ntags: [a,b,c]\n"
                 "created: 2026-01-01\nupdated: 2026-01-01\n---\n## Content\n")
    config = get_config()
    validator = Validator(config)
    result = validator.validate(f.read_text())
    assert result.is_valid
    assert result.errors == []
```

**Coverage requirement:** do not decrease existing coverage. Check with:
```bash
pytest --cov=. --cov-report=term-missing --cov-fail-under=94
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
docs: update ARCHITECTURE.md module map for Phase 2.5
test: add validator edge cases for E006 taxonomy violation
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
