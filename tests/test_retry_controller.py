"""
Tests for AKF Phase 2.1 — Retry Controller (S3)
ADR-001: Validation Layer Architecture
"""

import pytest
from akf.retry_controller import run_retry_loop, RetryResult, MAX_ATTEMPTS
from akf.validation_error import (
    ValidationError, ErrorCode, Severity,
    missing_field, invalid_enum, invalid_date_format,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_valid_doc(content: str = "valid") -> str:
    return f"---\ntitle: Test\n---\n{content}"


def always_valid(_doc: str) -> list[ValidationError]:
    """Validator that always returns no errors."""
    return []


def always_invalid(errors: list[ValidationError]):
    """Returns a validator that always returns the given errors."""
    def _validate(_doc: str) -> list[ValidationError]:
        return errors
    return _validate


def fixed_generate(new_doc: str):
    """Generator that always returns the same fixed document."""
    def _generate(_doc: str, _prompt: str) -> str:
        return new_doc
    return _generate


def incrementing_generate():
    """Generator that returns a unique document each call."""
    counter = [0]
    def _generate(_doc: str, _prompt: str) -> str:
        counter[0] += 1
        return f"---\ntitle: Attempt {counter[0]}\n---\ncontent"
    return _generate


# ---------------------------------------------------------------------------
# Success paths
# ---------------------------------------------------------------------------

class TestRetrySuccess:

    def test_no_errors_returns_success_zero_attempts(self):
        doc = make_valid_doc()
        result = run_retry_loop(
            document=doc,
            errors=[],
            generate_fn=fixed_generate(make_valid_doc("new")),
            validate_fn=always_valid,
        )
        assert result.success is True
        assert result.attempts == 0

    def test_first_retry_fixes_error(self):
        initial_errors = [missing_field("title")]
        call_count = [0]

        def validate(doc: str) -> list[ValidationError]:
            call_count[0] += 1
            return []  # fixed after first retry

        result = run_retry_loop(
            document="bad doc",
            errors=initial_errors,
            generate_fn=incrementing_generate(),
            validate_fn=validate,
        )
        assert result.success is True
        assert result.attempts == 1

    def test_second_retry_fixes_error(self):
        initial_errors = [missing_field("title")]
        call_count = [0]

        def validate(doc: str) -> list[ValidationError]:
            call_count[0] += 1
            if call_count[0] < 2:
                return [missing_field("domain")]  # still failing
            return []  # fixed on second attempt

        result = run_retry_loop(
            document="bad doc",
            errors=initial_errors,
            generate_fn=incrementing_generate(),
            validate_fn=validate,
        )
        assert result.success is True
        assert result.attempts == 2

    def test_warnings_do_not_block_success(self):
        warning = ValidationError(
            code=ErrorCode.SCHEMA_VIOLATION,
            field="version",
            expected="vX.Y",
            received="1.0",
            severity=Severity.WARNING,
        )

        def validate(_doc: str) -> list[ValidationError]:
            return [warning]

        result = run_retry_loop(
            document="bad doc",
            errors=[missing_field("title")],
            generate_fn=incrementing_generate(),
            validate_fn=validate,
        )
        assert result.success is True
        assert len(result.errors) == 1  # warning preserved


# ---------------------------------------------------------------------------
# Abort paths
# ---------------------------------------------------------------------------

class TestRetryAbort:

    def test_max_attempts_exhausted(self):
        """Max attempts reached when errors change each retry (no convergence)."""
        # Errors rotate through different fields so convergence never triggers
        fields = ["title", "domain", "level"]
        call_count = [0]

        def validate(_doc: str) -> list[ValidationError]:
            idx = call_count[0] % len(fields)
            call_count[0] += 1
            return [missing_field(fields[idx])]

        result = run_retry_loop(
            document="bad doc",
            errors=[missing_field("type")],  # initial error, different field
            generate_fn=incrementing_generate(),
            validate_fn=validate,
        )
        assert result.success is False
        assert result.attempts == MAX_ATTEMPTS
        assert "max_attempts_reached" in result.abort_reason

    def test_identical_output_aborts(self):
        """Identical output detected when initial and retry errors differ (no early convergence)."""
        # Use different initial errors vs validate errors so convergence
        # doesn't trigger on attempt 1, allowing hash check to catch attempt 2
        same_doc = make_valid_doc("same content every time")
        initial_errors = [missing_field("type")]   # different field
        retry_errors = [missing_field("domain")]   # different field → no convergence

        def validate(_doc: str) -> list[ValidationError]:
            return retry_errors

        result = run_retry_loop(
            document="bad doc",
            errors=initial_errors,
            generate_fn=fixed_generate(same_doc),
            validate_fn=validate,
        )
        assert result.success is False
        assert "identical_output" in result.abort_reason

    def test_same_ecode_same_field_twice_aborts(self):
        """ADR-001 hard rule: same (field, E-code) pair failing twice → abort."""
        errors = [missing_field("domain")]
        call_count = [0]

        def validate(_doc: str) -> list[ValidationError]:
            call_count[0] += 1
            return [missing_field("domain")]  # same field, same E-code every time

        result = run_retry_loop(
            document="bad doc",
            errors=errors,
            generate_fn=incrementing_generate(),
            validate_fn=validate,
        )
        assert result.success is False
        assert "convergence_failure" in result.abort_reason
        assert "domain" in result.abort_reason


# ---------------------------------------------------------------------------
# Attempt counting
# ---------------------------------------------------------------------------

class TestAttemptCounting:

    def test_attempt_count_matches_llm_calls(self):
        call_count = [0]

        def generate(_doc: str, _prompt: str) -> str:
            call_count[0] += 1
            return f"doc_{call_count[0]}"

        errors = [missing_field("title")]

        def validate(_doc: str) -> list[ValidationError]:
            return []  # succeeds immediately

        result = run_retry_loop(
            document="bad doc",
            errors=errors,
            generate_fn=generate,
            validate_fn=validate,
        )
        assert result.attempts == call_count[0] == 1

    def test_custom_max_attempts_respected(self):
        """Custom max_attempts cap is respected when errors rotate (no convergence)."""
        fields = ["title", "domain"]
        call_count = [0]

        def validate(_doc: str) -> list[ValidationError]:
            idx = call_count[0] % len(fields)
            call_count[0] += 1
            return [missing_field(fields[idx])]

        result = run_retry_loop(
            document="bad doc",
            errors=[missing_field("type")],
            generate_fn=incrementing_generate(),
            validate_fn=validate,
            max_attempts=2,
        )
        assert result.attempts == 2
        assert "max_attempts_reached" in result.abort_reason


# ---------------------------------------------------------------------------
# RetryResult contract
# ---------------------------------------------------------------------------

class TestRetryResultContract:

    def test_success_result_has_no_abort_reason(self):
        result = run_retry_loop(
            document="doc",
            errors=[],
            generate_fn=fixed_generate("new"),
            validate_fn=always_valid,
        )
        assert result.abort_reason is None

    def test_failure_result_has_abort_reason(self):
        errors = [missing_field("title")]
        result = run_retry_loop(
            document="bad doc",
            errors=errors,
            generate_fn=incrementing_generate(),
            validate_fn=always_invalid(errors),
        )
        assert result.abort_reason is not None
        assert isinstance(result.abort_reason, str)

    def test_str_representation_success(self):
        result = run_retry_loop(
            document="doc",
            errors=[],
            generate_fn=fixed_generate("new"),
            validate_fn=always_valid,
        )
        assert "success=True" in str(result)

    def test_str_representation_failure(self):
        errors = [missing_field("title")]
        result = run_retry_loop(
            document="bad doc",
            errors=errors,
            generate_fn=incrementing_generate(),
            validate_fn=always_invalid(errors),
        )
        assert "success=False" in str(result)
