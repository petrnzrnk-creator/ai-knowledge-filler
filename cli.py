#!/usr/bin/env python3
"""
AKF CLI — AI Knowledge Filler (Multi-LLM Edition)
"""

import sys
import os
import re
import argparse
import time
from datetime import datetime
from pathlib import Path
from llm_providers import get_provider, list_providers, PROVIDERS

# ─── CONFIGURATION ────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.absolute()
OUTPUT_DIR = Path(os.getenv("AKF_OUTPUT_DIR", "."))
SYSTEM_PROMPT_PATH = Path(__file__).parent / "system_prompt.md"

# Telemetry writer path (repo, not vault — ADR-001 Decision 9)
TELEMETRY_PATH = Path(os.getenv("AKF_TELEMETRY_PATH", "telemetry/events.jsonl"))


CLI_EXCLUDE_PATTERNS = [
    ".github",
    "README.md",
    "08-TEMPLATES",  # Obsidian Templater files — not knowledge documents
]

# ─── COLORS ───────────────────────────────────────────────────────────────────

GREEN = "\033[0;32m"
BLUE = "\033[0;34m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
NC = "\033[0m"


def ok(msg: str) -> None:
    print(f"{GREEN}✅ {msg}{NC}")


def info(msg: str) -> None:
    print(f"{BLUE}→  {msg}{NC}")


def warn(msg: str) -> None:
    print(f"{YELLOW}⚠  {msg}{NC}")


def err(msg: str) -> None:
    print(f"{RED}❌ {msg}{NC}")


# ─── VALIDATE ─────────────────────────────────────────────────────────────────

from akf.validator import validate as _akf_validate
from akf.validation_error import Severity


def _validate_file_impl(filepath: str, strict: bool = False) -> tuple[list[str], list[str]]:
    """Adapter: wraps akf.validator.validate() to match cli expected signature."""
    with open(filepath, encoding="utf-8") as _f:
        content = _f.read()
    all_errors = _akf_validate(content)
    if strict:
        error_msgs = [str(e) for e in all_errors]
        warning_msgs: list[str] = []
    else:
        error_msgs = [str(e) for e in all_errors if e.severity == Severity.ERROR]
        warning_msgs = [str(e) for e in all_errors if e.severity == Severity.WARNING]
    return error_msgs, warning_msgs


def validate_file(filepath: str, strict: bool = False) -> tuple[list[str], list[str]]:
    """Validate a Markdown file using akf.validator (full E001-E007 enforcement)."""
    return _validate_file_impl(filepath, strict=strict)


def cmd_validate(args: argparse.Namespace) -> None:
    import glob

    # Resolve file list
    if args.file:
        files = [args.file]
    elif args.path:
        base = Path(args.path)
        files = [str(p) for p in base.rglob("*.md")]
    else:
        files = glob.glob("**/*.md", recursive=True)

    files = [f for f in files if not any(x in f for x in CLI_EXCLUDE_PATTERNS)]

    strict = getattr(args, "strict", False)
    mode = " [STRICT]" if strict else ""
    info(f"Checking {len(files)} files{mode}...")

    total = valid = warned = failed = 0
    for filepath in sorted(files):
        total += 1
        errors, warnings = validate_file(filepath, strict=strict)
        rel = filepath
        if errors:
            failed += 1
            print(f"{RED}❌ {rel}{NC}")
            for e in errors:
                print(f"   {RED}{e}{NC}")
        elif warnings:
            warned += 1
            print(f"{YELLOW}⚠  {rel}{NC}")
            for w in warnings:
                print(f"   {YELLOW}{w}{NC}")
        else:
            valid += 1
            print(f"{GREEN}✅ {rel}{NC}")

    print()
    info(f"Total: {total} | OK: {valid} | Warnings: {warned} | Errors: {failed}")
    if failed > 0:
        sys.exit(1)


# ─── INIT ─────────────────────────────────────────────────────────────────────


