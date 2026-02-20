## Summary

<!-- One sentence: what does this PR do and why? -->

## Type

- [ ] feat — new feature
- [ ] fix — bug fix
- [ ] docs — documentation only
- [ ] test — tests only, no behaviour change
- [ ] refactor — no behaviour change
- [ ] chore — tooling, deps, CI

## Changes

<!-- Bullet list of what changed. Be specific. -->

-
-

## Quality Gates

Run locally before submitting:

```bash
black . && pylint *.py --fail-under=9.0 && mypy *.py --ignore-missing-imports && pytest
```

- [ ] All tests pass (`pytest --tb=short`)
- [ ] Coverage not decreased (`pytest --cov=. --cov-fail-under=95`)
- [ ] Black format check passes
- [ ] Pylint ≥ 9.0
- [ ] Mypy clean

## Testing

<!-- How was this tested? New tests added? Edge cases covered? -->

## Known Issues / Known Unknowns

<!-- Anything deferred, or risks introduced? If none, write "None". -->

## Related

<!-- Issue numbers, related PRs, or docs updated -->

Closes #
