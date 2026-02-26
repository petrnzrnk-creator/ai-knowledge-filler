from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from pathlib import Path
from akf.pipeline import Pipeline, GenerateResult, ValidateResult

app = FastAPI(title="AKF API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_pipeline = None

def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = Pipeline(
            output=os.getenv("AKF_OUTPUT_DIR", "./output"),
            verbose=False,
        )
    return _pipeline


class GenerateRequest(BaseModel):
    prompt: str
    output: Optional[str] = None
    model: Optional[str] = None

class GenerateResponse(BaseModel):
    success: bool
    path: Optional[str]
    content: Optional[str]
    attempts: int
    errors: list[str]
    generation_id: str
    duration_ms: int

class ValidateRequest(BaseModel):
    content: str
    strict: bool = False

class ValidateResponse(BaseModel):
    valid: bool
    errors: list[str]
    warnings: list[str]

class BatchRequest(BaseModel):
    prompts: list[str]
    output: Optional[str] = None
    model: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/v1/models")
def models():
    from llm_providers import list_providers
    return {"providers": list_providers()}


@app.post("/v1/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    result = get_pipeline().generate(
        prompt=req.prompt,
        output=req.output,
        model=req.model,
    )
    return GenerateResponse(
        success=result.success,
        path=str(result.path) if result.path else None,
        content=result.content,
        attempts=result.attempts,
        errors=[str(e) for e in result.errors],
        generation_id=result.generation_id,
        duration_ms=result.duration_ms,
    )


@app.post("/v1/validate", response_model=ValidateResponse)
def validate(req: ValidateRequest):
    from akf.validator import validate as _validate
    from akf.validation_error import Severity
    all_errors = _validate(req.content)
    if req.strict:
        errors = [str(e) for e in all_errors]
        warnings = []
    else:
        errors = [str(e) for e in all_errors if e.severity == Severity.ERROR]
        warnings = [str(e) for e in all_errors if e.severity == Severity.WARNING]
    return ValidateResponse(valid=len(errors) == 0, errors=errors, warnings=warnings)


@app.post("/v1/batch")
def batch(req: BatchRequest):
    results = get_pipeline().batch_generate(
        prompts=req.prompts,
        output=req.output,
        model=req.model,
    )
    return {
        "total": len(results),
        "success": sum(1 for r in results if r.success),
        "failed": sum(1 for r in results if not r.success),
        "results": [
            {
                "success": r.success,
                "path": str(r.path) if r.path else None,
                "attempts": r.attempts,
                "errors": [str(e) for e in r.errors],
                "generation_id": r.generation_id,
                "duration_ms": r.duration_ms,
            }
            for r in results
        ],
    }
