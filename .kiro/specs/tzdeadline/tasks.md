# Implementation Plan: tzdeadline

## Overview

Implement `tzdeadline` as a Python 3.11+ package with a shared core conversion library, a CLI
entry point, and an MCP server entry point. The core is split into three independent modules
(`parser`, `converter`, `formatter`), which are then wired together by `__main__` (CLI) and
`server` (MCP). Property-based tests use Hypothesis; unit/example tests use pytest.

---

## Tasks

- [x] 1. Set up project structure and packaging
  - Create the directory layout: `tzdeadline/core/`, `tests/unit/`, `tests/property/`
  - Add `pyproject.toml` (or `setup.cfg`) with package metadata, entry point
    `tzdeadline = tzdeadline.__main__:main`, and dependencies (`mcp`, `hypothesis`, `pytest`)
  - Add an empty `tzdeadline/__init__.py` and `tzdeadline/core/__init__.py`
  - Add `tests/__init__.py`, `tests/unit/__init__.py`, `tests/property/__init__.py`
  - _Requirements: 1.1, 1.2, 3.1, 4.1_

- [x] 2. Implement `tzdeadline.core.parser`
  - [x] 2.1 Create `tzdeadline/core/parser.py`
    - Define `ParseError(ValueError)`
    - Implement `parse_datetime(dt_string: str) -> datetime` using `datetime.fromisoformat()`
      with fallback to `ParseError`; return naive datetime or offset-carrying datetime per design
    - _Requirements: 3.1, 3.2_

  - [ ]* 2.2 Write property test for parser round-trip (Property 2)
    - **Property 2: Parser round-trip**
    - **Validates: Requirements 3.1**
    - File: `tests/property/test_round_trip.py`
    - Use `@settings(max_examples=100)`; annotate with
      `# Feature: tzdeadline, Property 2: Parser round-trip`

  - [ ]* 2.3 Write property test for invalid datetime strings → error (Property 4)
    - **Property 4: Invalid datetime strings always produce errors**
    - **Validates: Requirements 3.2**
    - File: `tests/property/test_error_conditions.py`
    - Strategy: `st.text()` filtered to exclude valid ISO 8601 datetime patterns

  - [ ]* 2.4 Write unit tests for parser
    - File: `tests/unit/test_parser.py`
    - Cover: each accepted format variant (`T`-sep, space-sep, with/without UTC offset),
      `ParseError` on garbage input
    - _Requirements: 3.1, 3.2_

- [x] 3. Implement `tzdeadline.core.converter`
  - [x] 3.1 Create `tzdeadline/core/converter.py`
    - Define `ConversionError(ValueError)` and `ConversionResult` frozen dataclass
    - Implement `convert(dt, source_tz, target_tz)`: load both `ZoneInfo` objects (re-raise
      `ZoneInfoNotFoundError` as `ConversionError`), strip offset if dt is aware, attach source
      zone and `astimezone` to target zone
    - _Requirements: 1.1, 1.2, 1.3_

  - [ ]* 3.2 Write property test for round-trip timezone conversion (Property 1)
    - **Property 1: Round-trip timezone conversion**
    - **Validates: Requirements 5.1**
    - File: `tests/property/test_round_trip.py`
    - Strategy: naive datetimes × pairs of valid IANA identifiers; assert UTC equivalence after A→B→A

  - [ ]* 3.3 Write property test for converted datetime in target zone (Property 6)
    - **Property 6: Converted datetime is timezone-aware in the target zone**
    - **Validates: Requirements 1.1**
    - File: `tests/property/test_round_trip.py`
    - Assert `result.converted_dt.tzinfo` corresponds to the requested target IANA zone

  - [ ]* 3.4 Write property test for invalid timezone identifiers → error (Property 3)
    - **Property 3: Invalid timezone identifiers always produce errors**
    - **Validates: Requirements 1.3**
    - File: `tests/property/test_error_conditions.py`
    - Strategy: `st.text()` filtered to exclude `zoneinfo.available_timezones()`

  - [ ]* 3.5 Write unit tests for converter
    - File: `tests/unit/test_converter.py`
    - Cover: known conversion (e.g. UTC→America/New_York), `ConversionError` on bad source,
      `ConversionError` on bad target, awareness of result
    - _Requirements: 1.1, 1.2, 1.3_

