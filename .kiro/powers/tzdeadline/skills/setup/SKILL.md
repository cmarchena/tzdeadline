# TZ Deadline setup

## When to use
Building or changing the timezone deadline converter.

## Conventions
- Follow `.kiro/steering/python-style.md`
- Pure conversion in `tzdeadline/core/converter.py` — no network, no print
- CLI printing stays in the CLI module
- Property tests live under `tests/` and use Hypothesis
- Invalid zones or times must raise clear errors

## Quick checks
1. Convert `2026-10-05 23:59` from `America/Los_Angeles` to `Europe/Madrid`
2. Run `python -m pytest -q`