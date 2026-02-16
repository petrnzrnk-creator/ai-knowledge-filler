#!/usr/bin/env python3
"""
AKF CLI — AI Knowledge Filler (Gemini 3 Flash Edition)
"""

import sys
import os
import re
import argparse
from datetime import datetime
from pathlib import Path

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
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        err("google-genai not installed. Run: pip install google-genai")
        sys.exit(1)

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        err("GOOGLE_API_KEY is not set.")
        sys.exit(1)

    system_prompt = load_system_prompt()
    info(f'Sending to Gemini 3 Flash: "{args.prompt}"')

    try:
        # Использование нового клиента Client (v1 SDK)
        client = genai.Client(api_key=api_key)

        # Модель gemini-3-flash-preview — самая мощная для кода и знаний в 2026 году
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=args.prompt,
            config=types.GenerateContentConfig(system_instruction=system_prompt, temperature=0.7),
        )
        content = response.text
    except Exception as e:
        err(f"Gemini API error: {e}")
        sys.exit(1)

    out_dir = Path(args.output) if args.output else OUTPUT_DIR
    filename = extract_filename(content, args.prompt)
    saved_path = save_file(content, filename, out_dir)

    ok(f"Saved to: {saved_path}")

    # Авто-валидация
    errors, _ = validate_file(str(saved_path))
    if not errors:
        ok("Validation passed!")
    else:
        warn(f"Validation found {len(errors)} issues.")


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(prog="akf")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate knowledge file")
    gen.add_argument("prompt")
    gen.add_argument("--output", "-o", help="Custom output path")

    val = sub.add_parser("validate", help="Check Markdown YAML")
    val.add_argument("--file", "-f")

    args = parser.parse_args()
    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "validate":
        cmd_validate(args)
    return 0


if __name__ == "__main__":
    main()