- [ ] 4. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement `tzdeadline.core.formatter`
  - [x] 5.1 Create `tzdeadline/core/formatter.py`
    - Implement `format_iso(dt: datetime) -> str` returning ISO 8601 with UTC offset
    - Implement `format_countdown(dt: datetime, now: datetime | None = None) -> str`:
      default `now` to `datetime.now(tz=timezone.utc)`, compute delta, format as
      "in X days, Y hours, Z minutes" or "X days, Y hours, Z minutes ago"
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ]* 5.2 Write property test for countdown direction (Property 5)
    - **Property 5: Countdown direction reflects past vs. future**
    - **Validates: Requirements 2.2, 2.3**
    - File: `tests/property/test_countdown.py`
    - Strategy: pairs of UTC-aware datetimes; assert "ago" iff `dt < now`

  - [ ]* 5.3 Write unit tests for formatter
    - File: `tests/unit/test_formatter.py`
    - Cover: ISO 8601 output format (regex check for `+HH:MM` offset), future label ("in …"),
      past label ("… ago"), with fixed injectable `now`
    - _Requirements: 2.1, 2.2, 2.3_

- [ ] 6. Implement `tzdeadline.__main__` (CLI)
  - [ ] 6.1 Create `tzdeadline/__main__.py`
    - Set up `argparse` with positional args: `datetime`, `source_tz`, `target_tz`
    - Call `parse_datetime` → `convert` → `format_iso` + `format_countdown`, print to stdout
    - Catch `ParseError` and `ConversionError`: print message to stderr, `sys.exit(1)`
    - Catch unexpected exceptions: print generic message to stderr, `sys.exit(1)`
    - Expose a `main()` function as the package entry point
    - _Requirements: 1.1, 1.3, 2.1, 2.2, 2.3, 3.2_

  - [ ]* 6.2 Write unit tests for CLI
    - File: `tests/unit/test_cli.py`
    - Cover: exit 0 on valid input (stdout contains ISO string and countdown), exit 1 on
      bad datetime, exit 1 on bad timezone
    - _Requirements: 1.3, 2.1, 3.2_

- [ ] 7. Implement `tzdeadline.server` (MCP)
  - [ ] 7.1 Create `tzdeadline/server.py`
    - Import and configure the MCP Python SDK (`mcp` package)
    - Register `@mcp.tool() convert_time(datetime_str, source_tz, target_tz) -> dict`
    - On success return `{"converted_datetime": ..., "countdown": ...}`
    - Catch `ParseError` / `ConversionError` and return `{"error": message}`
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ]* 7.2 Write property test for MCP handler structured error (Property 7)
    - **Property 7: MCP handler returns structured error for invalid inputs**
    - **Validates: Requirements 4.3**
    - File: `tests/property/test_error_conditions.py`
    - Strategy: combined invalid-input strategies from Properties 3 & 4; assert returned dict
      has `"error"` key and no unhandled exception

  - [ ]* 7.3 Write unit tests for MCP handler
    - File: `tests/unit/test_mcp_handler.py`
    - Cover: valid input returns `converted_datetime` and `countdown` keys, invalid timezone
      returns `{"error": ...}`, unparseable datetime returns `{"error": ...}`
    - _Requirements: 4.1, 4.2, 4.3_

- [ ] 8. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

---

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP.
- Each task references specific requirements for traceability.
- Property tests use [Hypothesis](https://hypothesis.readthedocs.io/) with
  `@settings(max_examples=100)` and are annotated `# Feature: tzdeadline, Property N: <title>`.
- Unit tests use pytest and focus on concrete examples, boundary conditions, and error paths.
- The `now` parameter in `format_countdown` is injectable so all countdown tests are deterministic.
- All timezone arithmetic uses `zoneinfo` only — no `pytz`, `dateutil`, or network I/O.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2.1", "3.1", "5.1"] },
    { "id": 2, "tasks": ["2.2", "2.3", "2.4", "3.2", "3.3", "3.4", "3.5", "5.2", "5.3"] },
    { "id": 3, "tasks": ["6.1"] },
    { "id": 4, "tasks": ["6.2", "7.1"] },
    { "id": 5, "tasks": ["7.2", "7.3"] }
  ]
}
```
