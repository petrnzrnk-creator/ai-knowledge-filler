#!/usr/bin/env python3
"""
AKF CLI — AI Knowledge Filler (Multi-LLM Edition)
"""

import sys
import os
import re
import argparse
from datetime import datetime
from pathlib import Path
from llm_providers import get_provider, list_providers, PROVIDERS

# ─── CONFIGURATION ────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.absolute()
VAULT_PATH = Path("/storage/emulated/0/Download/WorkingprogressAKF_Vault")
OUTPUT_DIR = VAULT_PATH / "04-DELIVERABLES" / "Code"
SYSTEM_PROMPT_PATH = BASE_DIR / "Core_System" / "System_Prompt_AI_Knowledge_Filler.md"

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


def validate_file(filepath: str) -> tuple[list[str], list[str]]:
    """Валидация YAML фронтматтера."""
    errors, warnings = [], []
    try:
        import yaml
    except ImportError:
        return ["pyyaml not installed."], []

    if not os.path.exists(filepath):
        return [f"File not found: {filepath}"], []

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        return ["No YAML frontmatter found"], []

    parts = content.split("---")
    if len(parts) < 3:
        return ["Invalid YAML structure"], []

    try:
        metadata = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        return [f"YAML error: {e}"], []

    required = ["title", "type", "level", "status", "created", "updated"]
    for field in required:
        if field not in metadata:
            errors.append(f"Missing field: {field}")

    return errors, warnings


def cmd_validate(args: argparse.Namespace) -> None:
    import glob

    files = [args.file] if args.file else glob.glob("**/*.md", recursive=True)
    files = [f for f in files if not any(x in f for x in [".github", "README.md"])]

    info(f"Checking {len(files)} files...")
    for filepath in sorted(files):
        errors, _ = validate_file(filepath)
        if errors:
            print(f"{RED}❌ {filepath}{NC}")
        else:
            print(f"{GREEN}✅ {filepath}{NC}")


# ─── GENERATE ─────────────────────────────────────────────────────────────────


def load_system_prompt() -> str:
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
    """Generate knowledge file using selected LLM provider."""
    # Get provider
    try:
        provider = get_provider(args.model)
    except ValueError as e:
        err(str(e))
        sys.exit(1)

    system_prompt = load_system_prompt()
    info(f'Generating via {provider.display_name}...')

    # Generate content
    try:
        content = provider.generate(args.prompt, system_prompt)
    except Exception as e:
        err(f"Generation error: {e}")
        sys.exit(1)

    # Save file
    out_dir = Path(args.output) if args.output else OUTPUT_DIR
    filename = extract_filename(content, args.prompt)
    saved_path = save_file(content, filename, out_dir)

    ok(f"Saved to: {saved_path}")

    # Auto-validate
    errors, _ = validate_file(str(saved_path))
    if not errors:
        ok("Validation passed!")
    else:
        warn(f"Validation found {len(errors)} issues.")


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
    val.add_argument("--file", "-f")
    
    # Models command
    models = sub.add_parser("models", help="List available LLM providers")

    args = parser.parse_args()
    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "models":
        cmd_models(args)
    return 0


if __name__ == "__main__":
    main()