def cmd_init(args: argparse.Namespace) -> None:
    """
    Generate akf.yaml in the target directory.

    Copies the bundled default config to the vault root (or --path).
    If akf.yaml already exists, aborts unless --force is passed.
    """
    import shutil

    target_dir = Path(args.path) if args.path else Path.cwd()
    target = target_dir / "akf.yaml"

    # Find bundled default
    try:
        import akf
        default_config = Path(akf.__file__).parent / "defaults" / "akf.yaml"
    except Exception:
        default_config = Path(__file__).parent / "akf" / "defaults" / "akf.yaml"

    if not default_config.exists():
        err(f"Bundled default config not found: {default_config}")
        sys.exit(1)

    if target.exists() and not args.force:
        warn(f"akf.yaml already exists: {target}")
        warn("Use --force to overwrite.")
        sys.exit(1)

    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(default_config, target)
    ok(f"Created: {target}")
    info("")
    info("Next steps:")
    info("  1. Edit akf.yaml — set vault_path and add your domains under taxonomy.domains")
    info("  2. Set your LLM API key:")
    info("       export ANTHROPIC_API_KEY=\'sk-ant-...\'   # Claude (recommended)")
    info("       export GOOGLE_API_KEY=\'AIza...\'         # Gemini")
    info("       export OPENAI_API_KEY=\'sk-...\'          # GPT-4")
    info("       export GROQ_API_KEY=\'gsk_...\'           # Groq (fast + free tier)")
    info("       # or run Ollama locally — no key needed")
    info("  3. Generate your first file:")
    info("       akf generate \"Create a concept about [topic] for the [domain] domain\"")
    info("")
    info("Docs: https://github.com/petrnzrnk-creator/ai-knowledge-filler")


# ─── GENERATE ─────────────────────────────────────────────────────────────────


def load_system_prompt() -> str:
    # Installed package: look in akf/ subdirectory
    try:
        import akf
        pkg_path = Path(akf.__file__).parent / "system_prompt.md"
        if pkg_path.exists():
            return pkg_path.read_text(encoding="utf-8")
    except Exception:
        pass
    # Local dev: look next to cli.py
    if not SYSTEM_PROMPT_PATH.exists():
        err(f"System prompt not found at: {SYSTEM_PROMPT_PATH}")
        sys.exit(1)
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


def extract_filename(content: str, prompt: str) -> str:
    match = re.search(r'title:\s*["\']?(.+?)["\']?\s*\n', content)
    if match:
        title = match.group(1).strip().strip("\"'")
        name = re.sub(r"[\s-]+", "_", re.sub(r"[^\w\s-]", "", title))
        return f"{name}.md"
    return "_".join(re.sub(r"[^\w\s]", "", prompt).split()[:4]).lower() + ".md"


