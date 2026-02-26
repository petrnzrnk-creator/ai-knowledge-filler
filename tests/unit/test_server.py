"""Unit tests for AKF REST API (Stage 3)."""

import textwrap
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from akf.server import app
from akf.pipeline import GenerateResult, ValidateResult
from pathlib import Path

client = TestClient(app)

VALID_CONTENT = textwrap.dedent("""\
    ---
    schema_version: "1.0.0"
    title: "Test Guide"
    type: guide
    domain: devops
    level: intermediate
    status: active
    tags: [docker, guide, test]
    related:
      - "[[Docker Basics]]"
    created: 2026-02-26
    updated: 2026-02-26
    ---

    ## Purpose

    Test content.

    ## Conclusion

    Done.
""")


class TestHealth:
    def test_health_ok(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_health_version(self):
        r = client.get("/health")
        assert "version" in r.json()


class TestModels:
    def test_models_returns_providers(self):
        with patch("llm_providers.list_providers", return_value={"claude": False, "groq": False}):
            r = client.get("/v1/models")
        assert r.status_code == 200
        assert "providers" in r.json()


class TestGenerate:
    def _mock_result(self, success=True):
        return GenerateResult(
            success=success,
            content=VALID_CONTENT,
            path=Path("/tmp/test.md"),
            attempts=1,
            errors=[],
            generation_id="test-uuid",
            duration_ms=100,
        )

    def test_generate_success(self):
        with patch("akf.server.get_pipeline") as mock_get:
            mock_pipeline = MagicMock()
            mock_pipeline.generate.return_value = self._mock_result(True)
            mock_get.return_value = mock_pipeline
            r = client.post("/v1/generate", json={"prompt": "Create a guide"})
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["attempts"] == 1
        assert data["generation_id"] == "test-uuid"

    def test_generate_failure(self):
        with patch("akf.server.get_pipeline") as mock_get:
            mock_pipeline = MagicMock()
            mock_pipeline.generate.return_value = self._mock_result(False)
            mock_get.return_value = mock_pipeline
            r = client.post("/v1/generate", json={"prompt": "Create a guide"})
        assert r.status_code == 200
        assert r.json()["success"] is False

    def test_generate_with_model(self):
        with patch("akf.server.get_pipeline") as mock_get:
            mock_pipeline = MagicMock()
            mock_pipeline.generate.return_value = self._mock_result()
            mock_get.return_value = mock_pipeline
            r = client.post("/v1/generate", json={"prompt": "Test", "model": "groq"})
        assert r.status_code == 200

    def test_generate_missing_prompt(self):
        r = client.post("/v1/generate", json={})
        assert r.status_code == 422

    def test_generate_path_in_response(self):
        with patch("akf.server.get_pipeline") as mock_get:
            mock_pipeline = MagicMock()
            mock_pipeline.generate.return_value = self._mock_result()
            mock_get.return_value = mock_pipeline
            r = client.post("/v1/generate", json={"prompt": "Test"})
        assert r.json()["path"] is not None


class TestValidate:
    def test_validate_valid_content(self):
        r = client.post("/v1/validate", json={"content": VALID_CONTENT})
        assert r.status_code == 200
        data = r.json()
        assert "valid" in data
        assert "errors" in data
        assert "warnings" in data

    def test_validate_invalid_content(self):
        bad = "---\ntitle: x\ntype: bad\n---\n## Content"
        r = client.post("/v1/validate", json={"content": bad})
        assert r.status_code == 200
        assert r.json()["valid"] is False

    def test_validate_strict_mode(self):
        r = client.post("/v1/validate", json={"content": VALID_CONTENT, "strict": True})
        assert r.status_code == 200

    def test_validate_missing_content(self):
        r = client.post("/v1/validate", json={})
        assert r.status_code == 422


class TestBatch:
    def _mock_result(self, i=0):
        return GenerateResult(
            success=True,
            content=VALID_CONTENT,
            path=Path(f"/tmp/test_{i}.md"),
            attempts=1,
            errors=[],
            generation_id=f"uuid-{i}",
            duration_ms=100,
        )

    def test_batch_success(self):
        with patch("akf.server.get_pipeline") as mock_get:
            mock_pipeline = MagicMock()
            mock_pipeline.batch_generate.return_value = [
                self._mock_result(0), self._mock_result(1)
            ]
            mock_get.return_value = mock_pipeline
            r = client.post("/v1/batch", json={"prompts": ["Guide 1", "Guide 2"]})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 2
        assert data["success"] == 2
        assert data["failed"] == 0
        assert len(data["results"]) == 2

    def test_batch_empty(self):
        with patch("akf.server.get_pipeline") as mock_get:
            mock_pipeline = MagicMock()
            mock_pipeline.batch_generate.return_value = []
            mock_get.return_value = mock_pipeline
            r = client.post("/v1/batch", json={"prompts": []})
        assert r.status_code == 200
        assert r.json()["total"] == 0

    def test_batch_missing_prompts(self):
        r = client.post("/v1/batch", json={})
        assert r.status_code == 422
