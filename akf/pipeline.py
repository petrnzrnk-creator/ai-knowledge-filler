from __future__ import annotations
import re, os, time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

@dataclass
class GenerateResult:
    success: bool
    content: str
    path: object = None
    attempts: int = 0
    errors: list = field(default_factory=list)
    generation_id: str = ""
    duration_ms: int = 0
    def __repr__(self):
        s = "VALID" if self.success else "INVALID"
        return f"GenerateResult({s}, attempts={self.attempts}, errors={len(self.errors)})"

@dataclass
class ValidateResult:
    valid: bool
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    filepath: object = None
    def __repr__(self):
        s = "VALID" if self.valid else "INVALID"
        return f"ValidateResult({s}, errors={len(self.errors)}, warnings={len(self.warnings)})"

class Pipeline:
    def __init__(self, output=None, model="auto", telemetry_path=None, verbose=True):
        self.model = model
        self.verbose = verbose
        self.output_dir = Path(output).expanduser() if output else Path(os.getenv("AKF_OUTPUT_DIR", "."))
        self.telemetry_path = Path(telemetry_path).expanduser() if telemetry_path else Path(os.getenv("AKF_TELEMETRY_PATH", "telemetry/events.jsonl"))
        self._system_prompt = None

    def _log(self, msg):
        if self.verbose:
            print(f"->  {msg}")

    def _load_system_prompt(self):
        if self._system_prompt:
            return self._system_prompt
        try:
            import akf as _pkg
            p = Path(_pkg.__file__).parent / "system_prompt.md"
            if p.exists():
                self._system_prompt = p.read_text(encoding="utf-8")
                return self._system_prompt
        except Exception:
            pass
        local = Path(__file__).parent / "system_prompt.md"
        if local.exists():
            self._system_prompt = local.read_text(encoding="utf-8")
            return self._system_prompt
        raise FileNotFoundError("system_prompt.md not found")

    @staticmethod
    def _extract_filename(content, prompt):
        import re
        match = re.search(r'title:\s*["\'\']?(.+?)["\'\']?\s*\n', content)
        if match:
            title = match.group(1).strip().strip("\"'")
            name = re.sub(r"[\s-]+", "_", re.sub(r"[^\w\s-]", "", title))
            return f"{name}.md"
        return "_".join(re.sub(r"[^\w\s]", "", prompt).split()[:4]).lower() + ".md"

    def _resolve_path(self, content, prompt, out_dir):
        out_dir.mkdir(parents=True, exist_ok=True)
        fp = out_dir / self._extract_filename(content, prompt)
        if fp.exists():
            ts = datetime.now().strftime("%H%M%S")
            fp = out_dir / f"{fp.stem}_{ts}.md"
        return fp

    def generate(self, prompt, output=None, model=None):
        from llm_providers import get_provider
        from akf.telemetry import TelemetryWriter, new_generation_id
        from akf.retry_controller import run_retry_loop
        from akf.commit_gate import commit as akf_commit
        from akf.validator import validate
        from akf.validation_error import Severity
        try:
            provider = get_provider(model or self.model)
        except Exception as e:
            return GenerateResult(success=False, content="", errors=[str(e)])
        system_prompt = self._load_system_prompt()
        self._log(f"Generating via {provider.display_name}...")
        generation_id = new_generation_id()
        writer = TelemetryWriter(path=self.telemetry_path)
        t_start = time.monotonic()
        try:
            content = provider.generate(prompt, system_prompt)
        except Exception as e:
            return GenerateResult(success=False, content="", errors=[str(e)], generation_id=generation_id)
        out_dir = Path(output).expanduser() if output else self.output_dir
        output_path = self._resolve_path(content, prompt, out_dir)
        document_id = output_path.stem
        try:
            initial_errors = validate(content)
        except Exception:
            initial_errors = []
        blocking = [e for e in initial_errors if e.severity == Severity.ERROR]
        rejected_candidates = []
        total_attempts = 1
        if blocking:
            def generate_fn(doc, retry_prompt):
                return provider.generate(retry_prompt, system_prompt)
            def validate_fn(doc):
                try:
                    return validate(doc)
                except Exception:
                    return []
            retry_result = run_retry_loop(
                document=content, errors=blocking,
                generate_fn=generate_fn, validate_fn=validate_fn,
                generation_id=generation_id, document_id=document_id,
                schema_version="1.0.0", model=provider.model_name,
                temperature=0, top_p=1, writer=writer,
            )
            content = retry_result.document
            total_attempts = retry_result.attempts
            for e in retry_result.errors:
                if e.field == "domain" and e.received:
                    rejected_candidates.append(str(e.received))
        total_duration_ms = int((time.monotonic() - t_start) * 1000)
        try:
            final_errors = validate(content)
        except Exception:
            final_errors = []
        commit_result = akf_commit(
            document=content, output_path=output_path, errors=final_errors,
            generation_id=generation_id, document_id=document_id,
            schema_version="1.0.0", total_attempts=total_attempts,
            rejected_candidates=rejected_candidates, model=provider.model_name,
            temperature=0, total_duration_ms=total_duration_ms, writer=writer,
        )
        if commit_result.committed:
            self._log(f"Saved: {commit_result.path}")
            return GenerateResult(success=True, content=content, path=commit_result.path,
                attempts=total_attempts, generation_id=generation_id, duration_ms=total_duration_ms)
        else:
            output_path.write_text(content, encoding="utf-8")
            return GenerateResult(success=False, content=content, path=output_path,
                attempts=total_attempts, errors=commit_result.blocking_errors,
                generation_id=generation_id, duration_ms=total_duration_ms)

    def validate(self, filepath, strict=False):
        from akf.validator import validate as _validate
        from akf.validation_error import Severity
        fp = Path(filepath).expanduser()
        if not fp.exists():
            return ValidateResult(valid=False, errors=[f"File not found: {fp}"], filepath=fp)
        all_errors = _validate(fp.read_text(encoding="utf-8"))
        if strict:
            errors = [str(e) for e in all_errors]
            warnings = []
        else:
            errors = [str(e) for e in all_errors if e.severity == Severity.ERROR]
            warnings = [str(e) for e in all_errors if e.severity == Severity.WARNING]
        return ValidateResult(valid=len(errors) == 0, errors=errors, warnings=warnings, filepath=fp)

    def batch_generate(self, prompts, output=None, model=None):
        results = []
        for i, prompt in enumerate(prompts, 1):
            self._log(f"[{i}/{len(prompts)}] {prompt[:60]}...")
            results.append(self.generate(prompt, output=output, model=model))
        return results