def save_file(content: str, filename: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename
    if filepath.exists():
        ts = datetime.now().strftime("%H%M%S")
        filepath = output_dir / f"{filepath.stem}_{ts}.md"
    filepath.write_text(content, encoding="utf-8")
    return filepath


def cmd_generate(args: argparse.Namespace) -> None:
    """Generate knowledge file using selected LLM provider.

    Pipeline (Phase 2.3):
      1. Generate initial content via LLM
      2. Validate → run_retry_loop if errors
      3. commit() → atomic write
      4. Telemetry emitted by RetryController + CommitGate automatically
    """
    from akf.telemetry import TelemetryWriter, new_generation_id
    from akf.retry_controller import run_retry_loop
    from akf.commit_gate import commit as akf_commit
    from akf.validator import validate

    # Get provider
    try:
        provider = get_provider(args.model)
    except ValueError as e:
        err(str(e))
        sys.exit(1)
    except Exception as e:
        # Catch ProviderUnavailableError (and subclasses) without hard import
        if "ProviderUnavailableError" in type(e).__name__ or "unavailable" in str(e).lower():
            err("No LLM provider available.")
            info("Set one of these environment variables and retry:")
            info("  export ANTHROPIC_API_KEY='sk-ant-...'")
            info("  export GOOGLE_API_KEY='AIza...'")
            info("  export OPENAI_API_KEY='sk-...'")
            info("  export GROQ_API_KEY='gsk_...'")
            info("Or run Ollama locally (no key needed): https://ollama.com")
        else:
            err(f"Provider error: {e}")
        sys.exit(1)

    system_prompt = load_system_prompt()
    info(f'Generating via {provider.display_name}...')

    # ── Telemetry setup ───────────────────────────────────────────────────────
    generation_id = new_generation_id()
    writer = TelemetryWriter(path=TELEMETRY_PATH)
    t_start = time.monotonic()

    # ── Initial generation ────────────────────────────────────────────────────
    try:
        t0 = time.monotonic()
        content = provider.generate(args.prompt, system_prompt)
        initial_duration_ms = int((time.monotonic() - t0) * 1000)
    except Exception as e:
        err(f"Generation error: {e}")
        sys.exit(1)

    # ── Determine output path ─────────────────────────────────────────────────
    out_dir = Path(args.output) if args.output else OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = extract_filename(content, args.prompt)
    output_path = out_dir / filename
    if output_path.exists():
        ts = datetime.now().strftime("%H%M%S")
        output_path = out_dir / f"{output_path.stem}_{ts}.md"

    document_id = output_path.stem

    # ── Initial validation ────────────────────────────────────────────────────
    try:
        initial_errors = validate(content)
    except Exception:
        initial_errors = []

    blocking = [e for e in initial_errors if e.severity.value == "error"]

    # ── Retry loop (if needed) ────────────────────────────────────────────────
    rejected_candidates: list[str] = []
    total_attempts = 0

    if blocking:
        def generate_fn(doc: str, retry_prompt: str) -> str:
            return provider.generate(retry_prompt, system_prompt)

        def validate_fn(doc: str) -> list:
            try:
                return validate(doc)
            except Exception:
                return []

        retry_result = run_retry_loop(
            document=content,
            errors=blocking,
            generate_fn=generate_fn,
            validate_fn=validate_fn,
            generation_id=generation_id,
            document_id=document_id,
            schema_version="1.0.0",
            model=provider.model_name,
            temperature=0,
            top_p=1,
            writer=writer,
        )
        content = retry_result.document
        total_attempts = retry_result.attempts

        # Collect rejected domain candidates from retry errors
        for e in retry_result.errors:
            if e.field == "domain" and e.received:
                rejected_candidates.append(str(e.received))
    else:
        total_attempts = 1

    total_duration_ms = int((time.monotonic() - t_start) * 1000)

    # ── Commit ────────────────────────────────────────────────────────────────
    final_errors = []
    try:
        final_errors = validate(content)
    except Exception:
        pass

    commit_result = akf_commit(
        document=content,
        output_path=output_path,
        errors=final_errors,
        generation_id=generation_id,
        document_id=document_id,
        schema_version="1.0.0",
        total_attempts=total_attempts,
        rejected_candidates=rejected_candidates,
        model=provider.model_name,
        temperature=0,
        total_duration_ms=total_duration_ms,
        writer=writer,
    )

    # ── Output ────────────────────────────────────────────────────────────────
    if commit_result.committed:
        ok(f"Saved to: {commit_result.path}")
        ok("Validation passed!")
    else:
        # Fallback: save anyway (pre-Phase 2.3 behaviour) and warn
        saved_path = save_file(content, filename, out_dir)
        ok(f"Saved to: {saved_path}")
        warn(f"Validation found {len(commit_result.blocking_errors)} issues.")


# ─── MODELS ───────────────────────────────────────────────────────────────────


def cmd_models(args: argparse.Namespace) -> None:
    """List available LLM providers."""
    providers = list_providers()

    info("Available LLM providers:\n")
    for name, available in providers.items():
        provider = PROVIDERS[name]()
        status = f"{GREEN}✅" if available else f"{RED}❌"
        print(f"{status} {name:<10} {provider.display_name}{NC}")
        if available:
            print(f"   Model: {provider.model_name}")
        else:
            # Show what's needed
            if name == "claude":
                print(f"   {YELLOW}Set ANTHROPIC_API_KEY{NC}")
            elif name == "gemini":
                print(f"   {YELLOW}Set GOOGLE_API_KEY{NC}")
            elif name == "gpt4":
                print(f"   {YELLOW}Set OPENAI_API_KEY{NC}")
            elif name == "groq":
                print(f"   {YELLOW}Set GROQ_API_KEY{NC}")
            elif name == "grok":
                print(f"   {YELLOW}Set XAI_API_KEY{NC}")
            elif name == "ollama":
                print(f"   {YELLOW}Run Ollama server{NC}")
        print()


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(prog="akf")
    sub = parser.add_subparsers(dest="command", required=True)

    # Init command
    init = sub.add_parser("init", help="Generate akf.yaml for a new vault")
    init.add_argument("--path", "-p", help="Target directory (default: CWD)")
    init.add_argument("--force", "-f", action="store_true",
                      help="Overwrite existing akf.yaml")

    # Generate command
    gen = sub.add_parser("generate", help="Generate knowledge file")
    gen.add_argument("prompt")
    gen.add_argument("--model", "-m",
                     choices=["auto", "claude", "gemini", "gpt4", "groq", "grok", "ollama"],
                     default="auto",
                     help="LLM provider (default: auto-select)")
    gen.add_argument("--output", "-o", help="Custom output path")

    # Validate command
    val = sub.add_parser("validate", help="Check Markdown YAML")
    val.add_argument("--file", "-f", help="Validate single file")
    val.add_argument("--path", "-p", help="Validate all .md files in folder")
    val.add_argument("--strict", "-s", action="store_true",
                     help="Promote warnings to errors")

    # Models command
    models = sub.add_parser("models", help="List available LLM providers")

    args = parser.parse_args()
    if args.command == "init":
        cmd_init(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "models":
        cmd_models(args)
    return 0


if __name__ == "__main__":
    main()
